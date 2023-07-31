from voc_watch import Watcher, Response
from bs4 import BeautifulSoup

voc_watcher = Watcher('voc_watch.db')

@voc_watcher.register(url="https://www.who.int/activities/tracking-SARS-CoV-2-variants")
def who(res: Response):
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

if __name__ == "__main__":
    voc_watcher.run()