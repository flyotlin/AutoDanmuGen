import numpy as np
import random
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

from AutoDanmuGen.config import Config
from AutoDanmuGen.core.util import Util


class Candidate(object):
    def __init__(self) -> None:
        self.train_comments = []
        datas = Util.load_from_json(Config.train_json)
        for i in datas:
            self.train_comments.append(i['comment'])

        self.train_comment_set = Counter(self.train_comments)
        self.train_comment_set = sorted(
            self.train_comment_set.items(),
            key=lambda kv: -kv[1]
        )
        self.train_comment_set = list(zip(*self.train_comment_set))[0]

        self.tfidf_vec = TfidfVectorizer()
        self.tfidf_vec = self.tfidf_vec.fit(self.train_comment_set)
        self.tfidf_comments = self.tfidf_vec.transform(self.train_comment_set)

    def get(self):
        context_datas = Util.load_from_json(Config.comment_context_json)
        candidate_datas = []

        for data in context_datas:
            candidates = {}
            candidates = self.update_correct_set(candidates, data)
            candidates = self.update_popular_set(candidates, Config.candidate_kth_popular)
            candidates = self.update_plausible_set(candidates, data, Config.candidate_kth_plausible)
            candidates = self.update_random_set(candidates, Config.candidate_kth_random)

            data['candidate'] = candidates
            candidate_datas.append(data.copy())

        Util.dump_to_json(candidate_datas, Config.comment_candidate_json)

    def update_correct_set(self, candidates, context_data):
        for comment in context_data['comment']:
            if comment not in candidates:
                candidates[comment] = 1
        return candidates

    def update_popular_set(self, candidates, kth):
        for comment in self.train_comment_set[:kth]:
            if comment not in candidates:
                candidates[comment] = 2
        return candidates

    def update_plausible_set(self, candidates, context_data, kth):
        query_tfidf = self.tfidf_vec.transform([context_data['context']])
        matrix = (query_tfidf * self.tfidf_comments.transpose()).todense()
        ids = np.array(np.argsort(-matrix, axis=1))[0]
        for _id in ids[:kth]:
            if self.train_comment_set[_id] not in candidates:
                candidates[self.train_comment_set[_id]] = 3
        return candidates

    def update_random_set(self, candidates, kth):
        while len(candidates) < kth:
            rand = random.randint(0, len(self.train_comment_set) - 1)
            if self.train_comment_set[rand] not in candidates:
                candidates[self.train_comment_set[rand]] = 3
            return candidates
