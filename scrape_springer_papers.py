import requests
from bs4 import BeautifulSoup

urls = ['https://link.springer.com/journal/10664/volumes-and-issues/29-3', 'https://link.springer.com/journal/10664/volumes-and-issues/29-4', 'https://link.springer.com/journal/10664/volumes-and-issues/29-5', 'https://link.springer.com/journal/10664/volumes-and-issues/29-6', 'https://link.springer.com/journal/10664/volumes-and-issues/30-1', 'https://link.springer.com/journal/10664/volumes-and-issues/30-2', 'https://link.springer.com/journal/10664/volumes-and-issues/30-3']
titles = []

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    issue = soup.find('h2', class_='app-journal-latest-issue__heading').get_text().split(',')[1].upper().replace(' ', '')
    journal = ''.join(word[0] for word in soup.find('span', class_='app-journal-masthead__title').get_text().split())
    year = soup.find('time', class_='app-journal-latest-issue__date')['datetime'].split('-')[0]

    section = soup.find('section', {'data-ga': 'journal-articles', 'data-test': 'article-listing'})
    if section:
            tds = section.find_all('div', class_='app-card-open__main')
            
            for td in tds:
                if td.find('h3'):
                    title = td.find('h3').get_text()
                else:
                    continue
                performer_list = td.find('div', class_='app-card-open__authors')
                
                performers = [li.get_text() for li in performer_list.find_all('li')] if performer_list else []
                
                title = f'{title.replace('\n', '')}, {", ".join(performers)}'
                
                meta_block = td.find('div', class_='app-card-open__meta')
                meta_data = [md.get_text().replace('\n', '').strip() for md in meta_block.find_all('span', class_='c-meta__type')]
                
                if len(meta_data) > 0:
                    title = f'{title}\n{" ".join(meta_data)}'
                    
                titles.append({
                    'Journal': f'{journal} {issue}',
                    'Year': year,
                    'Title': title})

    import pandas as pd

import pandas as pd
df = pd.DataFrame(titles)

df.to_csv('springer_papers.csv', index=False)