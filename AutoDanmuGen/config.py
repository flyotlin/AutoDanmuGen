import os


class Config(object):
    # folder saving tmp files for prediction
    tmp_dir = 'tmp'

    frames_outdir = os.path.join(tmp_dir, 'frames')

    comment_txt = os.path.join(tmp_dir, 'comment.txt')

    comment_json = os.path.join(tmp_dir, 'comment.json')

    comment_context_json = os.path.join(tmp_dir, 'comment-context.json')

    comment_candidate_json = os.path.join(tmp_dir, 'comment-candidate.json')

    train_json = 'train.json'

    candidate_kth_popular = 20

    candidate_kth_plausible = 20

    candidate_kth_random = 100

    @classmethod
    def load_default_config(cls):
        pass

    @classmethod
    def reset_config(cls):
        pass
