from pathlib import Path
from voc_watch.db import DB
import datetime
import requests

class Watcher:
    def __init__(self, db: Path = None):
        self.db = DB(db)
        self.pool = {}

    def register(self, url: str):
        def decorator(func):
            self.pool[url] = func
            return func
        return decorator
    
    def fetch(self, url: str):
        res = requests.get(url)
        if res.status_code != 200:
            raise ValueError(f"{url} returned {res.status_code}")
        return res

    def run(self):
        """Run the watcher."""
        for url, func in self.pool.items():
            name = func.__name__
            print(f"Running {name}...")
            collapse_file = f"collapse_files/{name}.txt"
            print(f"Fetching {url}...")
            res = self.fetch(url)
            vocs_in_db = self.db.get(url)
            list_of_vocs: list = func(res)
            if list_of_vocs is None:
                raise ValueError(f"Function '{name}' did not return a list of vocs.")
            if vocs_in_db == list_of_vocs:
                print(f"VOC list from {url} has not changed.")
                print("Skipping...")
                continue
            print(f"Found {len(list_of_vocs)} lineages.")
            print(", ".join(list_of_vocs))
            print(f"Updating {collapse_file}...")
            self.db.put(url, list_of_vocs)
            with open(collapse_file, "w") as f:
                date = datetime.datetime.now().strftime("%d/%m/%Y")
                list_of_vocs = [f"# This file was automatically generated from {url} on the {date}", *list_of_vocs]
                # list_of_vocs.extend(["# Capture all other lineages", "A", "B", "Recombinant"])
                for lineage in list_of_vocs:
                    if not lineage:
                        continue
                    f.write(f"{lineage}\n")

            
