import os
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
import json

app = FastAPI()

# 🔥 ИСПРАВЛЕНИЕ: Ищем файлы в ТЕКУЩЕЙ папке (откуда запущен start.bat), а не внутри exe
CURRENT_DIR = os.getcwd()
DB_PATH = os.path.join(CURRENT_DIR, "bot_logs.db")
PROFILE_PATH = os.path.join(CURRENT_DIR, "profile.txt")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, guild_name TEXT,
            action_type TEXT, moderator TEXT, target_user TEXT, details TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_profile():
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("name", "Пользователь"), data.get("display_name", "Пользователь"), data.get("avatar", "")
        except Exception:
            pass
    return "Пользователь", "Пользователь", ""

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_name, user_display, avatar_url = get_profile()
    
    if not avatar_url or not avatar_url.startswith("http"):
        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, guild_name, action_type, moderator, target_user, details FROM logs ORDER BY id DESC LIMIT 100")
    rows = cursor.fetchall()
    conn.close()

    rows_html = ""
    for r in rows:
        badge_class = r[2]
        rows_html += f"""
        <tr>
            <td style="color: #a1a1aa">{r[0]}</td>
            <td style="font-weight: 600">{r[1]}</td>
            <td><span class="badge {badge_class}">{r[2]}</span></td>
            <td>{r[3]}</td>
            <td>{r[4]}</td>
            <td style="color: #a1a1aa; font-family: monospace;">{r[5]}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Локальные Логи Орбикс</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {{ --bg: #09090b; --text: #f4f4f5; --text-muted: #a1a1aa; --glass-bg: rgba(255, 255, 255, 0.03); --glass-border: rgba(255, 255, 255, 0.08); --primary: #89b4fa; --ban: #f38ba8; --mute: #fab387; --warn: #f9e2af; --say: #b4befe; }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; min-height: 100vh; overflow-x: hidden; }}
            .bg-animation {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; overflow: hidden; }}
            .orb {{ position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.4; animation: float 20s infinite alternate; }}
            .orb-1 {{ width: 400px; height: 400px; background: #89b4fa; top: -100px; left: -100px; }}
            .orb-2 {{ width: 300px; height: 300px; background: #cba6f7; bottom: -100px; right: -100px; animation-duration: 25s; }}
            .orb-3 {{ width: 200px; height: 200px; background: #f38ba8; top: 40%; left: 40%; animation-duration: 15s; }}
            @keyframes float {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(50px, 50px) scale(1.1); }} }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 40px 20px; }}
            .glass {{ background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }}
            .logo {{ font-size: 24px; font-weight: 800; display: flex; align-items: center; gap: 10px; }}
            .logo i {{ color: var(--primary); }}
            .highlight {{ color: var(--primary); }}
            .user-info {{ display: flex; align-items: center; gap: 15px; text-align: right; }}
            .user-info img {{ width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--primary); }}
            .user-info .nick {{ font-weight: 600; font-size: 14px; }}
            .user-info .display {{ font-size: 12px; color: var(--text-muted); }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ padding: 24px; display: flex; align-items: center; gap: 20px; transition: transform 0.3s, box-shadow 0.3s; }}
            .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 40px rgba(0,0,0,0.3); }}
            .stat-icon {{ width: 60px; height: 60px; border-radius: 16px; display: flex; justify-content: center; align-items: center; font-size: 24px; }}
            .stat-card.ban .stat-icon {{ background: rgba(243, 139, 168, 0.1); color: var(--ban); }}
            .stat-card.mute .stat-icon {{ background: rgba(250, 179, 135, 0.1); color: var(--mute); }}
            .stat-card.warn .stat-icon {{ background: rgba(249, 226, 175, 0.1); color: var(--warn); }}
            .stat-card.say .stat-icon {{ background: rgba(180, 190, 254, 0.1); color: var(--say); }}
            .stat-info h3 {{ font-size: 14px; color: var(--text-muted); font-weight: 400; margin-bottom: 5px; }}
            .stat-value {{ font-size: 32px; font-weight: 800; }}
            .logs-section {{ padding: 0; overflow: hidden; }}
            .table-wrapper {{ overflow-x: auto; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 16px 20px; text-align: left; font-size: 14px; }}
            th {{ background: rgba(0,0,0,0.2); color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }}
            tbody tr {{ border-bottom: 1px solid var(--glass-border); transition: background 0.3s; }}
            tbody tr:hover {{ background: rgba(255,255,255,0.02); }}
            .badge {{ padding: 5px 12px; border-radius: 8px; font-size: 11px; font-weight: 800; text-transform: uppercase; }}
            .badge.BAN {{ background: rgba(243, 139, 168, 0.15); color: var(--ban); border: 1px solid rgba(243, 139, 168, 0.3); }}
            .badge.MUT {{ background: rgba(250, 179, 135, 0.15); color: var(--mute); border: 1px solid rgba(250, 179, 135, 0.3); }}
            .badge.WARN {{ background: rgba(249, 226, 175, 0.15); color: var(--warn); border: 1px solid rgba(249, 226, 175, 0.3); }}
            .badge.SAY {{ background: rgba(180, 190, 254, 0.15); color: var(--say); border: 1px solid rgba(180, 190, 254, 0.3); }}
            .footer {{ text-align: center; color: var(--text-muted); margin-top: 40px; font-size: 12px; }}
            .fade-in {{ opacity: 0; transform: translateY(20px); animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}
            .delay-1 {{ animation-delay: 0.1s; }} .delay-2 {{ animation-delay: 0.2s; }}
            @keyframes fadeInUp {{ to {{ opacity: 1; transform: translateY(0); }} }}
        </style>
    </head>
    <body>
        <div class="bg-animation"><div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div></div>
        <div class="container">
            <header class="header fade-in">
                <div class="logo"><i class="fa-solid fa-shield-halved"></i><span>ORBIX <span class="highlight">STUDIO</span></span></div>
                <div class="user-info">
                    <div>
                        <div class="nick">{user_name}</div>
                        <div class="display">{user_display}</div>
                    </div>
                    <img src="{avatar_url}" alt="Аватар">
                </div>
            </header>
            
            <section class="stats-grid fade-in delay-1">
                <div class="stat-card glass ban"><div class="stat-icon"><i class="fa-solid fa-gavel"></i></div><div class="stat-info"><h3>Баны</h3><div class="stat-value counter" data-target="0">0</div></div></div>
                <div class="stat-card glass mute"><div class="stat-icon"><i class="fa-solid fa-microphone-slash"></i></div><div class="stat-info"><h3>Муты</h3><div class="stat-value counter" data-target="0">0</div></div></div>
                <div class="stat-card glass warn"><div class="stat-icon"><i class="fa-solid fa-triangle-exclamation"></i></div><div class="stat-info"><h3>Варны</h3><div class="stat-value counter" data-target="0">0</div></div></div>
                <div class="stat-card glass say"><div class="stat-icon"><i class="fa-solid fa-bullhorn"></i></div><div class="stat-info"><h3>Объявления</h3><div class="stat-value counter" data-target="0">0</div></div></div>
            </section>

            <section class="logs-section fade-in delay-2 glass">
                <div class="table-wrapper">
                    <table>
                        <thead><tr><th>Время</th><th>Сервер</th><th>Действие</th><th>Модератор</th><th>Нарушитель</th><th>Детали</th></tr></thead>
                        <tbody>{rows_html if rows_html else '<tr><td colspan="6" style="text-align:center; padding: 40px; color: #a1a1aa;">Логи пока отсутствуют</td></tr>'}</tbody>
                    </table>
                </div>
            </section>
            
            <div class="footer">Создатель проекта: Ёжик</div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=58339)
