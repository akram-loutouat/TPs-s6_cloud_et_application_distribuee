import Pyro5.api
import re
import logging

# Configuration des logs système (Interne uniquement)
logging.basicConfig(level=logging.INFO, format="[SERVEUR LOG] %(asctime)s - %(levelname)s - %(message)s")

# Politique de sérialisation globale imposée au niveau du framework : utilisation de Serpent
# Serpent est un sérialiseur sûr qui convertit en types basiques (interdiction de pickle/RCE)
Pyro5.config.SERIALIZER = "serpent"

class DocumentService(object):
    def __init__(self):
        # Simulation d'une base de données interne en mémoire
        self._db = {
            "doc1": "Rapport annuel de cybersécurité ENSA-Fès.",
            "doc2": "Spécifications techniques de la topologie réseau de l'école."
        }
        self.secret_token = "RMI-AUTH-TOKEN-2026"

    # --- MÉTHODES EXPOSÉES (LISTE BLANCHE STRICTE) ---
    @Pyro5.api.expose
    def list_documents(self):
        logging.info("Appel distant : list_documents()")
        return list(self._db.keys())

    @Pyro5.api.expose
    def get_document_content(self, doc_id, auth_token):
        logging.info(f"Appel distant : get_document_content(doc_id='{doc_id}')")
        
        # 1. Contrôle d'accès applicatif simple
        if auth_token != self.secret_token:
            logging.warning("Échec d'authentification sur l'appel d'objet distant.")
            raise PermissionError("Accès refusé : Token d'authentification invalide.")

        # 2. Validation stricte des entrées (Contre le Path Traversal et injections)
        if not isinstance(doc_id, str):
            raise ValueError("Format invalide : L'identifiant doit être une chaîne de caractères.")
            
        # Regex restreignant aux caractères alphanumériques d'une longueur max de 32 caractères
        if not re.match(r"^[a-zA-Z0-9_]{1,32}$", doc_id):
            logging.warning(f"Tentative d'injection ou ID malformé détecté : {doc_id}")
            raise ValueError("Format invalide : Caractères non autorisés détectés.")

        # 3. Gestion défensive des erreurs et messages d'erreurs génériques (Sûrs)
        try:
            # Code métier pouvant potentiellement lever des exceptions internes complexes
            content = self._db[doc_id]
            return content
        except KeyError as ke:
            # Log de l'erreur précise en interne
            logging.error(f"Erreur interne : Document {doc_id} introuvable. Détail : {str(ke)}")
            # Masquage de la stack-trace technique et retour d'un message épuré au client
            raise KeyError("Ressource introuvable : L'identifiant demandé n'existe pas.")
        except Exception as e:
            logging.critical(f"Défaut d'infrastructure non géré : {str(e)}")
            raise RuntimeError("Une erreur interne au serveur est survenue.")

    # --- MÉTHODES NON EXPOSÉES (INVISIBLE ET INACCESSIBLE DU RÉSEAU) ---
    def administration_interne(self):
        # Cette méthode n'a pas le décorateur @Pyro5.api.expose. Elle ne peut être appelée à distance.
        print("Exécution d'une tâche d'administration machine interne.")

def main():
    # Instanciation du Daemon Pyro5 chargé d'écouter les connexions entrantes
    daemon = Pyro5.api.Daemon()
    
    # Localisation automatique du Name Server préalablement lancé
    try:
        ns = Pyro5.api.locate_ns()
    except Exception:
        print("Erreur : Impossible de localiser le Name Server. Lancez 'python -m Pyro5.nameserver'")
        return

    # Enregistrement de la classe de service auprès du Daemon
    uri = daemon.register(DocumentService)
    
    # Publication du service dans l'annuaire logique du Name Server (Découplage architectural)
    ns.register("ensa.cybersoc.documentservice", uri)
    
    print(f"Serveur d'objets distants prêt. URI enregistrée sous : ensa.cybersoc.documentservice")
    daemon.requestLoop()

if __name__ == '__main__':
    main()
    