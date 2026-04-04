from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Diccionario con los minerales que te funcionaron
        minerales_urls = {
            "plata": "https://es.investing.com/commodities/silver",
            "carbon": "https://es.investing.com/commodities/coal-cme-futures",
            "hierro": "https://es.investing.com/commodities/iron-ore-62-cfr-futures"
        }

        # 2. Leer qué mineral se solicita (ej: /api?m=hierro)
        url_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(url_path.query)
        # Si no se especifica mineral, usamos 'plata' por defecto
        target = params.get('m', ['plata'])[0].lower() 

        # 3. Configuración de cabeceras (Extraídas de tu script funcional)
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
                    # Usamos el selector que confirmaste que funciona
                    elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                    
                    if elemento:
                        # Limpiamos el texto para que PHP reciba solo números
                        texto_sucio = elemento.text.strip()
                        precio_final = re.sub(r'[^0-9.]', '', texto_sucio.replace(',', '.'))
                        status_msg = "success"
                    else:
                        status_msg = "Selector no encontrado en la página"
                else:
                    status_msg = f"Error de red: {res.status_code}"
            except Exception as e:
                status_msg = str(e)
        else:
            status_msg = "Mineral no disponible (usa: plata, carbon o hierro)"

        # 4. Respuesta JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "mineral": target.capitalize(),
            "precio": precio_final,
            "status": status_msg
        }
        self.wfile.write(json.dumps(response).encode())
        return