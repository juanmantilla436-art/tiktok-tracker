import os
from datetime import datetime, timedelta, timezone
from apify_client import ApifyClient

# ---------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------
# Nombre del usuario de TikTok (sin el @)
TARGET_USER = "picante.clips" 

# Clave de la API
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
client = ApifyClient(APIFY_TOKEN)

def get_videos_last_24h(username):
    print(f"Obteniendo videos de @{username}...")
    
    # Iniciar la extracción con Apify
    run_input = {
        "profiles": [f"https://www.tiktok.com/@{username}"],
        "resultsPerPage": 30,  # Evalúa los videos más recientes del perfil
    }
    
    run = client.actor("clockworks/tiktok-profile-scraper").call(run_input=run_input)
    
    videos = []
    # Definir el límite de hace exactamente 24 horas (en tiempo UTC)
    time_24h_ago = datetime.now(timezone.utc) - timedelta(hours=24)

    # Procesar cada video obtenido
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        # Obtener fecha de creación del video (en Unix Timestamp)
        create_time_epoch = item.get("createTime") or item.get("uploadedAt")
        
        if create_time_epoch:
            # Convertir timestamp a fecha
            if isinstance(create_time_epoch, (int, float)):
                video_date = datetime.fromtimestamp(create_time_epoch, tz=timezone.utc)
            else:
                # Si viene en formato ISO string
                video_date = datetime.fromisoformat(str(create_time_epoch).replace('Z', '+00:00'))
            
            # FILTRO: ¿Fue publicado en las últimas 24 horas?
            if video_date >= time_24h_ago:
                videos.append({
                    "id": item.get("id"),
                    "title": item.get("text", "Sin título")[:60], # Primeros 60 caracteres
                    "play_count": item.get("playCount", 0),
                    "url": item.get("webVideoUrl", f"https://www.tiktok.com/@{username}/video/{item.get('id')}"),
                    "created_at": video_date.strftime("%Y-%m-%d %H:%M:%S UTC")
                })

    if not videos:
        print("\n" + "="*60)
        print(f" No hay videos publicados por @{username} en las últimas 24 horas.")
        print("="*60)
        return

    # ORDENAR DESCENDENTE por número de vistas (play_count)
    videos_sorted = sorted(videos, key=lambda x: x['play_count'], reverse=False) # Mayor a menor

    # IMPRIMIR RESULTADOS
    print("\n" + "="*60)
    print(f" VIDEOS SUBIDOS EN LAS ÚLTIMAS 24H (@{username})")
    print(" Ordenados por Vistas (Mayor a Menor)")
    print("="*60)
    
    for idx, vid in enumerate(reversed(videos_sorted), 1):
        print(f"{idx}. VISTAS: {vid['play_count']:,}")
        print(f"   Título: {vid['title']}")
        print(f"   Fecha Subida: {vid['created_at']}")
        print(f"   Enlace: {vid['url']}")
        print("-" * 60)

if __name__ == "__main__":
    get_videos_last_24h(TARGET_USER)
