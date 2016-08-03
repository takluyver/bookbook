"""Convert a collection of notebooks to a single PDF, via Latex.

- Combines notebooks into one document
- Inserts Latex labels for each document
- Converts links between notebooks to Latex \\ref{}
- Runs pdflatex to make a PDF (actually, nbconvert does this)

Requirements:
- nbconvert pandocfilters  (pip installable)
- pandoc
- pdflatex
"""
import argparse
import logging
import os
from pathlib import Path
from typing import Sequence

import nbformat
from nbformat import NotebookNode
from nbformat.v4 import new_notebook, new_markdown_cell
from nbconvert.exporters import PDFExporter, LatexExporter
from nbconvert.writers import FilesWriter
from nbconvert.utils.pandoc import pandoc

log = logging.getLogger(__name__)

def new_latex_cell(source=''):
    return NotebookNode(
        cell_type='raw',
        metadata=NotebookNode(raw_mimetype='text/latex'),
        source=source,
    )


def combine_notebooks(notebook_files: Sequence[Path]) -> NotebookNode:
    combined_nb = new_notebook()

    count = 0
    for filename in notebook_files:
        count += 1
        log.debug('Adding notebook: %s', filename)
        nbname = filename.stem
        nb = nbformat.read(str(filename), as_version=4)

        assert nb.cells[0].cell_type == 'markdown', nb.cells[0].cell_type
        c0_lines = nb.cells[0].source.splitlines()
        if c0_lines[0].startswith('# '):
            header_lines = 1
        elif len(c0_lines) > 1 and c0_lines[1].startswith('==='):
            header_lines = 2
        else:
            raise Exception("Failed to find header in " + filename)

        header = '\n'.join(c0_lines[:header_lines])
        intro_remainder = '\n'.join(c0_lines[header_lines:]).strip()
        combined_nb.cells.append(new_markdown_cell(header))
        combined_nb.cells.append(new_latex_cell('\label{sec:%s}' % nbname))
        if intro_remainder:
            combined_nb.cells.append(new_markdown_cell(intro_remainder))

        combined_nb.cells.extend(nb.cells[1:])

        if not combined_nb.metadata:
            combined_nb.metadata = nb.metadata.copy()

    log.info('Combined %d files' % count)
    return combined_nb

mydir = os.path.dirname(os.path.abspath(__file__))
filter_links = os.path.join(mydir, 'filter_links.py')

def pandoc_convert_links(source):
    return pandoc(source, 'markdown', 'latex', extra_args=['--filter', filter_links])

class MyLatexExporter(LatexExporter):
    def default_filters(self):
        yield from super().default_filters()
        yield ('markdown2latex', pandoc_convert_links)

class MyLatexPDFExporter(PDFExporter):
    def default_filters(self):
        yield from super().default_filters()
        yield ('markdown2latex', pandoc_convert_links)

def export(combined_nb: NotebookNode, output_file: Path, pdf=False):
    resources = {}
    resources['unique_key'] = 'combined'
    resources['output_files_dir'] = 'combined_files'

    log.info('Converting to %s', 'pdf' if pdf else 'latex')
    exporter = MyLatexPDFExporter() if pdf else MyLatexExporter()
    writer = FilesWriter(build_directory=str(output_file.parent))
    output, resources = exporter.from_notebook_node(combined_nb, resources)
    writer.write(output, resources, notebook_name=output_file.stem)

def combine_and_convert(source_dir: Path, output_file: Path, pdf=False):
    notebook_files = sorted(source_dir.glob('*-*.ipynb'))
    combined_nb = combine_notebooks(notebook_files)
    export(combined_nb, output_file, pdf=pdf)

def main(argv=None):
    ap = argparse.ArgumentParser(description='Convert a set of notebooks to PDF via Latex')
    ap.add_argument('source_dir', nargs='?', type=Path, default='.',
                    help='Directory containing the .ipynb files')
    ap.add_argument('--output-file', type=Path, default='combined',
                    help='Directory where output files will be written')
    ap.add_argument('--pdf', action='store_true',
                    help='Run Latex to convert to PDF.')
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO)
    combine_and_convert(args.source_dir, args.output_file, args.pdf)

if __name__ == '__main__':
    main()
