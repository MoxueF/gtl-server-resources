"""Build the current server resource pack."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name('build_release4.py')), run_name='__main__')
