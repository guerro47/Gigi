import os
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import escape_markdown
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUMROAD_URL = os.getenv("GUMROAD_URL", "https://gigi.gumroad.com/l/exclusive-set01")
ADMIN_TELEGRAM = os.getenv("ADMIN_TELEGRAM", "@youradminhandle")
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Database setup
Base = declarative_base()

class Claim(Base):
    __tablename__ = 'claims'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    full_name = Column(String)
    claim = Column(Text)

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()

async def generate_text(prompt):
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured."
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating text: {e}")
        return "Sorry, I'm having trouble thinking right now."


PURCHASE_PROMPT = (
    "Your pleasure awaits. Complete your purchase securely through Gumroad:\n\n"
    f"{GUMROAD_URL}\n\n"
    "After purchase, you will receive a Gumroad receipt and permanent access to the purchased files.\n\n"
    "If you prefer, send your Gumroad receipt URL or email with /redeem and we'll verify manually."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Create a sensual, professional, and brief welcome message for a Telegram bot named Gigi Borgan that sells exclusive, intimate content. The message should be welcoming and mysterious, inviting users to explore the bot's offerings. Use markdown for emphasis."
    welcome_message = await generate_text(prompt)
    escaped_welcome_message = escape_markdown(welcome_message, version=2)
    keyboard = [
        [InlineKeyboardButton("👀 View Preview", callback_data="preview")],
        [InlineKeyboardButton("💳 Buy Access", callback_data="buy")],
        [InlineKeyboardButton("📩 Redeem Purchase", callback_data="redeem")],
        [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{ADMIN_TELEGRAM.lstrip('@')}")]
    ]
    await update.message.reply_markdown_v2(escaped_welcome_message, reply_markup=InlineKeyboardMarkup(keyboard))

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "preview":
        prompt = "Create a short, alluring caption for a preview image from an exclusive photo set. The caption should be mysterious and enticing, encouraging users to purchase the full set. Use markdown for emphasis."
        preview_caption = await generate_text(prompt)
        escaped_preview_caption = escape_markdown(preview_caption, version=2)
        # Replace sample.jpg with your hosted preview image
        await query.message.reply_photo(
            photo="https://via.placeholder.com/800x800.png?text=Gigi+Borgan+Preview",
            caption=escaped_preview_caption,
            parse_mode="MarkdownV2"
        )
    elif query.data == "buy":
        await query.message.reply_text(PURCHASE_PROMPT)
    elif query.data == "redeem":
        await query.message.reply_text(
            "To redeem, please reply with: /redeem <your_gumroad_receipt_url_or_email>\n\n"
            "Example:\n"
            "/redeem https://gumroad.com/receipts/xxxxxx\n\n"
            "Our team will verify and send your private access link within 24 hours."
        )

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /redeem <gumroad_receipt_url_or_email>")
        return
    claim_text = " ".join(args)
    
    if not DATABASE_URL:
        await update.message.reply_text("Error: Database not configured. Please contact support.")
        return

    new_claim = Claim(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        claim=claim_text
    )
    db_session.add(new_claim)
    db_session.commit()

    await update.message.reply_text(
        "Thank you — your claim has been recorded. An admin will verify and reply with the access link.\n\n"
        "If you need urgent help, contact support via the bot contact button."
    )

async def view_claims_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if f"@{user.username}" != ADMIN_TELEGRAM:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not DATABASE_URL:
        await update.message.reply_text("Error: Database not configured.")
        return
        
    claims = db_session.query(Claim).all()
    if not claims:
        await update.message.reply_text("No claims found.")
        return

    message = "Claims:\n"
    for claim in claims:
        message += f"ID: {claim.id}, User: {claim.username}, Claim: {claim.claim}\n"
    
    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Create a helpful and friendly message for a Telegram bot that lists the available commands. The commands are: /start, /preview, /buy, and /redeem. Briefly explain what each command does."
    help_text = await generate_text(prompt)
    escaped_help_text = escape_markdown(help_text, version=2)
    await update.message.reply_text(escaped_help_text, parse_mode="MarkdownV2")

async def preview_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Create a short, alluring caption for a preview image from an exclusive photo set. The caption should be mysterious and enticing, encouraging users to purchase the full set. Use markdown for emphasis."
    preview_caption = await generate_text(prompt)
    escaped_preview_caption = escape_markdown(preview_caption, version=2)
    await update.message.reply_photo(
        photo="https://via.placeholder.com/800x800.png?text=Gigi+Borgan+Preview",
        caption=escaped_preview_caption,
        parse_mode="MarkdownV2"
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that. Use /help to see available commands.")

if __name__ == "__main__":
    print(f"BOT_TOKEN from environment: {BOT_TOKEN}")
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set. Exiting.")
        exit(1)
    
    if not DATABASE_URL:
        print("WARNING: DATABASE_URL environment variable not set. Claims will not be saved.")

    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY environment variable not set. Personality features will be disabled.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("preview", preview_cmd))
    app.add_handler(CommandHandler("view_claims", view_claims_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("🚀 Gigi Borgan Bot (Gumroad flow) is running…")
    app.run_polling()
