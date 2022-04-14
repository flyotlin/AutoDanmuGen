import os
import shutil
import sys
import unittest
from PIL import Image

try:
    sys.path.append('../../AutoDanmuGen')
except Exception as err:
    print(err)
from AutoDanmuGen.core import Preparer, Extractor


class TestExtractor(unittest.TestCase):
    filepath = '../AutoDanmuGen/tests/static/【動畫瘋】進擊的巨人 The Final Season[23][540P]'
    comment_path = '../AutoDanmuGen/tmp/comment.txt'
    frames_path = '../AutoDanmuGen/tmp/frames'

    @classmethod
    def setUpClass(cls) -> None:
        Preparer.prepare()

    def setUp(self) -> None:
        pass

    def test_extract_a_video(self):
        extractor = Extractor(self.filepath, 0)
        extractor.frames()
        extractor.comments()

        self.assertTrue(os.path.isfile(self.comment_path))
        self.assertTrue(os.path.exists(self.frames_path))

    def test_comment_format(self):
        extractor = Extractor(self.filepath, 0)
        extractor.comments()

        with open(self.comment_path, 'r', encoding='utf8') as f:
            lines = f.read().strip().split('\n')
            for line in lines:
                cols = line.strip().split('\t')
                self.assertEqual(len(cols), 3)
                self.assertTrue(cols[0].isnumeric())
                self.assertTrue(cols[1].isnumeric())

    def test_video_frame_format(self):
        extractor = Extractor(self.filepath, 0)
        extractor.frames()

        for dirpath, _, filenames in os.walk(self.frames_path):
            for file in filenames:
                with Image.open(os.path.join(dirpath, file)) as image:
                    width, height = image.size
                    self.assertEqual(width, 224)
                    self.assertEqual(height, 224)

    def tearDown(self) -> None:
        if os.path.isfile(self.comment_path):
            os.remove(self.comment_path)
        if os.path.exists(self.frames_path):
            shutil.rmtree(self.frames_path)
