import bibtexparser
import numpy as np
import pandas as pd
from pdb import set_trace

BIB = '../cv/mypapers.bib'
HTML = 'papers.html'

def bib_html(row, file=None):
    if row.booktitle != -1:
        venue = row.booktitle
    elif row.journal != -1:
        venue = row.journal
    else:
        raise ValueError(row.ID, 'Could not extract venue.')
    str = f'''
<li><p>
    {row.title}<br>
    {row.author}<br>
    {venue}, 2021.<br>
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


with open(BIB, 'r') as f:
    bib = bibtexparser.load(f)

df = pd.DataFrame(bib.entries)
set_trace()
df = df.sort_values('year', ascending=False)
df = df.fillna(-1)

with open(HTML, 'w') as f:
    df.apply(bib_html, axis=1, file=f)

