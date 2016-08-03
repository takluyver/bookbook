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


def test_convert_link():
    sample = "[link](01-abc.ipynb)"
    res = latex.pandoc_convert_links(sample)
    assert '\\ref{sec:01-abc}' in res
    assert '.ipynb' not in res


    sample = "[link](02-def.ipynb#Foo-bar)"
    res = latex.pandoc_convert_links(sample)
    assert '\\ref{foo-bar}' in res
    assert '.ipynb' not in res

    # Links to external sites shouldn't be converted
    sample = "[link](http://example.com/01-abc.ipynb)"
    assert '01-abc.ipynb' in latex.pandoc_convert_links(sample)
