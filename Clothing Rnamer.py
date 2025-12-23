import json
import os
import re

# Load catalog
with open("./runtime/catalog_items.json") as f:
    catalog = json.load(f)

# Match files (assuming sequential order)
assets_dir = "./runtime/assets/"
files = sorted([f for f in os.listdir(assets_dir) if f.endswith('.png')])

for i, filename in enumerate(files):
    if i < len(catalog["items"]):
        item = catalog["items"][i]
        new_name = f"{item['name'].replace(' ', '_').replace('*', '')}.png"
        
        old_path = os.path.join(assets_dir, filename)
        new_path = os.path.join(assets_dir, new_name)
        
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_name}")