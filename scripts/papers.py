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
HTML = 'papers.html.part'

VENUE_MAP = {
        'Proceedings of the AAAI Conference on Artificial Intelligence': 'AAAI',
        'Association for the Advancement of Artificial Intelligence Conference': 'AAAI',
        'Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops': 'CVPR Workshops',
        'Winter Simulation Conference': 'WSC',
        'ACM SIGKDD Conference on Knowledge Discovery and Data Mining': 'KDD',
        'International Conference on Complex Networks and Their Applications': 'Complex Networks',
        'International Conference on Autonomous Agents and Multiagent Systems': 'AAMAS',
        'International Conference on Machine Learning': 'ICML',
        'International Conference on Big Data': 'IEEE Big Data',
        'International Conference on Information and Knowledge Management': 'CIKM',
        'International Conference on Computer Communications': 'INFOCOM',
        'International Conference on Data Mining': 'ICDM',
        'PKDD': 'PKDD',
        'ICASSP': 'ICASSP',
        }

# Map LaTeX accents to characters
LATEX_TO_CHAR = {
    r"{\\'e}": "é",
    r"{\\'a}": "á",
    r"{\\'i}": "í",
    r"{\\'o}": "ó",
    r"{\\'u}": "ú",
    r"{\\`e}": "è",
    r"{\\`a}": "à",
    r"{\\`i}": "ì",
    r"{\\`o}": "ò",
    r"{\\`u}": "ù",
    r"{\\~n}": "ñ",
    r"{\\^o}": "ô",
    r"{\\aa}": "å",
    # add more if needed
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
    diff['title_web'] = diff.title
    diff['title_new'] = diff.title
    diff['journal_web'] = diff.journal
    diff['booktitle_web'] = diff.booktitle
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
        venue = shorten_venue(row.booktitle_web)
    elif not row.journal is None:
        venue = shorten_venue(row.journal_web)
    else:
        print(row.ID, 'Could not extract venue.')
        return
    
    title = sub('\n', ' ', row.title_web)
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
    auths = convert_latex_accents(auths)

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

def convert_latex_accents(text):
    for latex, char in LATEX_TO_CHAR.items():
        text = sub(latex, char, text)
    return text

@cli.command()
def db2bib():
    pass

if __name__ == '__main__':
    cli()
