from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Configuración de URLs (basada en tu scraper2.py)
        minerales_urls = {
            "plata": "https://es.investing.com/commodities/silver",
            "carbon": "https://es.investing.com/commodities/coal-cme-futures",
            "hierro": "https://es.investing.com/commodities/iron-ore-62-cfr-futures",
            "oro": "https://es.investing.com/commodities/gold"
        }

        # 2. Leer qué mineral pide el usuario (ej: /api?m=plata)
        url_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(url_path.query)
        target = params.get('m', ['oro'])[0].lower() # Por defecto busca oro

        # 3. Lógica de Scraping (tus HEADERS y selectores)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/"
        }

        precio_final = "0.00"
        status_msg = ""

        if target in minerales_urls:
            try:
                res = requests.get(minerales_urls[target], headers=headers, timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    # Usamos tu selector: instrument-price-last
                    elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                    if elemento:
                        precio_final = elemento.text.strip()
                        status_msg = "success"
                    else:
                        status_msg = "Selector no encontrado"
                else:
                    status_msg = f"Error de red: {res.status_code}"
            except Exception as e:
                status_msg = str(e)
        else:
            status_msg = "Mineral no soportado"

        # 4. Respuesta de la API
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "mineral": target,
            "precio": precio_final,
            "status": status_msg
        }
        self.wfile.write(json.dumps(response).encode())
        return