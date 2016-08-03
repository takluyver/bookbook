from pathlib import Path
from tempfile import TemporaryDirectory
from testpath import assert_isfile

from bookbook import html

sample_dir = Path(__file__).parent / 'sample'

def test_sampledir():
    with TemporaryDirectory() as td:
        td = Path(td)
        html.convert_directory(sample_dir, td)

        assert_isfile(td / '01-introduction.html')
