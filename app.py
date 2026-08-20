import os
from datetime import datetime, timedelta, timezone
from apify_client import ApifyClient

# ---------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------
TARGET_USER = "picante.clips"  # Cambia por la cuenta deseada (sin el @)

APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
client = ApifyClient(APIFY_TOKEN)

def get_top3_engagement_24h(username):
    print(f"Obteniendo videos de @{username}...")
    
    run_input = {
        "profiles": [f"https://www.tiktok.com/@{username}"],
        "resultsPerPage": 30,
    }
    
    run = client.actor("clockworks/tiktok-profile-scraper").call(run_input=run_input)
    
    videos = []
    time_24h_ago = datetime.now(timezone.utc) - timedelta(hours=24)

    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        create_time_epoch = item.get("createTime") or item.get("uploadedAt")
        
        if create_time_epoch:
            if isinstance(create_time_epoch, (int, float)):
                video_date = datetime.fromtimestamp(create_time_epoch, tz=timezone.utc)
            else:
                video_date = datetime.fromisoformat(str(create_time_epoch).replace('Z', '+00:00'))
            
            # FILTRO: Publicados en las últimas 24 horas
            if video_date >= time_24h_ago:
                play_count = item.get("playCount", 0)
                likes = item.get("diggCount", 0)
                comments = item.get("commentCount", 0)
                shares = item.get("shareCount", 0)

                # Cálculo del Engagement Rate (%)
                total_interactions = likes + comments + shares
                engagement_rate = (total_interactions / play_count * 100) if play_count > 0 else 0.0

                videos.append({
                    "id": item.get("id"),
                    "title": item.get("text", "Sin título")[:60],
                    "play_count": play_count,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "engagement_rate": round(engagement_rate, 2),
                    "url": item.get("webVideoUrl", f"https://www.tiktok.com/@{username}/video/{item.get('id')}"),
                    "created_at": video_date.strftime("%Y-%m-%d %H:%M:%S UTC")
                })

    if not videos:
        print("\n" + "="*60)
        print(f" No hay videos publicados por @{username} en las últimas 24 horas.")
        print("="*60)
        return

    # ORDENAR DESCENDENTE por Engagement Rate (%)
    videos_sorted = sorted(videos, key=lambda x: x['engagement_rate'], reverse=True)

    # TOMAR SOLO EL TOP 3
    top_3_videos = videos_sorted[:3]

    # IMPRIMIR RESULTADOS
    print("\n" + "="*60)
    print(f" TOP 3 VIDEOS CON MAYOR ENGAGEMENT RATE (24H) - @{username}")
    print(" Ordenados por Tasa de Interacción (%)")
    print("="*60)
    
    for idx, vid in enumerate(top_3_videos, 1):
        print(f"#{idx} | ENGAGEMENT RATE: {vid['engagement_rate']}%")
        print(f"    Vistas Totales: {vid['play_count']:,}")
        print(f"    Interacciones:  {vid['likes']:,} Me gusta | {vid['comments']:,} Comentarios | {vid['shares']:,} Compartidos")
        print(f"    Título:        {vid['title']}")
        print(f"    Fecha Subida:  {vid['created_at']}")
        print(f"    Enlace:        {vid['url']}")
        print("-" * 60)

if __name__ == "__main__":
    get_top3_engagement_24h(TARGET_USER)
