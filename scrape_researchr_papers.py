import requests
from bs4 import BeautifulSoup

urls = ['https://conf.researchr.org/track/fse-2025/fse-2025-research-papers']

titles = []
for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    conference = url.split('/')[-1].split('-')[0].upper()
    year = url.split('/')[-1].split('-')[1]

    section = soup.find(id='event-overview')
    if section:
        h3 = section.find('h3')
        if h3 and h3.get_text() == 'Accepted Papers':
            tds = section.find_all('td')
            
            for td in tds:
                if td.find('a'):
                    title = td.find('a').get_text()
                else:
                    continue
                performers = td.find('div', class_='performers')
                
                performer = [a.get_text() for a in performers.find_all('a')] if performers else []
                
                title = f'{title}, {", ".join(performer)}'
                
                spans = [a.get_text() for a in td.find_all('a', class_='publication-link')]
                
                if len(spans) > 0:
                    title = f'{title}\n{" ".join(spans)}'
                    
                titles.append({
                    'Conference': conference,
                    'Year': year,
                    'Title': title})

import pandas as pd
df = pd.DataFrame(titles)
df.to_csv('researchr_papers.csv', index=False)