import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Definimos los productos que queremos buscar con sus URLs o IDs
PRODUCTOS_CONFIG = [
    {
        "id_interno": "aceite_oliva_1l",
        "nombre": "Aceite de Oliva Virgen Extra 1L",
        "urls": {
            "mercadona": "11234", # ID interno de su API
            "carrefour": "https://www.carrefour.es/supermercado/aceite-de-oliva-extra-1-l/R-VC4G-1234/p",
            "lidl": "https://www.lidl.es/es/aceite-de-oliva-virgen-extra/p1234",
            "aldi": "https://www.aldi.es/productos/aceite-oliva-virgen-extra.html"
        }
    }
]

def extraer_precio(tienda, identificador):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        if tienda == "mercadona":
            # API Directa
            res = requests.get(f"https://tienda.mercadona.es/api/products/{identificador}/", headers=headers)
            return res.json()['price_instructions']['unit_price']
        
        else:
            # Scraping Web
            res = requests.get(identificador, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            if tienda == "carrefour":
                return float(soup.find("span", {"class": "buy-box__price"}).text.replace('€','').replace(',','.').strip())
            if tienda == "lidl":
                return float(soup.find("meta", {"property": "product:price:amount"})["content"])
            if tienda == "aldi":
                return float(soup.find("span", {"class": "price__wrapper"}).text.replace('€','').replace(',','.').strip())
    except Exception as e:
        print(f"Error en {tienda}: {e}")
        return None

def main():
    resultados = {
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "productos": []
    }

    for p in PRODUCTOS_CONFIG:
        item = {
            "nombre": p["nombre"],
            "precios": {}
        }
        for tienda, url_o_id in p["urls"].items():
            item["precios"][tienda] = extraer_precio(tienda, url_o_id)
        
        resultados["productos"].append(item)

    with open('precios.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()