from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import sys
import json
class handler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin',"*")
        self.send_header('Access-Control-Allow-Methods',"*")
        self.send_header('Access-Control-Allow-Headers',"*")
        BaseHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.end_headers()
        self.wfile.write(bytes("Hola","utf-8"))

    def do_POST(self):
        self.end_headers()
        size = int(self.headers.get('content-length'))
        data = self.rfile.read(size)
        json_data = json.loads(data)
        debcon = sqlite3.connect("db.sqlite3")
        debcursor = debcon.cursor()
        debcursor.execute(f"SELECT nombre FROM numeros WHERE numero = {json_data['numero']};")
        if debcursor.fetchone() != (None,):
            self.send_error(404,"Already taken number")
            return
        print(f"UPDATE numeros SET nombre = '{json_data['nombre']}', apellido = '{json_data['apellido']}' WHERE numero = {json_data['numero']};")
        debcursor.execute(f"UPDATE numeros SET nombre = '{json_data['nombre']}', apellido = '{json_data['apellido']}' WHERE numero = {json_data['numero']};")
        
        debcon.commit()
        debcursor.close()
        debcon.close()
        print(json_data, len(json_data))

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    
if __name__ == "__main__":
    webserver = HTTPServer(('0.0.0.0',8080),handler)
    debcon = sqlite3.connect("db.sqlite3")
    debcursor = debcon.cursor()
    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            debcursor.execute("CREATE TABLE numeros(numero,nombre,apellido)")
            for i in range(25):
                print(f"INSERT INTO numeros(numero) VALUES({i+1})")
                debcursor.execute(f"INSERT INTO numeros(numero) VALUES({i+1})")
                debcon.commit()
        elif sys.argv[1] == "get_winner":
            print(debcursor.execute("SELECT * FROM numeros ORDER BY RANDOM() LIMIT 1").fetchone())
    debcursor.close()
    debcon.close()
    print("Iniciao")
    try:
        webserver.serve_forever()
    except KeyboardInterrupt:
        pass
    webserver.server_close()