
import logging
import os
import json
from telegram import Bot
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(level=logging.INFO, format=\'%(asctime)s - %(levelname)s - %(message)s\')
logger = logging.getLogger(__name__)

# Bot token provided in the prompt
BOT_TOKEN = \'8124593711:AAFeVuf_x7ok_8PJx97e92SaDpcdTwafYlg\'

# Chat IDs (replace with actual IDs for personal chat if needed)
TELEGRAM_GROUP_CHAT_ID = \'-1002642236931\'
# PERSONAL_TELEGRAM_CHAT_ID = \'YOUR_PERSONAL_CHAT_ID\' # Uncomment and replace if personal chat is needed

JOB_DIR = \'jobs\'
MANIFEST_FILE = os.path.join(JOB_DIR, \'job_manifest.json\')

def load_manifest():
    if not os.path.exists(MANIFEST_FILE):
        return {
            "last_updated": "",
            "total_jobs": 0,
            "active_jobs": 0,
            "expired_jobs": 0,
            "jobs": []
        }
    with open(MANIFEST_FILE, \'r\') as f:
        return json.load(f)

def format_job_message(job):
    """
    Formats a single job dictionary into a human-readable message.
    """
    message = f"✨ *New Job Alert!* ✨\n\n"
    message += f"*Title:* {job.get(\'title\', \'N/A\')}\n"
    message += f"*Source:* {job.get(\'source\', \'N/A\')}\n"
    message += f"*Category:* {job.get(\'category\', \'General\')}\n"
    message += f"*Description:* {job.get(\'description\', \'N/A\')[:200]}...\n"
    if job.get(\'important_dates\'):
        for key, value in job[\'important_dates\'].items():
            message += f"*{key.replace(\'_\', \' \').title()}:* {value}\n"
    if job.get(\'skills\'):
        message += f"*Skills:* {\', \'.join(job[\'skills\'])}\n"
    message += f"*Link:* {job.get(\'url\', \'N/A\')}\n\n"
    return message

async def send_telegram_message(chat_id, message):
    """
    Sends a message to the specified Telegram chat ID.
    """
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=\'Markdown\')
        logger.info(f"Message sent to chat ID {chat_id}")
    except TelegramError as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")

async def notify_new_jobs():
    """
    Loads job data and sends notifications for new jobs.
    This function assumes that \'new\' jobs are those not yet notified.
    A more robust solution would involve tracking notified jobs in the manifest.
    """
    logger.info("Starting Telegram notification for new jobs...")
    manifest = load_manifest()
    
    # For demonstration, let's assume all jobs in the manifest are \'new\' for now.
    # In a real scenario, you would compare with previously notified jobs.
    jobs_to_notify = manifest.get(\'jobs\', [])

    if not jobs_to_notify:
        logger.info("No new jobs to notify.")
        return

    for job in jobs_to_notify:
        message = format_job_message(job)
        await send_telegram_message(TELEGRAM_GROUP_CHAT_ID, message)
        # if PERSONAL_TELEGRAM_CHAT_ID:
        #     await send_telegram_message(PERSONAL_TELEGRAM_CHAT_ID, message)

    logger.info(f"Notified about {len(jobs_to_notify)} jobs.")

async def main():
    await notify_new_jobs()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


