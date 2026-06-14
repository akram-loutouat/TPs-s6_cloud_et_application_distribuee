import urllib.request
import urllib.error
import json
import time
import random
import uuid

def send_document_defensive(title, content, visibility):
    url = "http://localhost:8080/documents"
    token = "ENSA-FES-2026-SECRET-KEY"
    request_id = str(uuid.uuid4()) # ID unique pour traçabilité (Observabilité)

    payload = {
        "title": title,
        "content": content,
        "visibility": visibility
    }
    data = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Request-ID", request_id)

    # Paramètres de fiabilité
    base_delay = 1.0
    max_delay = 10.0
    max_retries = 3

    for attempt in range(max_retries + 1):
        try:
            print(f"[Client] Tentative {attempt} / Request-ID: {request_id}")
            # Connexion timeout (3s) et Read timeout (5s) strictes
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = response.read().decode('utf-8')
                print(f"[Client] Succès (Code {response.status}): {res_data}")
                return json.loads(res_data)

        except urllib.error.HTTPError as e:
            # Séparation stricte : erreurs transitoires (Retries autorisés) vs permanentes (Interdits)
            if e.code in [500, 502, 503, 504]:
                print(f"[Erreur Transitoire] Code {e.code}. Préparation du retry...")
            else:
                # Erreurs 400, 401, 403, 404 : Abandon immédiat (Évite les boucles futiles)
                print(f"[Erreur Critique Permanente] Code {e.code}: {e.read().decode('utf-8')}. Abandon.")
                return None
        except urllib.error.URLError as e:
            print(f"[Erreur Réseau/Timeout] Raison : {e.reason}. Préparation du retry...")
        
        # Application de l'algorithme de Backoff Exponentiel et Jitter si non-dernier essai
        if attempt < max_retries:
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0.5, 1.5)
            final_delay = delay * jitter
            print(f"[Fiabilité] Attente de {final_delay:.2f} secondes avant nouvel essai...")
            time.sleep(final_delay)
        else:
            print("[Échec Définitif] Nombre maximal de retries atteint. Alerte système levée.")
            return None

if __name__ == '__main__':
    # Test nominal
    print("--- Test Nominal (Données valides) ---")
    send_document_defensive("Rapport de Sécurité", "Données chiffrées de l'ENSA", "private")
    
    # Test d'une erreur permanente (Ne doit pas engendrer de retries)
    print("\n--- Test Erreur Permanente (Schéma invalide) ---")
    send_document_defensive("Titre invalide", "Contenu", "PUBLIC_INVALIDE")