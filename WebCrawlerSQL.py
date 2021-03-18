import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent import futures
import sqlite3

conn = sqlite3.connect('paper_list.db')
#ID INT PRIMARY KEY,
conn.execute('''CREATE TABLE IF NOT EXISTS PAPER_LIST
                (
                PMID INT NOT NULL UNIQUE,
                DOI VARCHAR,
                TITLE   VARCHAR,
                AUTHORS VARCHAR,
                PUBLISH_DATE    VARCHAR,
                CITED_PMID VARCHAR);
                ''')
#print('Table Created')

###################################################################
############    Process the Web ###################################
###################################################################

pmids_df = pd.read_csv('pmids_list.csv')
pmids_list = list(pmids_df['pmid'])

root = 'http://www.ncbi.nlm.nih.gov/pubmed/'
doi_prefix = 'https://doi.org/'

#pmids_list = pmids_list[:100]

def get_doi(pmid):
    response = requests.get(root+str(pmid))
    if response.status_code == 200:
        #soup = BeautifulSoup(response.text, "html.parser")
        #return [pmid,doi_prefix + soup.find_all(attrs={"name": "citation_doi"})[0]['content']]
        return [pmid, response.text]
    else:
        #return [pmid, None]
        return [pmid, None]

processes = []
sql = "INSERT INTO paper_list(pmid, doi, title, authors, publish_date, cited_pmid) " \
      "VALUES (?, ?, ?, ?, ?, ?)"

with futures.ThreadPoolExecutor(max_workers=8) as executor:
    for pmid in pmids_list:
        processes.append(executor.submit(get_doi, pmid))
for task in futures.as_completed(processes):
    pmid, html_text = task.result()
    # html_text == None means the web requests return Error
    if html_text == None:
        continue

    soup = BeautifulSoup(html_text, "html.parser")
    doi_suffix = soup.find_all(attrs={"name": "citation_doi"})[0]['content']
    # '' means there is no doi
    if(doi_suffix == ''):
        doi = None
    else:
        doi = doi_prefix + doi_suffix

    title = soup.find(attrs={'name': 'citation_title'})['content']
    authors = soup.find(attrs={'name': 'citation_authors'})['content']
    date = soup.find('meta', attrs={'name': 'citation_date'})['content']

    cited_list = soup.find_all('a', class_='docsum-title', attrs={'data-ga-category': 'cited_by'})
    cited_pmid = [cited['data-ga-action'] for cited in cited_list]

    val = (int(pmid),doi,title,authors,date,('|').join(cited_pmid))
    conn.execute(sql, val)
    conn.commit()

conn.close()
