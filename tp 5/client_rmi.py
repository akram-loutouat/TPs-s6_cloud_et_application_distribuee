import Pyro5.api

# Alignement obligatoire de la configuration du sérialiseur binaire côté client
Pyro5.config.SERIALIZER = "serpent"

def run_client():
    name_server_key = "ensa.cybersoc.documentservice"
    token_valide = "RMI-AUTH-TOKEN-2026"

    try:
        print("[Client] Recherche du service auprès du registre de noms...")
        ns = Pyro5.api.locate_ns()
        uri = ns.lookup(name_server_key)
        print(f"[Client] Service localisé à l'adresse URI : {uri}")
    except Exception as e:
        print(f"[Client - Erreur Registre] Impossible d'obtenir l'URI de l'objet distant. {str(e)}")
        return

    # Instanciation du Proxy transparent (Représentant local de l'objet distant)
    with Pyro5.api.Proxy(uri) as proxy:
        print("\n--- 1. Appel nominal de listing ---")
        try:
            docs = proxy.list_documents()
            print(f"[Client] Liste des documents disponibles : {docs}")
        except Exception as e:
            print(f"Erreur lors du listing : {e}")

        print("\n--- 2. Lecture nominale d'un document avec token valide ---")
        try:
            content = proxy.get_document_content("doc1", token_valide)
            print(f"[Client] Contenu récupéré avec succès : {content}")
        except Exception as e:
            print(f"Erreur : {e}")

        print("\n--- 3. Tentative d'accès avec un jeton corrompu (Sécurité) ---")
        try:
            proxy.get_document_content("doc1", "MAUVAIS-TOKEN")
        except Exception as e:
            print(f"[Client - Blocage Intercepté] L'objet distant a levé l'exception : {e}")

        print("\n--- 4. Tentative d'attaque par injection de chemin / Path traversal ---")
        try:
            # Tentative d'injection de caractères interdits par la regex du serveur
            proxy.get_document_content("../../etc/passwd", token_valide)
        except Exception as e:
            print(f"[Client - Blocage Intercepté] L'objet distant a levé l'exception : {e}")

        print("\n--- 5. Tentative d'invocation d'une méthode non exposée (Sécurité Framework) ---")
        try:
            # administration_interne existe dans la classe mais n'est pas décorée
            proxy.administration_interne()
        except AttributeError as ae:
            print(f"[Client - Succès] Méthode protégée inaccessible au niveau du proxy ! Détail : {str(ae)}")

if __name__ == '__main__':
    run_client()