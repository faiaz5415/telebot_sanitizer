"""
Telegram Word Sanitizer Bot
----------------------------
Restricted word/phrase (e.g. "Review") পেলে auto sanitize করে
("Re-v-ie-w") reply দেয়।

Install:
    pip install python-telegram-bot --upgrade

Run:
    python sanitize_bot.py
"""

import re
import random
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# 🔴 আপনার Bot Token এখানে বসান (BotFather থেকে পাওয়া টোকেন)
# ---------------------------------------------------------
BOT_TOKEN = "8921038564:AAEoDEQfKt6xlIVIA6bmrWZxqZlQ9rUpe9c"

# ---------------------------------------------------------
# 🔴 Launcher/banner image (bot_banner.png) - এই ফাইলটা
# sanitize_bot.py এর সাথে একই folder-এ রাখতে হবে
# ---------------------------------------------------------
BANNER_IMAGE = "bot_banner.png"

# ---------------------------------------------------------
# 🔴 Restricted words/phrases এখানে যোগ করুন
# (case-insensitive match হবে, নিজের মতো যত খুশি word/sentence add করুন)
# ---------------------------------------------------------
RESTRICTED_WORDS = [
    "i work in other places besides fiverr",
    "visit my website for more details",
    "i will send files to your email",
    "here\u2019s my personal contact",
    "here's my personal contact",
    "essay writing for students",
    "fiverr review manipulation",
    "contact me outside fiverr",
    "heres my personal contact",
    "unprofessional behavior",
    "increase fiverr ratings",
    "empty/partial delivery",
    "let\u2019s move to whatsapp",
    "let's move to whatsapp",
    "let\u2019s move to telegram",
    "let's move to telegram",
    "message me on whatsapp",
    "contact me on linkedin",
    "research paper writing",
    "feedback manipulation",
    "lets move to whatsapp",
    "lets move to telegram",
    "coursework assistance",
    "reach me on facebook",
    "copyrighted material",
    "illegal transactions",
    "contact me directly",
    "credit card details",
    "copyright violation",
    "plagiarized content",
    "homework assistance",
    "dm me on instagram",
    "email list selling",
    "outside of fiverr",
    "negative feedback",
    "pay me via paypal",
    "5-star guaranteed",
    "illegal services",
    "cracked software",
    "send me an email",
    "academic writing",
    "money laundering",
    "positive rating",
    "increase rating",
    "review exchange",
    "fake engagement",
    "assignment help",
    "boost my rating",
    "escort services",
    "sexual services",
    "data harvesting",
    "freelancer.com",
    "unprofessional",
    "contact number",
    "cryptocurrency",
    "stolen content",
    "fake documents",
    "identity theft",
    "western union",
    "wire transfer",
    "peopleperhour",
    "mother fucker",
    "mobile number",
    "bank transfer",
    "adult content",
    "black hat seo",
    "phone number",
    "off-platform",
    "bank account",
    "transferwise",
    "fake reviews",
    "rating boost",
    "motherfucker",
    "outlook mail",
    "paid reviews",
    "prostitution",
    "google meet",
    "credentials",
    "offplatform",
    "transaction",
    "credit card",
    "outsourcely",
    "stolen work",
    "bot traffic",
    "buy reviews",
    "sugar daddy",
    "counterfeit",
    "credential",
    "truelancer",
    "misleading",
    "plagiarism",
    "yahoo mail",
    "debit card",
    "copy-paste",
    "sugar baby",
    "ransomware",
    "messenger",
    "instagram",
    "99designs",
    "fivesquid",
    "freelance",
    "five star",
    "gift card",
    "black hat",
    "keylogger",
    "whatsapp",
    "facebook",
    "telegram",
    "facetime",
    "password",
    "off-site",
    "linkedin",
    "payoneer",
    "ethereum",
    "spamming",
    "phishing",
    "gambling",
    "onlyfans",
    "stripper",
    "cracking",
    "fake ids",
    "scraping",
    "purchase",
    "contact",
    "twitter",
    "outside",
    "discord",
    "address",
    "offsite",
    "invoice",
    "website",
    "payment",
    "cashapp",
    "bitcoin",
    "binance",
    "workana",
    "reviews",
    "bastard",
    "asshole",
    "dumbass",
    "betting",
    "camgirl",
    "hacking",
    "carding",
    "malware",
    "wechat",
    "signal",
    "direct",
    "google",
    "paypal",
    "stripe",
    "crypto",
    "upwork",
    "toptal",
    "review",
    "coupon",
    "hacked",
    "casino",
    "nudity",
    "hentai",
    "erotic",
    "trojan",
    "tiktok",
    "skype",
    "email",
    "slack",
    "viber",
    "phone",
    "money",
    "venmo",
    "offer",
    "bitch",
    "whore",
    "fraud",
    "gmail",
    "virus",
    "zoom",
    "mail",
    "line",
    "call",
    "link",
    "bank",
    "wise",
    "cash",
    "guru",
    "sell",
    "fuck",
    "shit",
    "slut",
    "scam",
    "fake",
    "porn",
    "ddos",
    "url",
    "pay",
    "buy",
    "xxx",
    "fb",
]


def sanitize_word(phrase: str) -> str:
    """একটা word বা multi-word phrase কে random ভাবে ১ বা ২ অক্ষরের
    ছোট ছোট অংশে ভেঙে মাঝে '-' বসিয়ে sanitize করে। Space থাকলে সেটা
    অক্ষত থাকবে (স্পেসের চারপাশে dash বসবে না)।
    Example: 'Review' -> 'Re-vi-e-w'
             'lets move to whatsapp' -> 'le-ts mo-ve t-o wh-ats-a-pp'
    """
    def chunk(token: str) -> str:
        chars = list(token)
        parts = []
        i = 0
        while i < len(chars):
            remaining = len(chars) - i
            chunk_size = random.choice([1, 2]) if remaining > 1 else 1
            parts.append("".join(chars[i:i + chunk_size]))
            i += chunk_size
        return "-".join(parts)

    # phrase-কে space দিয়ে ভেঙে প্রতিটা word আলাদাভাবে chunk করে,
    # তারপর আবার space দিয়ে জোড়া লাগানো হচ্ছে
    return " ".join(chunk(token) if token else "" for token in phrase.split(" "))


def sanitize_text(text: str) -> tuple[str, int]:
    """
    টেক্সটের মধ্যে RESTRICTED_WORDS এর যেকোনোটা থাকলে
    সেটাকে sanitize করে বসিয়ে দেয়। রিটার্ন করে (নতুন টেক্সট, কতগুলো পাওয়া গেছে)
    """
    count = 0
    new_text = text

    # লম্বা phrase আগে match করবো, যাতে overlapping word এ সমস্যা না হয়
    sorted_words = sorted(RESTRICTED_WORDS, key=len, reverse=True)

    for phrase in sorted_words:
        # \b দিয়ে word-এর শুরুতে anchor করা হচ্ছে (যাতে 'line' দিয়ে
        # 'coastline'-এর মতো শব্দের মাঝখানে false match না হয়),
        # আর \w* দিয়ে পরে লেগে থাকা suffix (plural 's', '-ing' ইত্যাদি) ধরা হচ্ছে
        pattern = re.compile(r"\b" + re.escape(phrase) + r"\w*", re.IGNORECASE)

        def _replacer(match):
            nonlocal count
            count += 1
            return sanitize_word(match.group(0))

        new_text = pattern.sub(_replacer, new_text)

    return new_text, count


WELCOME_MESSAGE = (
    "Welcome to the world\u2019s most uselessly useful sanitizer \U0001F60E\u2728\n"
    "It sanitizes your words, not your germs.\n"
    "If you're trying to kill germs\u2026 sorry boss, go grab some Lifebuoy \U0001F9FC\U0001F602\n"
    "But if your messages are dirty, toxic, or just straight-up embarrassing \u2014 I got you \U0001F440\n"
    "To begin your legendary sanitizing journey with Faiaz\u2019s Pet Sanitizer \U0001F43E: "
    "\U0001F449 Type /start \U0001F449 Paste your message \U0001F449 Sit back, sip some coffee \u2615 "
    "\U0001F449 BOOM \U0001F4A5 watch the magic happen\n"
    "Your words go in messy\u2026 come out fresh like morning vibes \U0001F33F\U0001F60C"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(BANNER_IMAGE, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=WELCOME_MESSAGE)
    except FileNotFoundError:
        # ছবিটা পাওয়া না গেলে শুধু text দিয়ে welcome message পাঠাবে
        await update.message.reply_text(WELCOME_MESSAGE)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    sanitized, count = sanitize_text(text)

    if count > 0:
        await update.message.reply_text(
            f"\u26A0\uFE0F {count}টা restricted word পাওয়া গেছে!\n\nSanitized version:\n{sanitized}"
        )
    else:
        await update.message.reply_text("restricted word পাওয়া যায়নি \u2705")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot চালু হয়েছে...")
    app.run_polling()


if __name__ == "__main__":
    main()