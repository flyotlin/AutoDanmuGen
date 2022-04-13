import os
from AutoDanmuGen.common_vars import CommonVars

class Extractor(object):
    """Extract frames and comments from raw `.mp4` and `.ass` files."""
    frames_outdir = os.path.join(CommonVars.tmp_dir, 'frames')
    comments_outfile = os.path.join(CommonVars.tmp_dir, 'comment.txt')

    def __init__(self, filepath, video_id=0) -> None:
        """Initialize Extractor

        Args:
            filepath (str): filepath to `.mp4` and `.ass` files, *but without extension*.
            video_id (int, optional): _description_. Defaults to 0.
        """
        self.filepath = filepath
        self.video_id = video_id

    def frames(self):
        """Extract frames from `.mp4` file and save them inside `tmp/frames`"""
        if not os.path.exists(self.frames_outdir):	# check if output folder for frame exists
            os.mkdir(self.frames_outdir)

        cmd_str = 'ffmpeg -i "%s" -r 1/1 -s 224x224 -f image2 %s/' % (self.filepath+'.mp4', self.frames_outdir) + '%d.bmp'	# 用ffmpeg extract video中的frame
        print(cmd_str)
        os.system(cmd_str)	# execute the command in a subshell

    def comments(self):
        """Extract comments from `.ass` file and save it in `tmp/comment.txt`"""
        with open(self.comments_outfile, 'w', encoding='utf8') as fw:	# open comment output file
            for line in open(self.filepath+'.ass', 'r', encoding='utf8').readlines():	# open .ass file
                if line.startswith('Dialogue:'):
                    comment = line[line.rfind('}')+1:].strip()	# 找到最右邊 } 的index
                    time = line[line.find(',')+1:line.find('.')]	# time在第一個,至第一個.中間
                    time = sum(x * int(t) for x, t in zip([3600, 60, 1], time.split(":")))	# 計算總秒數
                    fw.write("%d\t%d\t%s\n" % (self.video_id, time, comment))
