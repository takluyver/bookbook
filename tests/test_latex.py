from pathlib import Path
from tempfile import TemporaryDirectory
from testpath import assert_isfile

from bookbook import latex

sample_dir = Path(__file__).parent / 'sample'

def test_sampledir():
    with TemporaryDirectory() as td:
        td = Path(td)
        latex.combine_and_convert(sample_dir, td / 'combined.pdf', pdf=True)

        assert_isfile(td / 'combined.pdf')
