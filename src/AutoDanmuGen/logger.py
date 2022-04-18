import logging
import os
import sys

__all__ = ['logger']

logger = logging.getLogger(name='AutoDanmuGen-cli')
logger.setLevel(os.environ.get('UTENSOR_LOG_LEVEL', logging.INFO))

_fmt = logging.Formatter(fmt='[%(level) %(file) %(func) * %(lineno)] %(message)')
_handler = logging.StreamHandler(sys.stdout)
_handler.formatter = _fmt

logger.addHandler(_handler)
