import os

from AutoDanmuGen.config import Config


class Preparer(object):
    def __init__(self):
        pass

    @staticmethod
    def prepare():
        if not os.path.exists(Config.tmp_dir):
            os.mkdir(Config.tmp_dir)
