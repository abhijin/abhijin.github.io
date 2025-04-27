import bibtexparser
import click
import numpy as np
import pandas as pd
from pdb import set_trace
from re import sub
from scholarly import scholarly
import sqlite3

DB = '../data/data.db'
INBIB = '../data/scholar.bib'
OUTBIB = '../data/mypapers.bib'
HTML = 'papers.html.part'

VENUE_MAP = {
        'Proceedings of the AAAI Conference on Artificial Intelligence': 'AAAI',
        'Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops': 'CVPR Workshops',
        }

@click.group()
def cli():
    pass

@cli.command()
def scholar2db():
    # load latest scholar (does not have to full file)
    with open(INBIB, 'r') as f:
        bib = bibtexparser.load(f)
        df = pd.DataFrame(bib.entries)

    # load db that contains old conversions
    conn = sqlite3.connect(DB)
    old_df = pd.read_sql_query("SELECT * FROM bib", conn)

    ## first time
    ## df.to_sql('bib', conn, if_exists='replace', index=False)

    # compare db with new data and remove duplicates in the new data
    diff = df.merge(old_df[df.columns], how='left', indicator=True).query(
            '_merge == "left_only"').drop(columns=['_merge'])

    if not diff.shape[0]:
        print('No new document to be added to database.')
        return
    else:
        print('The following new entries will be added ...', diff.title.values)

    # concat with db
    diff['title_new'] = diff.title
    diff['journal_new'] = diff.journal
    diff['booktitle_new'] = diff.booktitle
    diff.to_sql('bib', conn, if_exists="append", index=False)
    return

@cli.command()
def db2html():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM bib WHERE ignore=0", conn)
    df = df.sort_values('year', ascending=False)
    with open(HTML, 'w') as f:
        f.write('''
<h6 id="papers">Research papers</h6>
      <div style="max-width:75ch">
          <ul class="ul-research-papers">
''')
        df.apply(row2html, axis=1, file=f)
        f.write('</ul>\n</div>')

def row2html(row, file=None):
    if not row.booktitle is None:
        venue = shorten_venue(row.booktitle_new)
    elif not row.journal is None:
        venue = shorten_venue(row.journal_new)
    else:
        print(row.ID, 'Could not extract venue.')
        return
    
    title = sub('\n', ' ', row.title_new)
    author = sub('\n', ' ', authors(row.author))
    venue = sub('\n', ' ', venue)

    str = f'''
    <li><p>
        {title}.
        {author}.
        {venue}, {row.year}.<br>
    '''

    ## if row.url != -1:
    ##     url = row.url
    ##     str += f'''
    ##     <a href="{url}" class="btn btn-outline-dark btn-xs">PDF</a>

    str += '''
    </p></li>
'''
    file.write(str)
    return

def shorten_venue(venue):
    for k,v in VENUE_MAP.items():
        if k in venue:
            return v
    return venue

def authors(auths):
    new_auth_list = []
    for auth in auths.split(' and '):
        name_disagg = auth.split(', ')
        try:
            new_auth_list.append(name_disagg[1] + r'&nbsp' + name_disagg[0])
        except IndexError:
            if name_disagg[0] == 'others':
                new_auth_list.append(name_disagg[0])
    try:
        return ', '.join(new_auth_list[0:-1]) + ' and ' + new_auth_list[-1]
    except:
        set_trace()

@cli.command()
def db2bib():
    pass

if __name__ == '__main__':
    cli()
