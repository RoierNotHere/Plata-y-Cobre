from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        url = "https://tradingeconomics.com/commodities"
        
        try:
            res = scraper.get(url, timeout=20)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Mapeo de símbolos en Trading Economics
                # Plata: XAGUSD:CUR | Cobre: HG1:COM
                minerales_target = {
                    'XAGUSD:CUR': 'Plata',
                    'HG1:COM': 'Cobre'
                }
                
                resultados = {}
                
                for symbol, nombre in minerales_target.items():
                    fila = soup.find('tr', {'data-symbol': symbol})
                    if fila:
                        precio_raw = fila.find('td', id='p')
                        resultados[nombre] = precio_raw.text.strip() if precio_raw else "N/A"
                    else:
                        resultados[nombre] = "No encontrado"
                
                payload = {
                    "datos": resultados,
                    "status": "success"
                }
                status_code = 200
            else:
                payload = {"error": f"Error de conexión: {res.status_code}"}
                status_code = res.status_code
                
        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        # Respuesta para Vercel
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return
