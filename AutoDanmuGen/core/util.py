import json


class Util(object):
    """Providing some common utility functions for AutoDanmuGen core"""

    @staticmethod
    def load_from_json(json_file: str) -> list:
        """Load comment json object from a json file

        The loaded from file might be named `comment.json`

        Args:
            json_file (str): the loaded from filename

        Returns:
            list: list containing all comment json object
        """
        with open(json_file, 'r', encoding='utf8') as f:
            json_datas = []
            for line in f:
                data = json.loads(line)
                json_datas.append(data)
            return json_datas

    @staticmethod
    def dump_to_json(json_datas: list, json_file: str):
        """Dump the comment json object into a json file

        The dumped to file might be named `comment.json`

        Args:
            json_datas (list): list contains all comment json object
            json_file (str): the file to dump `json_datas` to
        """

        with open(json_file, 'w', encoding='utf8') as f:
            for data in json_datas:
                f.write(json.dumps(data, sort_keys=True, separators=(',', ': '), ensure_ascii=False))
                f.write('\n')
