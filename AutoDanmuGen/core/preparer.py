import os
from AutoDanmuGen.core.common_vars import CommonVars


class Preparer(object):
    def __init__(self):
        pass

    @staticmethod
    def prepare():
        if not os.path.exists(CommonVars.tmp_dir):
            os.mkdir(CommonVars.tmp_dir)
