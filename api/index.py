from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
import re
import time

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        minerales = [
            {"id": "plata", "url": "https://es.investing.com/commodities/silver"},
            {"id": "carbon", "url": "https://es.investing.com/commodities/coal-cme-futures"},
            {"id": "hierro", "url": "https://es.investing.com/commodities/iron-ore-62-cfr-futures"}
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": "https://www.google.com/"
        }

        resultados = {}

        for m in minerales:
            try:
                # Una pequeña pausa para no saturar a Investing
                time.sleep(1) 
                res = requests.get(m["url"], headers=headers, timeout=15)
                
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    # El selector que te funcionó en el scraper local
                    elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                    
                    if elemento:
                        texto = elemento.text.strip()
                        # Limpiamos: quitamos todo excepto números y el punto decimal
                        # Si hay una coma (mil), la quitamos para que sea un número puro
                        precio = re.sub(r'[^0-9.]', '', texto.replace(',', ''))
                        resultados[m["id"]] = precio
                    else:
                        resultados[m["id"]] = "0.01" # Error de selector
                else:
                    resultados[m["id"]] = "0.02" # Error de bloqueo 403/404
            except Exception as e:
                resultados[m["id"]] = "0.00"

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(resultados).encode())
        return