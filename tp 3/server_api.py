import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configuration de la journalisation interne (Observabilité)
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "request_id": "%(message)s"}'
)

TOKEN_SECRET = "ENSA-FES-2026-SECRET-KEY"

class SecureAPIHandler(BaseHTTPRequestHandler):
    def _log_with_id(self, message, request_id="-"):
        # Formatage structuré du log incluant le X-Request-ID
        logging.info(f"{request_id} - {message}")

    def do_POST(self):
        # 1. Extraction et validation des en-têtes
        request_id = self.headers.get("X-Request-ID", "UNKNOWN")
        auth_header = self.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            self._log_with_id("Échec Auth: En-tête Authorization manquant ou malformé", request_id)
            self.send_error_response(401, "Unauthorized: Missing Bearer Token")
            return
            
        token = auth_header.split(" ")[1]
        if token != TOKEN_SECRET:
            self._log_with_id("Échec Auth: Token invalide fourni", request_id)
            self.send_error_response(401, "Unauthorized: Invalid Token")
            return

        # 2. Gestion de l'endpoint unique /documents
        if self.path != "/documents":
            self.send_error_response(404, "Not Found")
            return

        # 3. Lecture sécurisée du corps de la requête
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response(400, "Bad Request: Empty Body")
                return
                
            raw_data = self.rfile.read(content_length)
            data = json.loads(raw_data.decode('utf-8'))
        except (json.JSONDecodeError, ValueError) as e:
            self._log_with_id(f"Erreur décodage JSON: {str(e)}", request_id)
            self.send_error_response(400, "Bad Request: Malformed JSON")
            return

        # 4. Validation stricte du schéma (Rejet de l'inconnu et vérification des types)
        required_fields = {"title", "content", "visibility"}
        if not required_fields.issubset(data.keys()) or len(data) > len(required_fields):
            self._log_with_id("Validation échouée: Champs manquants ou injection de champs inconnus", request_id)
            self.send_error_response(400, "Bad Request: Invalid contract schema")
            return

        if not isinstance(data["title"], str) or not (1 <= len(data["title"]) <= 200):
            self.send_error_response(400, "Bad Request: 'title' must be a string between 1 and 200 chars")
            return

        if not isinstance(data["content"], str):
            self.send_error_response(400, "Bad Request: 'content' must be a string")
            return

        if data["visibility"] not in ["public", "private"]:
            self.send_error_response(400, "Bad Request: 'visibility' must be 'public' or 'private'")
            return

        # 5. Traitement métier réussi (Simulation de persistance)
        self._log_with_id(f"Document crée avec succès: {data['title']}", request_id)
        
        response_body = json.dumps({"status": "success", "message": "Document created"}).encode('utf-8')
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Request-ID", request_id)
        self.end_headers()
        self.wfile.write(response_body)

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

def run(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SecureAPIHandler)
    print(f"Server running secure API on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()