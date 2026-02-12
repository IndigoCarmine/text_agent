# utils.py
"""
Utility functions for Markdown section splitting and file I/O.
"""
from typing import List, Tuple

def split_markdown_sections(lines: List[str]) -> List[Tuple[str, List[str]]]:
    """
    Splits Markdown lines into sections: (heading, [paragraphs]).
    Returns list of (heading, paragraphs) tuples.
    """
    sections = []
    current_heading = None
    current_paragraphs = []
    for line in lines:
        if line.strip().startswith('#'):
            if current_heading is not None:
                sections.append((current_heading, current_paragraphs))
            current_heading = line.rstrip('\n')
            current_paragraphs = []
        elif line.strip() == '':
            continue  # skip blank lines
        else:
            # 1 paragraph = 1 line (no grouping)
            current_paragraphs.append(line.rstrip('\n'))
    if current_heading is not None:
        sections.append((current_heading, current_paragraphs))
    return sections

def read_markdown_file(path: str) -> List[str]:
    with open(path, encoding='utf-8') as f:
        return f.readlines()

def write_markdown_file(path: str, lines: List[str]):
    with open(path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
