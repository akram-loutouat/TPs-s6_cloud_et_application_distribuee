import pickle
import hmac
import hashlib
import document_pb2  # Fichier généré via compilateur protoc
from defusedxml.ElementTree import fromstring, ParseError

# --- PARTIE 1 : Protobuf (Sérialisation Binaire Sûre basée sur un Schéma) ---
def protobuf_demo():
    print("=== [1] SÉRIALISATION AVEC PROTOBUF (SÛRE) ===")
    doc = document_pb2.Document()
    doc.title = "Architecture Secrète"
    doc.content = "Contenu protégé par protocole binaire."
    doc.visibility = "private"

    # Sérialisation en chaîne d'octets binaire
    serialized_bytes = doc.SerializeToString()
    print(f"Données Protobuf sérialisées (binaire) : {serialized_bytes}\n")

    # Désérialisation stricte guidée par le type compilé
    new_doc = document_pb2.Document()
    new_doc.ParseFromString(serialized_bytes)
    print(f"Données restaurées : {new_doc.title} | {new_doc.visibility}\n")


# --- PARTIE 2 : XML et Sécurisation contre les attaques XXE ---
def xml_secure_demo():
    print("=== [2] XML ET COMPORTEMENT FACE AUX ATTAQUES XXE ===")
    # Payload malveillant tentant une attaque XXE (XML External Entity)
    malicious_xml = """<?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE test [
        <!ENTITY xxe SYSTEM "file:///etc/passwd">
    ]>
    <document>
        <title>Attaque XXE</title>
        <content>&xxe;</content>
        <visibility>public</visibility>
    </document>"""

    print("Tentative de parsing avec la bibliothèque sécurisée 'defusedxml'...")
    try:
        # defusedxml lève une exception s'il détecte des entités externes ou des déclarations DTD
        root = fromstring(malicious_xml)
    except ParseError as e:
        print(f"🎯 Succès : L'attaque XXE a été bloquée net par defusedxml ! Raison : {str(e)}\n")


# --- PARTIE 3 : Atténuation des Risques de Pickle (Signature Cryptographique) ---
# Pickle permet d'exécuter du code arbitraire à la désérialisation. Si on ne peut pas s'en passer,
# il faut impérativement signer les payloads avec une clé secrète partagée (HMAC).
SECRET_SIGNING_KEY = b"Clé-Super-Secrète-De-L-ENSA"

def serialize_and_sign_pickle(obj):
    raw_pickle = pickle.dumps(obj)
    # Calcul d'une empreinte cryptographique HMAC-SHA256
    signature = hmac.new(SECRET_SIGNING_KEY, raw_pickle, hashlib.sha256).digest()
    return signature + raw_pickle # Transmission conjointe de la signature et des octets

def deserialize_and_verify_pickle(signed_payload):
    # La signature fait 32 octets (SHA256 digest size)
    expected_signature = signed_payload[:32]
    raw_pickle = signed_payload[32:]
    
    # Calcul de contrôle
    actual_signature = hmac.new(SECRET_SIGNING_KEY, raw_pickle, hashlib.sha256).digest()
    
    # Vérification en temps constant pour éviter les attaques temporelles (side-channel)
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise SecurityError("🚨 ALERTE SÉCURITÉ : La signature du payload Pickle est invalide ! Données altérées.")
    
    return pickle.loads(raw_pickle)

class SecurityError(Exception): pass

if __name__ == '__main__':
    protobuf_demo()
    xml_secure_demo()
    
    print("=== [3] SÉCURISATION DE PICKLE VIA HMAC ===")
    data_to_send = {"user": "admin", "role": "root"}
    secured_stream = serialize_and_sign_pickle(data_to_send)
    
    print("Désérialisation d'un flux valide...")
    print("Résultat :", deserialize_and_verify_pickle(secured_stream))
    
    print("\nTentative d'attaque par falsification de données...")
    corrupted_stream = secured_stream[:-1] + b'\x00' # Altération malveillante du dernier octet
    try:
        deserialize_and_verify_pickle(corrupted_stream)
    except SecurityError as se:
        print(se)