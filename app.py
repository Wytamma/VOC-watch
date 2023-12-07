from typing import List
from voc_watch import Watcher, Response
from bs4 import BeautifulSoup
import re 

voc_watcher = Watcher('voc_watch.db')

def extract_first_pango_lineage(text: str) -> str:
    pattern = re.compile(r'[A-Z]{1,3}(?:\.\d+(?:\.\d+)*)?')
    match = pattern.search(text)
    if match:
        return match.group(0)
    raise ValueError(f"Could not extract pango lineage from {text}")
    
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
            pango_lineage = extract_first_pango_lineage(pango_lineage)
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
        pango_lineage = extract_first_pango_lineage(pango_lineage)
        list_of_vocs.append(pango_lineage)
    return list_of_vocs

@voc_watcher.register(url="https://www.cdc.gov/coronavirus/2019-ncov/variants/variant-classifications.html")
def cdc(res: Response) -> List[str]:
    soup = BeautifulSoup(res.text, 'html.parser')
    # find all divs with attribute row="row"
    # Find all divs that represent columns
    columns = soup.find_all('div', class_='col-md-3')

    # List to store Pango Lineages
    pango_lineages = []

    for column in columns:
        # Check if the column header is 'Pango Lineage'
        if 'Pango Lineage' in column.text:
            # Find the next div with role='cell' which contains the Pango Lineage
            next_cell = column.find_next('div', {'role': 'cell'})
            if next_cell:
                pango_lineages.append(next_cell.get_text(strip=True))
    pango_lineages = [extract_first_pango_lineage(lineage) for lineage in pango_lineages]
    return [lineage for lineage in pango_lineages if len(lineage) > 1]
        
def combine_results(results: List[List[str]]) -> List[str]:
    combined_results = sorted(
        list(set([item for sublist in results for item in sublist]))
    )
    collapse_file = "collapse_files/combined.txt"
    with open(collapse_file, "w") as f:
        combined_results.extend(["# Capture all other lineages", "A", "B", "Recombinant"])
        for lineage in combined_results:
            if not lineage:
                continue
            f.write(f"{lineage}\n")


if __name__ == "__main__":
    voc_watcher.run()
    results = [voc_watcher.db.get(key) for key in voc_watcher.db]
    combine_results(results)