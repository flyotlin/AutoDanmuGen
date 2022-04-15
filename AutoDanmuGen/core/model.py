import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable

from AutoDanmuGen.config import Config

BOS = 1


class Model(nn.Module):
    def __init__(self, n_emb, n_hidden, vocab_size, dropout, d_ff, n_head, n_block):
        super(Model, self).__init__()
        self.n_emb = n_emb
        self.n_hidden = n_hidden
        self.vocab_size = vocab_size
        self.dropout = dropout
        self.embedding = nn.Sequential(Embeddings(n_hidden, vocab_size).cpu(), PositionalEncoding(n_hidden, dropout).cpu()).cpu()
        self.video_encoder = VideoEncoder(n_hidden, d_ff, n_head, dropout, n_block).cpu()
        self.text_encoder = TextEncoder(n_hidden, d_ff, n_head, dropout, n_block).cpu()
        self.comment_decoder = CommentDecoder(n_hidden, d_ff, n_head, dropout, n_block).cpu()
        self.output_layer = nn.Linear(self.n_hidden, self.vocab_size).cpu()
        self.criterion = nn.CrossEntropyLoss(reduce=False, size_average=False, ignore_index=0).cpu()

    def encode_img(self, X):
        out = self.video_encoder(X)
        return out

    def encode_text(self, X, m):
        embs = self.embedding(X)
        out = self.text_encoder(embs, m)
        return out

    def decode(self, x, m1, m2, mask):
        embs = self.embedding(x)
        out = self.comment_decoder(embs, m1, m2, mask)
        out = self.output_layer(out)
        return out

    def forward(self, X, Y, T):
        out_img = self.encode_img(X)
        out_text = self.encode_text(T, out_img)
        mask = Variable(subsequent_mask(Y.size(0), Y.size(1) - 1), requires_grad=False)
        outs = self.decode(Y[:, :-1], out_img, out_text, mask)

        Y = Y.t()
        outs = outs.transpose(0, 1)

        loss = self.criterion(outs.contiguous().view(-1, self.vocab_size), Y[1:].contiguous().view(-1))

        return torch.mean(loss)

    def generate(self, X, T):
        out_img = self.encode_img(X)
        out_text = self.encode_text(T, out_img)

        ys = torch.ones(X.size(0), 1).long()
        with torch.no_grad():
            for i in range(Config.dataset_max_len):
                out = self.decode(
                    ys, out_img, out_text, Variable(subsequent_mask(ys.size(0), ys.size(1))))
                prob = out[:, -1]
                _, next_word = torch.max(prob, dim=-1, keepdim=True)
                next_word = next_word.data
                ys = torch.cat([ys, next_word], dim=-1)

        return ys[:, 1:]

    def ranking(self, X, Y, T):
        nums = len(Y)
        out_img = self.encode_img(X.unsqueeze(0))
        out_text = self.encode_text(T.unsqueeze(0), out_img)
        out_img = out_img.repeat(nums, 1, 1)
        out_text = out_text.repeat(nums, 1, 1)

        mask = Variable(subsequent_mask(Y.size(0), Y.size(1) - 1), requires_grad=False)
        outs = self.decode(Y[:, :-1], out_img, out_text, mask)

        Y = Y.t()
        outs = outs.transpose(0, 1)

        loss = self.criterion(outs.contiguous().view(-1, self.vocab_size), Y[1:].contiguous().view(-1))

        loss = loss.view(-1, nums).sum(0)
        return torch.sort(loss, dim=0, descending=True)[1]


class luong_attention(nn.Module):
    def __init__(self, hidden_size):
        super(luong_attention, self).__init__()
        self.hidden_size = hidden_size
        self.linear_in = nn.Linear(hidden_size, hidden_size)
        self.linear_out = nn.Sequential(nn.Linear(2 * hidden_size, hidden_size), nn.Tanh())
        self.softmax = nn.Softmax(dim=-1)

    def init_context(self, context):
        self.context = context  # batch * seq1 * size

    def forward(self, h):  # batch * seq2 * size
        gamma_h = self.linear_in(h)  # batch * seq2 * size
        weights = torch.bmm(gamma_h, self.context.transpose(1, 2))  # batch * seq2 * seq1
        weights = self.softmax(weights)  # batch * seq2 * seq1
        c_t = torch.bmm(weights, self.context)  # batch * seq2 * size
        output = self.linear_out(torch.cat([c_t, h], -1))  # batch * seq2 * size

        return output


class Generator(nn.Module):
    "Define standard linear + softmax generation step."
    def __init__(self, d_model, vocab):
        super(Generator, self).__init__()
        self.proj = nn.Linear(d_model, vocab)

    def forward(self, x):
        return self.proj(x)


class VideoEncoder(nn.Module):
    def __init__(self, d_model, d_ff, n_head, dropout, n_block):
        super(VideoEncoder, self).__init__()
        self.layers = nn.ModuleList([VideoBlock(d_model, d_ff, n_head, dropout) for _ in range(n_block)])
        self.norm = LayerNorm(d_model)

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return self.norm(x)


class TextEncoder(nn.Module):

    def __init__(self, d_model, d_ff, n_head, dropout, n_block):
        super(TextEncoder, self).__init__()
        self.layers = nn.ModuleList([TextBlock(d_model, d_ff, n_head, dropout) for _ in range(n_block)])
        self.norm = LayerNorm(d_model)

    def forward(self, x, m):
        for layer in self.layers:
            x = layer(x, m)
        return self.norm(x)


class CommentDecoder(nn.Module):
    def __init__(self, d_model, d_ff, n_head, dropout, n_block):
        super(CommentDecoder, self).__init__()
        self.layers = nn.ModuleList([DecoderBlock(d_model, d_ff, n_head, dropout) for _ in range(n_block)])
        self.norm = LayerNorm(d_model)

    def forward(self, x, m1, m2, mask):
        for layer in self.layers:
            x = layer(x, m1, m2, mask)
        return self.norm(x)


class VideoBlock(nn.Module):
    def __init__(self, d_model, d_ff, n_head, dropout):
        super(VideoBlock, self).__init__()
        self.self_attn = MultiHeadedAttention(n_head, d_model)
        self.feed_forward = PositionwiseFeedForward(d_model, d_ff, dropout)
        self.sublayer = nn.ModuleList([SublayerConnection(d_model, dropout) for _ in range(2)])

    def forward(self, x):
        x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x))
        return self.sublayer[1](x, self.feed_forward)


class TextBlock(nn.Module):
    def __init__(self, d_model, d_ff, n_head, dropout):
        super(TextBlock, self).__init__()
        self.self_attn = MultiHeadedAttention(n_head, d_model)
        self.video_attn = MultiHeadedAttention(n_head, d_model)
        self.feed_forward = PositionwiseFeedForward(d_model, d_ff, dropout)
        self.sublayer = nn.ModuleList([SublayerConnection(d_model, dropout) for _ in range(3)])

    def forward(self, x, m):
        x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x))
        x = self.sublayer[1](x, lambda x: self.video_attn(x, m, m))
        return self.sublayer[2](x, self.feed_forward)


class DecoderBlock(nn.Module):
    def __init__(self, d_model, d_ff, n_head, dropout):
        super(DecoderBlock, self).__init__()
        self.self_attn = MultiHeadedAttention(n_head, d_model)
        self.video_attn = MultiHeadedAttention(n_head, d_model)
        self.text_attn = MultiHeadedAttention(n_head, d_model)
        self.feed_forward = PositionwiseFeedForward(d_model, d_ff, dropout)
        self.sublayer = nn.ModuleList([SublayerConnection(d_model, dropout) for _ in range(4)])

    def forward(self, x, m1, m2, mask):
        x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x, mask))
        x = self.sublayer[1](x, lambda x: self.video_attn(x, m1, m1))
        x = self.sublayer[2](x, lambda x: self.text_attn(x, m2, m2))
        return self.sublayer[3](x, self.feed_forward)


class LayerNorm(nn.Module):
    def __init__(self, features, eps=1e-6):
        super(LayerNorm, self).__init__()
        self.a_2 = nn.Parameter(torch.ones(features))
        self.b_2 = nn.Parameter(torch.zeros(features))
        self.eps = eps

    def forward(self, x):
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True)
        return self.a_2 * (x - mean) / (std + self.eps) + self.b_2


class SublayerConnection(nn.Module):
    """
    A residual connection followed by a layer norm.
    Note for code simplicity the norm is first as opposed to last.
    """
    def __init__(self, size, dropout):
        super(SublayerConnection, self).__init__()
        self.norm = LayerNorm(size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, sublayer):
        return x + self.dropout(sublayer(self.norm(x)))


class MultiHeadedAttention(nn.Module):
    def __init__(self, h, d_model, dropout=0.1):
        "Take in model size and number of heads."
        super(MultiHeadedAttention, self).__init__()
        assert d_model % h == 0
        # We assume d_v always equals d_k
        self.d_k = d_model // h
        self.h = h
        self.linears = nn.ModuleList([nn.Linear(d_model, d_model) for _ in range(4)])
        self.attn = None
        self.dropout = nn.Dropout(p=dropout)

    def attention(self, query, key, value, mask=None, dropout=None):
        "Compute 'Scaled Dot Product Attention'"
        d_k = query.size(-1)
        scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        p_attn = F.softmax(scores, dim=-1)
        if dropout is not None:
            p_attn = dropout(p_attn)
        return torch.matmul(p_attn, value), p_attn

    def forward(self, query, key, value, mask=None):
        if mask is not None:
            # Same mask applied to all h heads.
            mask = mask.unsqueeze(1)
        nbatches = query.size(0)

        # 1) Do all the linear projections in batch from d_model => h x d_k
        query, key, value = [
            l(x).view(nbatches, -1, self.h, self.d_k).transpose(1, 2) for l, x in zip(self.linears, (query, key, value))]  # noqa

        # 2) Apply attention on all the projected vectors in batch.
        x, self.attn = self.attention(query, key, value, mask=mask, dropout=self.dropout)

        # 3) "Concat" using a view and apply a final linear.
        x = x.transpose(1, 2).contiguous() \
            .view(nbatches, -1, self.h * self.d_k)
        return self.linears[-1](x)


class Embeddings(nn.Module):
    def __init__(self, d_model, vocab):
        super(Embeddings, self).__init__()
        self.lut = nn.Embedding(vocab, d_model)
        self.d_model = d_model

    def forward(self, x):
        return self.lut(x)


class PositionalEncoding(nn.Module):
    "Implement the PE function."

    def __init__(self, d_model, dropout, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Compute the positional encodings once in log space.
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0., max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0., d_model, 2) * -(math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + Variable(self.pe[:, :x.size(1)], requires_grad=False)
        return self.dropout(x)


class PositionalEmb(nn.Module):
    "Implement the PE function."

    def __init__(self, d_model, dropout, max_len=5000):
        super(PositionalEmb, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Compute the positional encodings once in log space.
        self.pe = torch.nn.Embedding(max_len, d_model)

    def forward(self, x):
        x = x + self.pe(Variable(torch.range(1, x.size(1))).long()).unsqueeze(0)
        return self.dropout(x)


class PositionwiseFeedForward(nn.Module):
    "Implements FFN equation."
    def __init__(self, d_model, d_ff, dropout=0.1):
        super(PositionwiseFeedForward, self).__init__()
        self.w_1 = nn.Linear(d_model, d_ff)
        self.w_2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.w_2(self.dropout(F.relu(self.w_1(x))))


def subsequent_mask(batch, size):
    "Mask out subsequent positions."
    attn_shape = (batch, size, size)
    subsequent_mask = np.triu(np.ones(attn_shape), k=1).astype('uint8')
    return torch.from_numpy(subsequent_mask) == 0
