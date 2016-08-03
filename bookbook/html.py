"""Converts a collection of notebooks to HTML files."""
import argparse
import logging
from pathlib import Path
import re

from nbconvert.exporters import HTMLExporter
from nbconvert.writers import FilesWriter
from nbconvert.filters.markdown_mistune import MarkdownWithMath, IPythonRenderer

class MyMarkdownRenderer(IPythonRenderer):
    def link(self, link, title, text):
        m = re.match(r'(\d+\-.+)\.ipynb(#.+)?$', link)
        if m:
            link = m.expand(r'\1.html\2')
        return super().link(link, title, text)

def markdown2html_custom(source):
    """Convert a markdown string to HTML using mistune"""
    return MarkdownWithMath(renderer=MyMarkdownRenderer(escape=False)).render(source)

class MyHTMLExporter(HTMLExporter):
    def default_filters(self):
        yield from super().default_filters()
        yield ('markdown2html', markdown2html_custom)

def convert(source_path: Path, output_dir: Path):
    exporter = MyHTMLExporter()
    writer = FilesWriter(build_directory=str(output_dir))
    output, resources = exporter.from_filename(str(source_path))
    notebook_name = source_path.stem
    writer.write(output, resources, notebook_name=notebook_name)

def convert_directory(source_dir: Path, output_dir: Path):
    for nbfile in source_dir.glob('*-*.ipynb'):
        convert(nbfile, output_dir)

def main(argv=None):
    ap = argparse.ArgumentParser(description='Convert a set of notebooks to HTML')
    ap.add_argument('source_dir', nargs='?', type=Path, default='.',
                    help='Directory containing the .ipynb files')
    ap.add_argument('--output-dir', type=Path, default='html',
                    help='Directory where output files will be written')
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO)
    convert_directory(args.source_dir, args.output_dir)

if __name__ == '__main__':
    main()
