from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Usamos solo la Plata para la prueba
        url = "https://es.investing.com/commodities/silver"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/"
        }

        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # Tu selector estrella: data-test="instrument-price-last"
                elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                
                if elemento:
                    texto = elemento.text.strip()
                    # Limpiamos el número (quitamos comas de miles y dejamos el punto decimal)
                    precio_limpio = re.sub(r'[^0-9.]', '', texto.replace(',', ''))
                    resultado = {"plata": precio_limpio, "status": "success"}
                else:
                    resultado = {"plata": "0.00", "status": "Selector no encontrado"}
            else:
                resultado = {"plata": "0.00", "status": f"Error HTTP {res.status_code}"}
        except Exception as e:
            resultado = {"plata": "0.00", "status": str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(resultado).encode())
        return