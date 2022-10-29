import http.server
import socketserver
PORT = 8888
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("example.html", PORT), Handler)
httpd.serve_forever()
