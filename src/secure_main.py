import ssl
import subprocess
import threading
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Paths to your certs


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # one level up from src/
CERT_FILE = os.path.join(BASE_DIR, "certs", "localhost.crt")
KEY_FILE = os.path.join(BASE_DIR, "certs", "localhost.key")




# Step 1: Start Streamlit on an internal port (e.g. 8501)
def start_streamlit():
    subprocess.run(["python", "-m", "streamlit", "run", "src/main.py", "--server.port=8501", "--server.headless=true"])



# Step 2: Wrap HTTPS around it using Python’s ssl
def start_https_proxy():
    class SecureHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            # Proxy all requests to local streamlit server
            self.send_response(301)
            self.send_header('Location', 'http://localhost:8501')
            self.end_headers()

    httpd = HTTPServer(('0.0.0.0', 8443), SecureHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print("🚀 Secure Streamlit running at https://localhost:8443")
    httpd.serve_forever()

# Run both servers
threading.Thread(target=start_streamlit, daemon=True).start()
start_https_proxy()
