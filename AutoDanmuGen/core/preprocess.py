import jieba
import json

from AutoDanmuGen.config import Config


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
            'video': '',
            'time': '',
            'comment': ''
        }

        with open(Config.comments_outfile, 'r', encoding='utf8') as comment_txt:
            lines = comment_txt.read().strip().split('\n')
            for line in lines:
                cols = line.split('\t')
                data['id'] = int(cols[0])
                data['time'] = int(cols[1])
                data['comment'] = self.tokenize_comment(cols[2])
                json_datas.append(data.copy())

        self.dump_to_json(json_datas, Config.comments_json)

    def add_context_in_json(self):
        """Add context comments (surrounding 8 comments, 4 each) to the comment json object, and create `comment-context.json`"""
        pass

    def tokenize_comment(self, comment: str):
        """Tokenize comments using jieba"""

        ret = list(jieba.cut(comment.replace(' ', '')))
        ret = " ".join(ret)
        return ret

    def dump_to_json(self, json_datas: list, json_file: str):
        """Dump the comment json object into a json file"""

        with open(json_file, 'w', encoding='utf8') as f:
            for data in json_datas:
                f.write(json.dumps(data, sort_keys=True, separators=(',', ': '), ensure_ascii=False))
                f.write('\n')
