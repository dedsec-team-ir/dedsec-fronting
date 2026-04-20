import http.server
import socketserver
import socket
import select
import urllib.parse
import http.client
import sys


def print_banner():
    banner = r"""
░▒▓███████▓▒░░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓███████▓▒░▒▓████████▓▒░▒▓██████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░     ░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓██████▓▒░░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓███████▓▒░░▒▓████████▓▒░▒▓███████▓▒░░▒▓███████▓▒░░▒▓████████▓▒░▒▓██████▓▒░  
                                                                               
                                                                                                                
"""
    print(banner)

class DomainFrontingProxy(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_http_request()

    def do_POST(self):
        self.proxy_http_request()

    def do_PUT(self):
        self.proxy_http_request()

    def do_DELETE(self):
        self.proxy_http_request()

    def do_HEAD(self):
        self.proxy_http_request()

    def do_OPTIONS(self):
        self.proxy_http_request()

    def proxy_http_request(self):
        print(f"HTTP {self.command} request received for: {self.path}")
        try:

            parsed = urllib.parse.urlparse(self.path)
            target_host = parsed.netloc
            path = parsed.path
            if parsed.query:
                path += '?' + parsed.query
            if not path:
                path = '/'

            print(f"Proxying HTTP request to {target_host} via google.com")


            conn = http.client.HTTPSConnection('google.com', timeout=10)
            headers = dict(self.headers)
            headers['Host'] = target_host
            headers['Connection'] = 'close'


            content_length = self.headers.get('Content-Length')
            body = None
            if content_length:
                body = self.rfile.read(int(content_length))

            conn.request(self.command, path, body=body, headers=headers)
            response = conn.getresponse()


            self.send_response(response.status)
            for header, value in response.getheaders():
                if header.lower() not in ['connection', 'keep-alive', 'proxy-connection']:
                    self.send_header(header, value)
            self.end_headers()

            # Send response body
            self.wfile.write(response.read())
            conn.close()

        except Exception as e:
            print(f"Error proxying HTTP request: {e}")
            self.send_error(500, f"Proxy error: {str(e)}")

    def do_CONNECT(self):
        print(f"CONNECT request received for: {self.path}")
        try:

            target_host, target_port = self.path.split(':', 1)
            target_port = int(target_port)

            print(f"Tunneling HTTPS request to {target_host}:{target_port} via google.com:443")


            front_sock = socket.create_connection(('google.com', 443))


            self.send_response(200, 'Connection established')
            self.end_headers()


            connections = [self.connection, front_sock]
            try:
                while True:
                    readable, _, _ = select.select(connections, [], [], 1)
                    if not readable:
                        continue
                    for r in readable:
                        other = front_sock if r is self.connection else self.connection
                        data = r.recv(4096)
                        if not data:
                            return
                        other.sendall(data)
            except Exception as e:
                print(f"Error during forwarding: {e}")
            finally:
                front_sock.close()
                self.connection.close()

        except Exception as e:
            print(f"Error tunneling CONNECT: {e}")
            self.send_error(500, f"Tunnel error: {str(e)}")

    def log_message(self, format, *args):

        pass

def main():
    port = 8080
    try:
        with socketserver.ThreadingTCPServer(('', port), DomainFrontingProxy) as httpd:
            print_banner()
            print(f"Domain fronting proxy server running on localhost:{port}")
            print("Configure your browser to use HTTP proxy: localhost:8080")
            print("Note: HTTPS tunneling may not work due to SNI checking")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nProxy server stopped")
    except Exception as e:
        print(f"Error starting proxy: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()