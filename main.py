from AutoDanmuGen.core import Preparer, Extractor, Preprocessor

if __name__ == '__main__':
    filepath = '/Users/flyotlin/Documents/Program/research_project/test/video/【動畫瘋】進擊的巨人 The Final Season[23][540P]'
    video_id = 0

    Preparer.prepare()

    extractor = Extractor(filepath, video_id)
    extractor.frames()
    extractor.comments()

    preprocessor = Preprocessor()
    preprocessor.txt_to_json()
