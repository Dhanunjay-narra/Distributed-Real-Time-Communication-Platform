import os, sys, http.server, socketserver

PORT = 3000
DIRECTORY = "apps/web"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[ONLINE] Chatbot Web Frontend running at: http://localhost:{PORT}")
        print(f"[READY] 1-Click Demo Login is active with pre-filled test credentials.")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    start_server()
