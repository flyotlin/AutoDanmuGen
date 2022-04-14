import os


class Config(object):
    tmp_dir = 'tmp'  # folder saving tmp files for prediction
    frames_outdir = os.path.join(tmp_dir, 'frames')
    comments_outfile = os.path.join(tmp_dir, 'comment.txt')  # TODO: should be renamed to `comments_txt`
    comments_json = os.path.join(tmp_dir, 'comment.json')
