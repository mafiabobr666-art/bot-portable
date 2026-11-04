import os
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bot_logs.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, guild_name TEXT,
            action_type TEXT, moderator TEXT, target_user TEXT, details TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_id = request.query_params.get("user_id", "0")
    user_avatar = request.query_params.get("avatar", "https://cdn.discordapp.com/embed/avatars/0.png")
    user_name = request.query_params.get("name", "Пользователь")
    user_display = request.query_params.get("display_name", "Пользователь")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, guild_name, action_type, moderator, target_user, details FROM logs ORDER BY id DESC LIMIT 100")
    rows = cursor.fetchall()
    conn.close()

    rows_html = ""
    for r in rows:
        badge_class = "BAN" if r[2] == "BAN" else "MUT" if r[2] == "MUT" else "SAY"
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
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{ background: #09090b; color: #f4f4f5; font-family: 'Inter', sans-serif; padding: 40px; margin: 0; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; }}
            .user-info {{ display: flex; align-items: center; gap: 15px; background: rgba(255,255,255,0.05); padding: 10px 20px; border-radius: 10px; }}
            .user-info img {{ width: 40px; height: 40px; border-radius: 50%; }}
            .user-info .nick {{ font-weight: 800; color: #89b4fa; font-size: 14px; }}
            .user-info .display {{ font-size: 12px; color: #a1a1aa; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); text-align: left; font-size: 14px; }}
            th {{ color: #89b4fa; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }}
            tr:hover {{ background: rgba(255,255,255,0.02); }}
            .badge {{ padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 11px; }}
            .BAN {{ background: rgba(243, 139, 168, 0.15); color: #f38ba8; }}
            .MUT {{ background: rgba(250, 179, 135, 0.15); color: #fab387; }}
            .SAY {{ background: rgba(180, 190, 254, 0.15); color: #b4befe; }}
            .footer {{ text-align: center; color: #585b70; margin-top: 40px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🖥️ Локальные Логи</h1>
                <div class="user-info">
                    <img src="{user_avatar}" alt="Аватар">
                    <div>
                        <div class="nick">{user_name}</div>
                        <div class="display">{user_display}</div>
                    </div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr><th>Время</th><th>Сервер</th><th>Действие</th><th>Модератор</th><th>Нарушитель</th><th>Детали</th></tr>
                </thead>
                <tbody>
                    {rows_html if rows_html else '<tr><td colspan="6" style="text-align:center; color:#555;">Логов пока нет</td></tr>'}
                </tbody>
            </table>
            
            <div class="footer">Создатель проекта: Ёжик</div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=58339)