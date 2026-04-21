#!/usr/bin/env python3
  """
  Illustration : appels séquentiels vs asynchrones.
  Montre l'impact de la latence en distribué.
  """
  
  import asyncio
  import time
  
  
  async def appeler_service(nom, latence):
      """Simule un appel à un service distant avec une latence donnée."""
      print(f"  📡 Appel à {nom} (latence prévue : {latence}s)...")
      await asyncio.sleep(latence)  # Simule l'attente réseau
      print(f"  ✅ {nom} a répondu !")
      return {"service": nom, "status": "ok"}
  
  
  async def appels_sequentiels():
      """Appels l'un après l'autre — les latences s'additionnent."""
      print("\n── Appels SÉQUENTIELS ──")
      debut = time.time()
  
      r1 = await appeler_service("Auth", 0.5)
      r2 = await appeler_service("Stockage", 0.8)
      r3 = await appeler_service("Recherche", 0.3)
  
      total = time.time() - debut
      print(f"  ⏱ Temps total séquentiel : {total:.2f}s")
      # Attendu : ≈ 0.5 + 0.8 + 0.3 = 1.6s
  
  
  async def appels_paralleles():
      """Appels en parallèle — temps total = max des latences."""
      print("\n── Appels PARALLÈLES (asyncio.gather) ──")
      debut = time.time()
  
      r1, r2, r3 = await asyncio.gather(
          appeler_service("Auth", 0.5),
          appeler_service("Stockage", 0.8),
          appeler_service("Recherche", 0.3),
      )
  
      total = time.time() - debut
      print(f"  ⏱ Temps total parallèle : {total:.2f}s")
      # Attendu : ≈ max(0.5, 0.8, 0.3) = 0.8s  →  2× plus rapide !
  
  
  if __name__ == "__main__":
      asyncio.run(appels_sequentiels())
      asyncio.run(appels_paralleles())