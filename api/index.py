from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Configuración basada en tu script funcional
        minerales = [
            {"id": "plata", "nombre": "Plata", "url": "https://es.investing.com/commodities/silver"},
            {"id": "carbon", "nombre": "Carbon", "url": "https://es.investing.com/commodities/coal-cme-futures"},
            {"id": "hierro", "nombre": "Hierro", "url": "https://es.investing.com/commodities/iron-ore-62-cfr-futures"}
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/"
        }

        resultados = {}

        for m in minerales:
            try:
                res = requests.get(m["url"], headers=headers, timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    # Usamos el selector data-test="instrument-price-last" que ya probaste
                    elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                    
                    if elemento:
                        # Limpieza de texto (quitar espacios, cambiar coma por punto)
                        texto_sucio = elemento.text.strip()
                        precio_limpio = re.sub(r'[^0-9.]', '', texto_sucio.replace(',', '.'))
                        resultados[m["id"]] = precio_limpio
                    else:
                        resultados[m["id"]] = "0.00"
                else:
                    resultados[m["id"]] = "0.00"
            except:
                resultados[m["id"]] = "0.00"

        # Respuesta de la API
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # El JSON mandará algo como: {"plata": "31.20", "carbon": "140.50", "hierro": "105.10"}
        self.wfile.write(json.dumps(resultados).encode())
        return