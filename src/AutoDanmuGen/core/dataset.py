import json
import torch

from AutoDanmuGen.config import Config
from AutoDanmuGen.core.util import Util


class DataSet(torch.utils.data.Dataset):
    vocabs = json.load(open(Config.vocab_path, 'r', encoding='utf8'))['word2id']
    rev_vocabs = json.load(open(Config.vocab_path, 'r', encoding='utf8'))['id2word']

    def __init__(self, data_path, vocabs, is_train=True, imgs=None):
        self.datas = Util.load_from_json(data_path)
        if imgs is not None:
            self.imgs = imgs
        else:
            if Config.test_use_cuda:
                self.imgs = torch.load(open(Config.res18_img_path, 'rb'))
            else:
                self.imgs = torch.load(open(Config.res18_img_path, 'rb'), map_location=torch.device('cpu'))

        self.vocabs = vocabs
        self.vocab_size = len(self.vocabs)
        self.is_train = is_train

    def __len__(self):
        return len(self.datas)

    def __getitem__(self, index):
        data = self.datas[index]
        video_id, video_time = data['video'], data['time'] - 1

        X = self.load_imgs(video_id, video_time)
        T = self.load_comments(data['context'])

        if not self.is_train:
            comment = data['comment'][0]
        else:
            comment = data['comment']
        Y = DataSet.padding(comment, Config.dataset_max_len)

        return X, Y, T

    def get_img_and_candidate(self, index):
        data = self.datas[index]
        video_id, video_time = data['video'], data['time']

        X = self.load_imgs(video_id, video_time)
        T = self.load_comments(data['context'])

        Y = [DataSet.padding(c, Config.dataset_max_len) for c in data['candidate']]
        return X, torch.stack(Y), T, data

    def load_imgs(self, video_id, video_time):
        if Config.test_img_num == 0:
            return torch.stack([self.imgs[video_id][video_time].fill_(0.0) for _ in range(5)])

        surroundings = [0, -1, 1, -2, 2, -3, 3, -4, 4]
        X = []
        for t in surroundings:
            if video_time + t >= 0 and video_time + t < len(self.imgs[video_id]):
                X.append(self.imgs[video_id][video_time + t])
                if len(X) == Config.test_img_num:
                    break
        return torch.stack(X)

    def load_comments(self, context):
        if Config.test_comment_num == 0:
            return torch.LongTensor([1] + [0] * Config.dataset_max_len * 5 + [2])
        return DataSet.padding(context, Config.dataset_max_len * Config.test_comment_num)

    @classmethod
    def padding(cls, data, max_len):
        data = data.split()
        if len(data) > max_len - 2:
            data = data[:max_len - 2]
        Y = list(map(lambda t: cls.vocabs.get(t, 3), data))
        Y = [1] + Y + [2]
        length = len(Y)
        Y = torch.cat([torch.LongTensor(Y), torch.zeros(max_len - length).long()])
        return Y

    @classmethod
    def transform_to_words(cls, ids):
        words = []
        for id in ids:
            if id == 2:
                break
            words.append(cls.rev_vocabs[str(id.item())])
        return "".join(words)
