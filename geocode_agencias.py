"""
Geocodifica agências sem lat/lng usando Nominatim (OpenStreetMap) — gratuito, sem chave.
Uso: python geocode_agencias.py

Respeita o rate limit do Nominatim: 1 req/segundo.
"""

import time
import urllib.request
import urllib.parse
import json

from app import app, db, Agencia


def geocode_nominatim(logradouro, numero, municipio, uf):
    """Tenta geocodificar do mais específico ao mais genérico."""
    tentativas = []

    if logradouro and numero:
        tentativas.append(f"{logradouro}, {numero}, {municipio}, {uf}, Brasil")
    if logradouro:
        tentativas.append(f"{logradouro}, {municipio}, {uf}, Brasil")
    tentativas.append(f"{municipio}, {uf}, Brasil")

    headers = {"User-Agent": "rise-up-disec-geocoder/1.0"}

    for query in tentativas:
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
            "q": query,
            "format": "json",
            "limit": 1,
            "countrycodes": "br",
        })
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                results = json.loads(resp.read().decode())
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"]), query
        except Exception as e:
            print(f"    Erro na requisição: {e}")
        time.sleep(1)  # rate limit: 1 req/s

    return None, None, None


def main():
    with app.app_context():
        sem_coords = Agencia.query.filter(
            (Agencia.lat == None) | (Agencia.lng == None)
        ).all()

        total = len(sem_coords)
        print(f"Agências sem coordenadas: {total}\n")

        ok = 0
        falhou = 0

        for i, ag in enumerate(sem_coords, 1):
            print(f"[{i}/{total}] {ag.prefixo} — {ag.nome} ({ag.municipio}/{ag.uf})")

            lat, lng, query_usada = geocode_nominatim(
                ag.logradouro, ag.numero, ag.municipio, ag.uf
            )

            if lat and lng:
                ag.lat = lat
                ag.lng = lng
                db.session.commit()
                print(f"    ✓ lat={lat:.4f}, lng={lng:.4f}  [{query_usada}]")
                ok += 1
            else:
                print(f"    ✗ Não encontrado")
                falhou += 1

            time.sleep(1)  # rate limit entre agências

        print(f"\nConcluído: {ok} geocodificadas, {falhou} sem resultado.")


if __name__ == "__main__":
    main()
