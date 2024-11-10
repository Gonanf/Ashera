from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import sys
import json
import ssl

def get_ssl_context(certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(certfile, keyfile)
    context.set_ciphers("@SECLEVEL=1:ALL")
    return context

class handler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin',"*")
        self.send_header('Access-Control-Allow-Methods',"*")
        self.send_header('Access-Control-Allow-Headers',"*")
        BaseHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type","text/html")
        debcon = sqlite3.connect("db.sqlite3")
        debcursor = debcon.cursor()
        self.end_headers()
        debcursor.execute("SELECT * FROM numeros;")
        response = debcursor.fetchall()
        response_server = {a[0]: a[1] == None for a in response}
        print(response_server)
        print(json.dumps(response_server, sort_keys=True, indent=4))
        self.wfile.write(bytes(json.dumps(response_server, sort_keys=True, indent=4),"utf-8"))

    def do_POST(self):

        size = int(self.headers.get('content-length'))
        data = self.rfile.read(size)
        json_data = json.loads(data)
        debcon = sqlite3.connect("db.sqlite3")
        debcursor = debcon.cursor()
        debcursor.execute(f"SELECT nombre FROM numeros WHERE numero = {json_data['numero']};")
        if debcursor.fetchone() != (None,):
            self.send_error(404,"Already taken number")
            self.send_header("Content-type","text/html")
            self.end_headers()
            return
        print(f"UPDATE numeros SET nombre = '{json_data['nombre']}', apellido = '{json_data['apellido']}' WHERE numero = {json_data['numero']};")
        debcursor.execute(f"UPDATE numeros SET nombre = '{json_data['nombre']}', apellido = '{json_data['apellido']}' WHERE numero = {json_data['numero']};")
        
        debcon.commit()
        debcursor.close()
        debcon.close()
        print(json_data, len(json_data))
        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    
if __name__ == "__main__":
    webserver = HTTPServer(('192.168.1.45',28129),handler)
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
        context = get_ssl_context("cert.pem","key.pem")
        webserver.socket = context.wrap_socket(webserver.socket, server_side=True)
        webserver.serve_forever()
    except KeyboardInterrupt:
        pass
    webserver.server_close()