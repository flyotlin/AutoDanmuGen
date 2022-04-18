import os


class Config(object):
    abs_path = os.path.dirname(os.path.abspath(__file__))
    abs_path = abs_path[:abs_path.rfind('/')]
    tmp_dir = 'tmp'
    resources_dir = os.path.join(abs_path, __package__, 'resources')

    # For Preparation
    # folder saving tmp files for prediction
    src_filepath = '../test/video/【動畫瘋】進擊的巨人 The Final Season[23][540P]'

    frames_outdir = os.path.join(tmp_dir, 'frames')

    comment_txt = os.path.join(tmp_dir, 'comment.txt')

    comment_json = os.path.join(tmp_dir, 'comment.json')

    comment_context_json = os.path.join(tmp_dir, 'comment-context.json')

    comment_candidate_json = os.path.join(tmp_dir, 'comment-candidate.json')

    train_json = os.path.join(resources_dir, 'train.json')

    candidate_kth_popular = 20

    candidate_kth_plausible = 20

    candidate_kth_random = 100

    # For Danmu Testing and Prediction #
    vocab_path = os.path.join(resources_dir, 'dicts-30000.json')

    res18_img_path = os.path.join(resources_dir, 'res18.pkl')

    dataset_max_len = 20    # should be renamed to test_max_len

    test_img_num = 5

    test_comment_num = 5

    test_embedding_size = 512  # embedding size
    test_hidden_size = 512  # hidden size
    test_vocab_size = 30005  # vocabulary size. it should be 30000, but somehow it's 30005 in dicts-30000.json
    test_dropout_rate = 0.1   # dropout rate
    test_hidden_feedforward_size = 2048  # hidden size of feedforward
    test_head_num = 8  # number of head
    test_block_num = 6  # number of block
    test_restored_model_path = os.path.join(resources_dir, 'checkpoint.pt')   # restoring model path
    test_use_cuda = False

    @classmethod
    def load_default_config(cls):
        pass

    @classmethod
    def reset_config(cls):
        pass
