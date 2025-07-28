import logging
import os
import json
from telegram import Bot
from telegram.error import TelegramError
import asyncio

# ✅ Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ✅ Load from GitHub Secrets via environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_CHAT_ID = os.environ.get("TELEGRAM_GROUP_CHAT_ID")

# 📁 File locations
JOB_DIR = 'jobs'
MANIFEST_FILE = os.path.join(JOB_DIR, 'job_manifest.json')

def load_manifest():
    if not os.path.exists(MANIFEST_FILE):
        return {
            "last_updated": "",
            "total_jobs": 0,
            "active_jobs": 0,
            "expired_jobs": 0,
            "jobs": []
        }
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_job_message(job):
    """
    Formats a single job dictionary into a human-readable message.
    """
    message = "✨ *New Job Alert!* ✨\n\n"
    message += f"*Title:* {job.get('title', 'N/A')}\n"
    message += f"*Source:* {job.get('source', 'N/A')}\n"
    message += f"*Category:* {job.get('category', 'General')}\n"
    message += f"*Description:* {job.get('description', 'N/A')[:200]}...\n"
    if job.get('important_dates'):
        for key, value in job['important_dates'].items():
            message += f"*{key.replace('_', ' ').title()}:* {value}\n"
    if job.get('skills'):
        message += f"*Skills:* {', '.join(job['skills'])}\n"
    message += f"*Link:* {job.get('url', 'N/A')}\n"
    return message

async def send_telegram_message(chat_id, message):
    """
    Sends a message to the specified Telegram chat ID.
    """
    if not BOT_TOKEN or not chat_id:
        logger.error("Missing BOT_TOKEN or CHAT_ID environment variables.")
        return

    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        logger.info(f"✅ Message sent to chat ID {chat_id}")
    except TelegramError as e:
        logger.error(f"❌ Failed to send message to {chat_id}: {e}")

async def notify_new_jobs():
    logger.info("📢 Starting Telegram notification for new jobs...")
    manifest = load_manifest()
    jobs_to_notify = manifest.get('jobs', [])

    if not jobs_to_notify:
        logger.info("ℹ️ No new jobs found to notify.")
        return

    for job in jobs_to_notify:
        message = format_job_message(job)
        await send_telegram_message(TELEGRAM_GROUP_CHAT_ID, message)

    logger.info(f"📨 Notified about {len(jobs_to_notify)} jobs.")

async def main():
    await notify_new_jobs()

if __name__ == "__main__":
    asyncio.run(main())
