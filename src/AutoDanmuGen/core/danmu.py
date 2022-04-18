import time
import torch

from AutoDanmuGen.config import Config
from AutoDanmuGen.core.dataset import DataSet
from AutoDanmuGen.core.model import Model


class Danmu(object):
    def __init__(self) -> None:
        self.test_set = DataSet(
            Config.comment_candidate_json,
            Config.vocab_path,
            is_train=False,
            imgs=None
        )

        self.model = Model(
            n_emb=Config.test_embedding_size,
            n_hidden=Config.test_hidden_size,
            vocab_size=Config.test_vocab_size,
            dropout=Config.test_dropout_rate,
            d_ff=Config.test_hidden_feedforward_size,
            n_head=Config.test_head_num,
            n_block=Config.test_block_num
        ).cpu()

        if Config.test_use_cuda:
            self.model_dict = torch.load(Config.test_restored_model_path)
        else:
            self.model_dict = torch.load(Config.test_restored_model_path, map_location=torch.device('cpu'))
        self.model.load_state_dict(self.model_dict)
        if Config.test_use_cuda:
            self.model.cuda()

    def test(self):
        start_time = time.time()

        self.model.eval()
        predictions, references = [], []

        with torch.no_grad():
            for i in range(len(self.test_set)):
                X, Y, T, data = self.test_set.get_img_and_candidate(i)
                if Config.test_use_cuda:
                    X = X.cuda()
                    Y = Y.cuda()
                    T = T.cuda()
                ids = self.model.ranking(X, Y, T).data

                candidate = []
                comments = list(data['candidate'].keys())
                for _id in ids:
                    candidate.append(comments[_id])
                predictions.append(candidate)
                references.append(data['candidate'])

        for i in predictions:
            predict = i[:6]
            predict = [x.replace(' ', '') for x in predict]
            print(predict)
        end_time = time.time()
        print("testing time:", end_time - start_time)

    def predict(self):
        pass
