import os

from AutoDanmuGen.config import Config


class Extractor(object):
    """Extract frames and comments from raw `.mp4` and `.ass` files."""

    frames_outdir = Config.frames_outdir
    comment_txt = Config.comment_txt

    # TODO: specify output destination
    def __init__(self, filepath, video_id=0) -> None:
        """Initialize Extractor

        Args:
            filepath (str): filepath to `.mp4` and `.ass` files, *but without extension*.
            video_id (int, optional): _description_. Defaults to 0.
        """

        self.filepath = filepath
        # self.video_id = video_id  # TODO: remove it!

    def frames(self):
        """Extract frames from `.mp4` file and save them inside `tmp/frames`"""

        if not os.path.exists(self.frames_outdir):
            os.mkdir(self.frames_outdir)

        extract_frame_cmd = f'ffmpeg -i "{self.filepath}.mp4" -r 1/1 -s 224x224 -f image2 {self.frames_outdir}/%d.bmp'
        os.system(extract_frame_cmd)

    def comments(self):
        """Extract comments from `.ass` file and save it in `tmp/comment.txt`"""

        with open(self.comment_txt, 'w', encoding='utf8') as out_file:
            with open(self.filepath + '.ass', 'r', encoding='utf8') as ass_file:
                comment_id = 0
                for line in ass_file.readlines():
                    if line.startswith('Dialogue'):
                        comment = line[line.rfind('}') + 1:].strip()
                        time = line[line.find(',') + 1:line.find('.')]
                        time = sum(x * int(t) for x, t in zip([3600, 60, 1], time.split(":")))
                        out_file.write(f'{comment_id}\t{time}\t{comment}\n')
                        comment_id += 1
