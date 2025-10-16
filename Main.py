import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUMROAD_URL = os.getenv("GUMROAD_URL", "https://gigi.gumroad.com/l/exclusive-set01")
ADMIN_TELEGRAM = os.getenv("ADMIN_TELEGRAM", "@youradminhandle")

# Sensual, professional persona for Gigi Borgan
WELCOME = (
    "💋 *Welcome to Gigi Borgan — Exclusive Access*

"
    "Indulge in curated, intimate collections crafted for devoted admirers.

"
    "Choose an option below to preview or purchase content. Your discretion is respected."
)

PREVIEW_CAPTION = (
    "A whispered sample from *Set 01* — a glimpse, not the whole story.
"
    "For full access, select *Buy Access*."
)

PURCHASE_PROMPT = (
    "Your pleasure awaits. Complete your purchase securely through Gumroad:
"
    f"{GUMROAD_URL}

"
    "After purchase, you will receive a Gumroad receipt and permanent access to the purchased files.
"
    "If you prefer, send your Gumroad receipt URL or email with /redeem and we'll verify manually."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👀 View Preview", callback_data="preview")],
        [InlineKeyboardButton("💳 Buy Access", callback_data="buy")],
        [InlineKeyboardButton("📩 Redeem Purchase", callback_data="redeem")],
        [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{ADMIN_TELEGRAM.lstrip('@')}")]
    ]
    await update.message.reply_markdown_v2(WELCOME, reply_markup=InlineKeyboardMarkup(keyboard))

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "preview":
        # Replace sample.jpg with your hosted preview image
        await query.message.reply_photo(
            photo="https://via.placeholder.com/800x800.png?text=Gigi+Borgan+Preview",
            caption=PREVIEW_CAPTION,
            parse_mode="Markdown"
        )
    elif query.data == "buy":
        await query.message.reply_text(PURCHASE_PROMPT)
    elif query.data == "redeem":
        await query.message.reply_text(
            "To redeem, please reply with: /redeem <your_gumroad_receipt_url_or_email>

"
            "Example:
"
            "/redeem https://gumroad.com/receipts/xxxxxx

"
            "Our team will verify and send your private access link within 24 hours."
        )

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /redeem <gumroad_receipt_url_or_email>")
        return
    claim = " ".join(args)
    # Save claim to local file for manual verification by admin (simple queue)
    os.makedirs("claims", exist_ok=True)
    fname = f"claims/{user.id}.txt"
    with open(fname, "a") as f:
        f.write(f"{user.id}\t{user.username}\t{user.full_name}\t{claim}\n")
    await update.message.reply_text(
        "Thank you — your claim has been recorded. An admin will verify and reply with the access link.
"
        "If you need urgent help, contact support via the bot contact button."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Open menu\n"
        "/preview - View a preview image\n"
        "/buy - Get the purchase link\n"
        "/redeem <receipt_url_or_email> - Submit proof of purchase for manual verification"
    )

async def preview_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo="https://via.placeholder.com/800x800.png?text=Gigi+Borgan+Preview",
        caption=PREVIEW_CAPTION,
        parse_mode="Markdown"
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that. Use /help to see available commands.")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set. Exiting.")
        exit(1)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("preview", preview_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("🚀 Gigi Borgan Bot (Gumroad flow) is running…")
    app.run_polling()
