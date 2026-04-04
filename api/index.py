from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Configuramos solo Plata y Cobre de Yahoo Finance
        minerales = [
            {"id": "plata", "url": "https://finance.yahoo.com/quote/SI=F/"},
            {"id": "cobre", "url": "https://finance.yahoo.com/quote/HG=F/"}
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

        resultados = {}

        for m in minerales:
            try:
                res = requests.get(m["url"], headers=headers, timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    # El selector que confirmamos que tiene el número limpio
                    elemento = soup.find("span", {"data-testid": "qsp-price"})
                    
                    if elemento:
                        # Quitamos comas y dejamos solo el número decimal
                        precio = re.sub(r'[^0-9.]', '', elemento.text.strip().replace(',', ''))
                        resultados[m["id"]] = precio
                    else:
                        resultados[m["id"]] = "0.00"
                else:
                    resultados[m["id"]] = "0.00"
            except:
                resultados[m["id"]] = "0.00"

        # Respuesta en formato JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(resultados).encode())
        return