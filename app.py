import os
import shutil
from datetime import datetime, timedelta, timezone
from apify_client import ApifyClient

# ---------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------
TARGET_USER = "picante.clips"  # Cuenta a monitorear (sin el @)

APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
client = ApifyClient(APIFY_TOKEN)

def generate_html_report(username, top_videos, date_str):
    """Genera una página HTML visual con diseño Dashboard moderno."""
    os.makedirs("reports", exist_ok=True)
    filename_date = f"reports/reporte_{date_str}.html"
    filename_index = "index.html"

    cards_html = ""
    medals = ["🥇 #1", "🥈 #2", "🥉 #3"]
    rank_classes = ["rank-1", "rank-2", "rank-3"]

    if not top_videos:
        cards_html = f"""
        <div class="empty-state">
            <h2>Sin publicaciones recientes</h2>
            <p>La cuenta <strong>@{username}</strong> no ha publicado videos en las últimas 24 horas.</p>
        </div>
        """
    else:
        for idx, vid in enumerate(top_videos):
            medal = medals[idx] if idx < 3 else f"#{idx+1}"
            rank_class = rank_classes[idx] if idx < 3 else ""
            
            cards_html += f"""
            <div class="card">
                <div class="card-header">
                    <span class="rank-tag {rank_class}">{medal} Top Engagement</span>
                    <span class="er-badge">{vid['engagement_rate']}% ER</span>
                </div>
                <div class="video-title">{vid['title']}</div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Vistas</span>
                        <span class="stat-value">{vid['play_count']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Me Gusta</span>
                        <span class="stat-value">{vid['likes']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Comentarios</span>
                        <span class="stat-value">{vid['comments']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Compartidos</span>
                        <span class="stat-value">{vid['shares']:,}</span>
                    </div>
                </div>
                <div class="card-footer">
                    <span>Subido: {vid['created_at']}</span>
                    <a href="{vid['url']}" class="btn-link" target="_blank">Ver en TikTok ↗</a>
                </div>
            </div>
            """

    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte TikTok - @{username}</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent-pink: #ff0050;
            --accent-cyan: #00f2fe;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: var(--bg-color); color: var(--text-main); padding: 2rem 1rem; min-height: 100vh; }}
        .container {{ max-width: 850px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 2.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--border-color); }}
        .header h1 {{ font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, var(--accent-pink), var(--accent-cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }}
        .header .subtitle {{ color: var(--text-muted); font-size: 0.95rem; }}
        .account-badge {{ display: inline-block; background: rgba(255, 0, 80, 0.1); color: var(--accent-pink); border: 1px solid rgba(255, 0, 80, 0.3); padding: 0.3rem 0.9rem; border-radius: 20px; font-weight: 600; margin-top: 0.8rem; font-size: 0.9rem; }}
        .grid {{ display: flex; flex-direction: column; gap: 1.5rem; }}
        .card {{ background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
        .rank-tag {{ font-weight: 800; font-size: 1.15rem; }}
        .rank-1 {{ color: #f59e0b; }}
        .rank-2 {{ color: #cbd5e1; }}
        .rank-3 {{ color: #b45309; }}
        .er-badge {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #ffffff; font-weight: 700; font-size: 0.95rem; padding: 0.4rem 0.8rem; border-radius: 10px; }}
        .video-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 1.2rem; color: #f1f5f9; line-height: 1.4; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.8rem; margin-bottom: 1.2rem; background: rgba(15, 23, 42, 0.6); padding: 1rem; border-radius: 12px; }}
        .stat-item {{ display: flex; flex-direction: column; }}
        .stat-label {{ font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.2rem; }}
        .stat-value {{ font-size: 1.05rem; font-weight: 700; color: #ffffff; }}
        .card-footer {{ display: flex; justify-content: space-between; align-items: center; padding-top: 0.8rem; border-top: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.85rem; color: var(--text-muted); }}
        .btn-link {{ display: inline-flex; align-items: center; background-color: var(--accent-pink); color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.85rem; }}
        .empty-state {{ text-align: center; padding: 3rem 1rem; background-color: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color); color: var(--text-muted); }}
        @media (max-width: 600px) {{ body {{ padding: 1rem 0.5rem; }} .card {{ padding: 1rem; }} .stats-grid {{ grid-template-columns: 1fr 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TikTok Performance Dashboard</h1>
            <p class="subtitle">Última actualización: {date_str}</p>
            <div class="account-badge">@{username}</div>
        </div>
        <div class="grid">
            {cards_html}
        </div>
    </div>
</body>
</html>"""

    # Guardar reporte histórico con fecha
    with open(filename_date, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    # Guardar como index.html para la portada de GitHub Pages
    with open(filename_index, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f" Reporte generado exitosamente.")

def get_top3_engagement_24h(username):
    print(f"Obteniendo videos de @{username}...")
    
    run_input = {
        "profiles": [f"https://www.tiktok.com/@{username}"],
        "resultsPerPage": 30,
    }
    
    run = client.actor("clockworks/tiktok-profile-scraper").call(run_input=run_input)
    
    videos = []
    time_24h_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    today_str = datetime.now().strftime("%Y-%m-%d")

    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        create_time_epoch = item.get("createTime") or item.get("uploadedAt")
        
        if create_time_epoch:
            if isinstance(create_time_epoch, (int, float)):
                video_date = datetime.fromtimestamp(create_time_epoch, tz=timezone.utc)
            else:
                video_date = datetime.fromisoformat(str(create_time_epoch).replace('Z', '+00:00'))
            
            if video_date >= time_24h_ago:
                play_count = item.get("playCount", 0)
                likes = item.get("diggCount", 0)
                comments = item.get("commentCount", 0)
                shares = item.get("shareCount", 0)

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

    videos_sorted = sorted(videos, key=lambda x: x['engagement_rate'], reverse=True)
    top_3_videos = videos_sorted[:3]

    generate_html_report(username, top_3_videos, today_str)

if __name__ == "__main__":
    get_top3_engagement_24h(TARGET_USER)
