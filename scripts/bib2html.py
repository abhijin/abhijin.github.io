import bibtexparser
import numpy as np
import pandas as pd
from pdb import set_trace
from re import sub

BIB = '../cv/mypapers.bib'
HTML = 'papers.html'

def bib_html(row, file=None):
    if row.booktitle != -1:
        venue = row.booktitle
    elif row.journal != -1:
        venue = row.journal
    else:
        print(row.ID, 'Could not extract venue.')
        return
    
    row.title = sub('\n', ' ', row.title)
    row.author = sub('\n', ' ', row.author)
    venue = sub('\n', ' ', venue)

    str = f'''
    <li><p>
        {row.title}<br>
        {row.author}<br>
        {venue}, {row.year}.<br>
    '''

    if row.url != -1:
        url = row.url
        str += f'''
        <a href="{url}" class="btn btn-outline-dark btn-xs">PDF</a>
'''

    str += '''
    </p></li>
'''
    f.write(str)
    return


with open(BIB, 'r') as f:
    bib = bibtexparser.load(f)

df = pd.DataFrame(bib.entries)
df = df.sort_values('year', ascending=False)
df = df.fillna(-1)

with open(HTML, 'w') as f:
    f.write('<ul>')
    df.apply(bib_html, axis=1, file=f)
    f.write('</ul>')

