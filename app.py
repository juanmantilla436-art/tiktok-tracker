import os
import sqlite3
from datetime import datetime, timedelta
from apify_client import ApifyClient
import pandas as pd

# CONFIGURACIÓN
# Cambia 'el_hormiguero' por la cuenta de TikTok que quieras monitorear (sin el @)
TARGET_USER = "el_hormiguero" 
DB_NAME = "tiktok_tracker.db"

# Obtiene la clave de forma segura
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
client = ApifyClient(APIFY_TOKEN)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            username TEXT NOT NULL,
            title TEXT,
            play_count INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def fetch_and_save_snapshot(username):
    print(f"Obteniendo datos de @{username}...")
    run_input = {
        "profiles": [f"https://www.tiktok.com/@{username}"],
        "resultsPerPage": 30,
    }
    
    run = client.actor("clockworks/tiktok-profile-scraper").call(run_input=run_input)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now()

    count = 0
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        video_id = item.get("id")
        title = item.get("text", "")[:50]
        play_count = item.get("playCount", 0)

        cursor.execute('''
            INSERT INTO video_snapshots (video_id, username, title, play_count, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (video_id, username, title, play_count, now))
        count += 1

    conn.commit()
    conn.close()
    print(f"Snapshot guardado exitosamente. {count} videos registrados.")

def get_top_videos_24h(username):
    conn = sqlite3.connect(DB_NAME)
    
    df_latest = pd.read_sql_query('''
        SELECT video_id, title, play_count as current_views, timestamp as latest_time
        FROM video_snapshots
        WHERE username = ? AND timestamp = (SELECT MAX(timestamp) FROM video_snapshots WHERE username = ?)
    ''', conn, params=(username, username))

    if df_latest.empty:
        print("No hay datos suficientes.")
        conn.close()
        return

    time_24h_ago = datetime.now() - timedelta(hours=24)
    
    df_past = pd.read_sql_query('''
        SELECT video_id, play_count as past_views
        FROM video_snapshots
        WHERE username = ? AND timestamp <= ?
        GROUP BY video_id
        HAVING timestamp = MAX(timestamp)
    ''', conn, params=(username, time_24h_ago))

    conn.close()

    if df_past.empty:
        print("\n[!] Primera lectura realizada. Mañana a esta misma hora verás la diferencia de vistas.")
        return

    merged = pd.merge(df_latest, df_past, on="video_id", how="inner")
    merged['views_gained_24h'] = merged['current_views'] - merged['past_views']
    ranking = merged.sort_values(by="views_gained_24h", ascending=False)

    print("\n" + "="*60)
    print(f" TOP VIDEOS MÁS VISTOS EN LAS ÚLTIMAS 24H (@{username})")
    print("="*60)
    for idx, row in ranking.head(10).iterrows():
        print(f"• Vistas Ganadas (24h): +{row['views_gained_24h']:,}")
        print(f"  Total Vistas: {row['current_views']:,}")
        print(f"  Video: {row['title']} (ID: {row['video_id']})")
        print("-" * 60)

if __name__ == "__main__":
    init_db()
    fetch_and_save_snapshot(TARGET_USER)
    get_top_videos_24h(TARGET_USER)
