import json

def load_electrum_export(file_path : str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
    
