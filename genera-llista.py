import requests
import json

URL_PROGRAMA = "https://api.ccma.cat/videos?version=2.0&_format=json&items_pagina=1500&tipus_contingut=PPD&ordre=-data_emissio&produccio=1001217"

def main():
    contes = {}
    response = requests.get(URL_PROGRAMA, allow_redirects=True)
    data = response.json()
    
    for item in data["resposta"]["items"]["item"]:
        try:
            if item["idiomes"][0]["id"] == "PU_CATALA":
                titol = item["titol"]
                id = item["id"]
                if titol and id:
                    item_url = f"https://dinamics.ccma.cat/pvideo/media.jsp?media=video&idint={id}"
                    item_response = requests.get(item_url, allow_redirects=True)
                    item_data = item_response.json()
                    contes[titol] = item_data["media"]["url"][0]["file"]
        except Exception:
            pass
    
    with open("contes.json", "w") as file:
        json.dump(contes, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()