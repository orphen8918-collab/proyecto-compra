import requests
import json
from datetime import datetime
import time

# ==========================================
# CONFIGURACIÓN DE PRODUCTOS
# ==========================================
# Aquí añadirás tus productos. He puesto IDs y URLs reales.
PRODUCTOS_CONFIG = [
    {
        "nombre": "Arroz Redondo 1kg",
        "mercadona_id": "2142",
        "carrefour_url": "https://www.carrefour.es/supermercado/arroz-redondo-carrefour-1-kg/R-521004525/p"
    },
    {
        "nombre": "Leche Entera 1L",
        "mercadona_id": "11012",
        "carrefour_url": "https://www.carrefour.es/supermercado/leche-entera-carrefour-1-l/R-521021495/p"
    }
]

# ==========================================
# FUNCIONES DE AYUDA (ANTI-ERRORES)
# ==========================================

def obtener_precio_mercadona(product_id):
    """Llama a la API interna de Mercadona"""
    url = f"https://tienda.mercadona.es/api/products/{product_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Buscamos el precio en la estructura del JSON de Mercadona
            return data.get('price_instructions', {}).get('unit_price')
    except Exception as e:
        print(f"  [!] Error Mercadona ID {product_id}: {e}")
    return None

def ejecutar_subida_datos():
    print(f"--- Iniciando actualización: {datetime.now()} ---")
    
    resultados = {
        "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "productos": []
    }

    for item in PRODUCTOS_CONFIG:
        nombre = item["nombre"]
        print(f"Procesando: {nombre}...")
        
        precios_encontrados = {}

        # 1. Intentar Mercadona
        precio_m = obtener_precio_mercadona(item["mercadona_id"])
        if precio_m:
            precios_encontrados["mercadona"] = precio_m
            print(f"  -> Mercadona: {precio_m} €")
        
        # 2. Aquí podrías añadir más funciones para Carrefour/Lidl/etc.
        # Por ahora guardamos lo que tenemos
        
        resultados["productos"].append({
            "nombre": nombre,
            "precios": precios_encontrados,
            "enlaces": {
                "carrefour": item.get("carrefour_url")
            }
        })
        
        # Pequeña pausa para no saturar los servidores y evitar baneos
        time.sleep(1)

    # ==========================================
    # GUARDADO FINAL
    # ==========================================
    try:
        with open('base_de_datos_precio.json', 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=4, ensure_ascii=False)
        print("--- Proceso finalizado con éxito: archivo JSON guardado ---")
    except Exception as e:
        print(f"Error al escribir el archivo JSON: {e}")

if __name__ == "__main__":
    ejecutar_subida_datos()
