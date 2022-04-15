import os
import typer

from AutoDanmuGen.config import Config
from AutoDanmuGen.core.prepare import Preparer
from AutoDanmuGen.core.extract import Extractor
from AutoDanmuGen.core.preprocess import Preprocessor
from AutoDanmuGen.core.candicate import Candidate


__all__ = ['cli']

cli = typer.Typer(add_completion=False)


@cli.command()
def init(
    src: str = typer.Argument(default=None, help='the path to the video and comment, without extension.')
):
    """Initialize Prediction data
    """

    video_id = 0
    Config.src_filepath = src

    Preparer.prepare()

    extractor = Extractor(Config.src_filepath, video_id)
    extractor.frames()
    extractor.comments()

    preprocessor = Preprocessor()
    preprocessor.txt_to_json()
    preprocessor.add_context_in_json([22, 261, 1234, 1575])

    candidate = Candidate()
    candidate.get()


@cli.command()
def predict():
    """Do prediction by initialized prediction data
    """
    typer.echo("Predict")


@cli.command()
def list(
    file: str = typer.Option(default=None, help='Redirect the comments to a file'),
    no_output: bool = typer.Option(default=True, help='Redirect the comments to stdout or not')
):
    """List all comments with id
    """
    if not os.path.isfile(Config.comment_txt):
        typer.echo("Do AutoDanmuGen init first!")
        return

    if file:
        output_file = open(file, 'w', encoding='utf8')
        output_file.write('comment_id\ttime\tcomment\n')
    if not no_output:
        typer.echo('comment_id\ttime\tcomment')
    with open(Config.comment_txt, 'r', encoding='utf8') as f:
        lines = f.read().strip().split('\n')
        for line in lines:
            cols = line.strip().split('\t')
            if not no_output:
                typer.echo(f'{cols[0]}\t{cols[1]}\t{cols[2]}')
            if file:
                output_file.write(f'{cols[0]}\t{cols[1]}\t{cols[2]}\n')

    output_file.close()
