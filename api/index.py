from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Intentamos con la Plata que es tu URL base
        url = "https://es.investing.com/commodities/silver"
        
        # Headers mucho más completos para evitar el 403
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        try:
            # Usamos una sesión para mantener las cookies, esto ayuda a saltar bloqueos
            session = requests.Session()
            res = session.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # El selector que confirmaste en tu scraper2.py
                elemento = soup.find(attrs={"data-test": "instrument-price-last"})
                
                if elemento:
                    texto = elemento.text.strip()
                    # Limpiamos todo excepto números y puntos
                    precio_limpio = re.sub(r'[^0-9.]', '', texto.replace(',', '.'))
                    resultado = {"precio": precio_limpio, "status": "success"}
                else:
                    resultado = {"precio": "0.00", "status": "No se encontro el selector"}
            else:
                resultado = {"precio": "0.00", "status": f"Bloqueo de Investing: {res.status_code}"}
        
        except Exception as e:
            resultado = {"precio": "0.00", "status": str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(resultado).encode())
        return