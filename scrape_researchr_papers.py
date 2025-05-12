import requests
from bs4 import BeautifulSoup
import pandas as pd

urls = [
    'https://conf.researchr.org/track/fse-2025/fse-2025-research-papers',
    'https://conf.researchr.org/track/icse-2025/icse-2025-research-track?#event-overview',
    'https://conf.researchr.org/track/cain-2025/cain-2025-call-for-papers#event-overview',
]

def parse_standard_table_based_page(soup, conference, year):
    titles = []
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
                    'Title': title
                })
    return titles

def parse_h3_based_page(soup, conference, year):
    titles = []

    anchor = soup.find('h3', string='Papers - Accepted')
    if not anchor:
        return titles

    # Collect all siblings that come after <h3>Papers - Accepted</h3>
    for elem in anchor.find_all_next():
        if elem.name == 'h3':
            title_text = elem.get_text(strip=True)
            next_elem = elem.find_next_sibling()

            # Grab authors if the next element is a <p>
            if next_elem and next_elem.name == 'p':
                authors = next_elem.get_text(strip=True)
                if authors.lower().startswith('authors:'):
                    authors = authors[len('Authors:'):].strip()
                title = f"{title_text}, {authors}"

                titles.append({
                    'Conference': conference,
                    'Year': year,
                    'Title': title
                })

    return titles

all_titles = []
for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    conference = url.split('/')[-1].split('-')[0].upper()
    year = url.split('/')[-1].split('-')[1]

    # Detect structure
    section = soup.find(id='event-overview')
    if section and section.find('h3', string='Accepted Papers'):
        all_titles.extend(parse_standard_table_based_page(soup, conference, year))
    elif soup.find('div', id='Papers-Accepted') and soup.find('div', id='Papers-Accepted').find('h3'):
        all_titles.extend(parse_h3_based_page(soup, conference, year))
    else:
        print(f"Could not parse: {url}")

# Export to CSV
df = pd.DataFrame(all_titles)
df.to_csv('researchr_papers.csv', index=False)
