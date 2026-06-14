import os
import re
import urllib.request
import json
import smtplib
from email.mime.text import MIMEText

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
ENV_FILE = os.path.join(BASE_DIR, ".env")

def load_env():
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, val = line.split("=", 1)
                        env[key.strip()] = val.strip()
    return env

def find_task_title_in_tasks_md(tasks_file, task_id):
    if not os.path.exists(tasks_file):
        return ""
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(rf"###\s+{task_id}\s*[-—]\s*(.+)", content)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return ""

def send_http_post(url, data_dict):
    try:
        data_bytes = json.dumps(data_dict).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json", "User-Agent": "GovernAI-Notifier"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status in [200, 201, 204]
    except Exception as e:
        print(f"[NOTIFIER] [ERRO] Falha ao enviar HTTP POST: {e}")
        return False

def send_slack_notification(url, task_id, title, message):
    payload = {
        "text": f"⚠️ *[ALERTA DE GOVERNANÇA] GovernAI*\n*Tarefa:* {task_id} - {title}\n*Alerta:* {message}"
    }
    return send_http_post(url, payload)

def send_discord_notification(url, task_id, title, message):
    payload = {
        "content": f"⚠️ **[ALERTA DE GOVERNANÇA] GovernAI**\n**Tarefa:** {task_id} - {title}\n**Alerta:** {message}"
    }
    return send_http_post(url, payload)

def send_email_notification(smtp_config, task_id, title, message):
    try:
        host = smtp_config.get("host")
        port = int(smtp_config.get("port", 587))
        user = smtp_config.get("user")
        password = smtp_config.get("password")
        to_email = smtp_config.get("to")
        
        msg = MIMEText(f"Alerta de Governança no GovernAI\n\nTarefa: {task_id} - {title}\nAlerta: {message}")
        msg["Subject"] = f"⚠️ [ALERTA] GovernAI - {task_id}"
        msg["From"] = user
        msg["To"] = to_email
        
        with smtplib.SMTP(host, port) as server:
            if port == 587:
                server.starttls()
            if user and password:
                server.login(user, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[NOTIFIER] [ERRO] Falha ao enviar e-mail: {e}")
        return False

def send_notifications(task_id, message):
    env = load_env()
    tasks_file = os.path.join(BASE_DIR, "TASKS.md")
    title = find_task_title_in_tasks_md(tasks_file, task_id)
    if not title:
        title = "Tarefa sem título local"
        
    slack_url = env.get("GOVERNAI_SLACK_WEBHOOK_URL") or env.get("SLACK_WEBHOOK_URL")
    discord_url = env.get("GOVERNAI_DISCORD_WEBHOOK_URL") or env.get("DISCORD_WEBHOOK_URL")
    smtp_host = env.get("GOVERNAI_SMTP_HOST")
    
    sent = False
    
    if slack_url:
        if send_slack_notification(slack_url, task_id, title, message):
            print(f"[NOTIFIER] Alerta enviado para o Slack para a tarefa {task_id}.")
            sent = True
            
    if discord_url:
        if send_discord_notification(discord_url, task_id, title, message):
            print(f"[NOTIFIER] Alerta enviado para o Discord para a tarefa {task_id}.")
            sent = True
            
    if smtp_host:
        smtp_config = {
            "host": smtp_host,
            "port": env.get("GOVERNAI_SMTP_PORT", 587),
            "user": env.get("GOVERNAI_SMTP_USER"),
            "password": env.get("GOVERNAI_SMTP_PASSWORD"),
            "to": env.get("GOVERNAI_SMTP_TO")
        }
        if send_email_notification(smtp_config, task_id, title, message):
            print(f"[NOTIFIER] Alerta enviado por e-mail para a tarefa {task_id}.")
            sent = True
            
    if not sent:
        print(f"[NOTIFIER] [AVISO] Alerta gerado para {task_id}, mas nenhum adaptador de notificacao configurado no .env.")
