import json
import os
from datetime import datetime, timedelta, timezone
import requests

API_KEY = os.environ["AEMET_API_KEY"]
BASE_URL = "https://opendata.aemet.es/opendata/api"
OUTPUT_FILE = "assets/data/aemet_visibilidad.json"

AEROPUERTOS = {
    "5530E": "Granada Aeropuerto (GRX)",
    "6155A": "Málaga Aeropuerto (AGP)",
    "6325O": "Almería Aeropuerto (LEI)",
    "5783":  "Sevilla Aeropuerto (SVQ)",
    "5402":  "Córdoba Aeropuerto (ODB)",
    "5960":  "Jerez Aeropuerto (XRY)",
    "5910":  "Base Naval de Rota",
}


def descargar_observaciones_aemet():
    headers = {"api_key": API_KEY, "Accept": "application/json"}
    r = requests.get(
        f"{BASE_URL}/observacion/convencional/todas",
        headers=headers,
        timeout=20,
    )
    r.raise_for_status()
    meta = r.json()

    if meta.get("estado") != 200:
        raise RuntimeError(f"Error AEMET: {meta.get('descripcion')}")

    r_datos = requests.get(meta["datos"], timeout=30)
    r_datos.raise_for_status()
    r_datos.encoding = "latin1"
    return r_datos.json()


def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # Cargar histórico previo si existe
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            historico = json.load(f)
    else:
        historico = {"ultima_actualizacion": "", "estaciones": {}}

    observaciones = descargar_observaciones_aemet()
    limite_antiguedad = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")

    for idema, nombre in AEROPUERTOS.items():
        est_data = historico["estaciones"].setdefault(
            idema, {"nombre": nombre, "registros": []}
        )
        est_data["nombre"] = nombre

        # Indexar registros existentes por marca temporal YYYY-MM-DDTHH:MM
        mapa_registros = {
            reg["fint"]: reg
            for reg in est_data["registros"]
            if reg["fint"][:10] >= limite_antiguedad
        }

        # Añadir nuevas lecturas del visibilímetro
        for obs in observaciones:
            if obs.get("idema") == idema and obs.get("vis") is not None:
                fint = obs["fint"][:16]  # Ej: "2026-11-12T16:00"
                mapa_registros[fint] = {
                    "fint": fint,
                    "vis_m": round(float(obs["vis"]) * 1000),
                    "ta": obs.get("ta"),
                    "hr": obs.get("hr"),
                    "vv": obs.get("vv"),
                }

        est_data["registros"] = sorted(
            mapa_registros.values(), key=lambda x: x["fint"]
        )

    historico["ultima_actualizacion"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

    print(f"Actualización completada en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
