import jieba
from typing import List

from AutoDanmuGen.config import Config
from AutoDanmuGen.core.util import Util


class Preprocessor(object):
    """Preprocess the prediction data"""

    def __init__(self) -> None:
        pass

    def txt_to_json(self):
        """Convert `comment.txt` to `comment.json`

        Comment json object has id, time, comment.

        `id`: the id for comments.
        `time`: the timestamp for comments in sec(s).
        `comment`: the text content of the comments.
        """
        json_datas = []
        data = {
            'id': '',
            'time': '',
            'comment': ''
        }

        with open(Config.comment_txt, 'r', encoding='utf8') as comment_txt:
            lines = comment_txt.read().strip().split('\n')
            for line in lines:
                cols = line.split('\t')
                data['id'] = int(cols[0])
                data['time'] = int(cols[1])
                data['comment'] = self.tokenize_comment(cols[2])
                json_datas.append(data.copy())

        Util.dump_to_json(json_datas, Config.comment_json)

    def add_context_in_json(self, comment_ids: List[int]):
        """Add context comments (surrounding 8 comments, 4 each) to the comment json object, and create `comment-context.json`

        Making comment_ids a list can benefit from handling multiple prediction later.
        """
        datas = Util.load_from_json(Config.comment_json)
        datas_with_context = []
        data = {
            'id': '',
            'time': '',
            'comment': '',
            'context': ''
        }
        dicts = {}  # key is time, all comments at that time is the value inside key
        surrounding_comments = [-1, 1, -2, 2, -3, 3]

        for i in datas:
            key = i['time']
            if key not in dicts:
                dicts[key] = []
            dicts[key].append([i['id'], i['comment']])

        for i in comment_ids:
            time = datas[i]['time']
            context = ''
            for t in surrounding_comments:
                if time + t not in dicts:
                    continue
                # maybe 0 could be replaced to random number in the future
                surround_comment = dicts[time + t][0][1]
                if not context:
                    context = surround_comment
                else:
                    context += f' <&&&> {surround_comment}'
            data['id'] = i
            data['time'] = time
            data['comment'] = [x['comment'] for x in datas[i - 2: i + 3]]
            data['context'] = context
            datas_with_context.append(data.copy())

        Util.dump_to_json(datas_with_context, Config.comment_context_json)

    def tokenize_comment(self, comment: str):
        """Tokenize comments using jieba"""

        ret = list(jieba.cut(comment.replace(' ', '')))
        ret = " ".join(ret)
        return ret
