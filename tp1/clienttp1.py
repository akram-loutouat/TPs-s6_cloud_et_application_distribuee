#!/usr/bin/env python3
  """
  Mini client HTTP qui appelle le serveur de documents.
  Utilise uniquement la stdlib Python (urllib).
  Montre la gestion du timeout.
  """
  
  import json
  import time
  import urllib.request
  import urllib.error
  
  BASE_URL = "http://127.0.0.1:8000"
  TIMEOUT_SECONDS = 1.5  # ← on coupe si le serveur met plus de 1.5s
  
  
  def get_document(doc_id):
      """Récupère un document par son ID avec gestion du timeout."""
      url = f"{BASE_URL}/documents/{doc_id}"
      print(f"\n📡 Requête vers {url} (timeout={TIMEOUT_SECONDS}s)")
  
      debut = time.time()
      try:
          # urllib.request.urlopen accepte un paramètre timeout
          response = urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS)
          duree = time.time() - debut
  
          data = json.loads(response.read().decode("utf-8"))
          print(f"✅ Réponse reçue en {duree:.2f}s")
          print(f"   Données : {data}")
          return data
  
      except urllib.error.URLError as e:
          duree = time.time() - debut
          if "timed out" in str(e):
              print(f"⏰ TIMEOUT après {duree:.2f}s — le serveur est trop lent !")
          else:
              print(f"❌ Erreur réseau après {duree:.2f}s : {e}")
          return None
  
  
  if __name__ == "__main__":
      # Appeler plusieurs fois pour observer la variabilité
      for i in range(5):
          get_document("1")