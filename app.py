from typing import List
from voc_watch import Watcher, Response
from bs4 import BeautifulSoup

voc_watcher = Watcher('voc_watch.db')

@voc_watcher.register(url="https://www.who.int/activities/tracking-SARS-CoV-2-variants")
def who(res: Response) -> List[str]:
    soup = BeautifulSoup(res.text, 'html.parser')
    tables = soup.find_all('table')
    list_of_vocs = []
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            pango_lineage: str = cols[0].get_text(strip=True)
            pango_lineage = pango_lineage.rstrip('*').rstrip("#")
            list_of_vocs.append(pango_lineage)
    return list_of_vocs

@voc_watcher.register(url="https://www.gov.uk/government/publications/sars-cov-2-genome-sequence-prevalence-and-growth-rate")
def ukhsa(res: Response) -> List[str]:
    soup = BeautifulSoup(res.text, 'html.parser')
    section = soup.find(id='documents')
    # Find the first link in that section
    link = section.find('a')
    # Get the href attribute from the link
    link_url = link.get('href')
    res = voc_watcher.fetch(f"https://www.gov.uk/{link_url}")
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')
    list_of_vocs = []
    for row in rows[1:]:
        cols = row.find_all('td')
        pango_lineage: str = cols[0].get_text(strip=True)
        pango_lineage = pango_lineage.rstrip('*').rstrip("#")
        pango_lineage, *_ = pango_lineage.split()
        list_of_vocs.append(pango_lineage)
    return list_of_vocs


if __name__ == "__main__":
    voc_watcher.run()