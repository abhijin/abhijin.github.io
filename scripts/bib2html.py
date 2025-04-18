import bibtexparser
import numpy as np
import pandas as pd
from pdb import set_trace
from re import sub
from scholarly import scholarly

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

def authors(row):
    new_auth_list = []
    for auth in row.split(' and '):
        name_disagg = auth.split(', ')
        try:
            new_auth_list.append(name_disagg[1] + ' ' + name_disagg[0])
        except IndexError:
            if name_disagg[0] == 'others':
                new_auth_list.append(name_disagg[0])
    try:
        return ', '.join(new_auth_list[0:-1]) + ' and ' + new_auth_list[-1]
    except:
        set_trace()

# Search for your author profile
search_query = scholarly.search_author("Abhijin Adiga University of Virginia")
author = next(search_query)

# Fill in details (including publications & citations)
author = scholarly.fill(author, sections=["basics", "indices", "publications"])

publist = []
for i, pub in enumerate(author["publications"], start=1):
    print(i, '/', len(author['publications']))
    filled_pub = scholarly.fill(pub)
    publist.append({
        'title': filled_pub["bib"].get("title", "No Title"),
        'year': filled_pub["bib"].get("pub_year", -1),
        'citation': filled_pub["bib"].get("citation", ""),
        'author': filled_pub["bib"].get("author", ""),
        'id': int(filled_pub.get('cites_id')[0])})
    if i >= 5:
        break

df = pd.DataFrame(publist)
set_trace()
df = df.sort_values('year', ascending=False)
df = df.fillna(-1)
df['author_'] = df.author
df.author = df.author.apply(authors)
set_trace()

with open(HTML, 'w') as f:
    f.write('<ul>')
    df.apply(bib_html, axis=1, file=f)
    f.write('</ul>')

