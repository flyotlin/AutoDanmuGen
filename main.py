from AutoDanmuGen import (
    Preparer,
    Extractor,
    Preprocessor,
    Candidate
)

if __name__ == '__main__':
    filepath = '../test/video/【動畫瘋】進擊的巨人 The Final Season[23][540P]'
    video_id = 0

    Preparer.prepare()

    extractor = Extractor(filepath, video_id)
    extractor.frames()
    extractor.comments()

    preprocessor = Preprocessor()
    preprocessor.txt_to_json()
    preprocessor.add_context_in_json([22, 261])

    candidate = Candidate()
    candidate.get()
