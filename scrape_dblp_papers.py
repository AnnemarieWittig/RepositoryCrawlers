import requests
from bs4 import BeautifulSoup
import pandas as pd

urls = ['https://dblp.org/db/journals/tosem/tosem33.html']
papers = []

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    journal = soup.find('h1').get_text().split(',')[0]
    thingie = journal.split(' ')[0]
    journal = ''.join([c for c in journal if c.isupper()])
    journal = journal.replace(thingie, '').strip()

    headers = soup.find_all('h2')

    for i, header in enumerate(headers):
        text = header.get_text(strip=True)
        if 'Number' not in text:
            continue
        
        text_parts = text.split(',')
        issue = text_parts[1].replace('Number', 'ISSUE').strip()
        year = text_parts[-1][-4:]

        # Determine the block between this <h2> and the next <h2>
        next_header = headers[i + 1] if i + 1 < len(headers) else None
        contents = []
        for sibling in header.find_all_next():
            if sibling == next_header:
                break
            contents.append(sibling)
        
        # From collected siblings, extract all <ul class='publ-list'>
        for block in contents:
            if block.name == 'ul' and 'publ-list' in block.get('class', []):
                publications = block.find_all('li', class_='entry article')
                for publication in publications:
                    authors = ', '.join(
                        [author.find('a').get_text(strip=True) 
                            for author in publication.find_all('span', itemprop='author') if author.find('a')]
                    )
                    title = publication.find('span', class_='title').get_text()
                    title = f'{title}, {authors}'
                    papers.append({
                        'Conference': f'{journal} {issue}',
                        'Year': year,
                        'Title': title
                    })

df = pd.DataFrame(papers)
df.to_csv(f'dblp_papers.csv', index=False)
print(f"Saved {len(df)} papers to {journal}_papers.csv")
