import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram import ReplyKeyboardMarkup, Update
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from web3 import Web3
from .handlers.balance import check_balance, check_pool
from .handlers.multi_send import multi_send_prepare, multi_send_button_handler, handle_number_input
from .handlers.pool import pool_to_day, pool_button_handler, show_pool_buttons, show_pool_button_handler
from .handlers.help import help_handler
import os, json
from dotenv import load_dotenv
from .handlers.check_tsx_pool import pool_token_txns, pool_txns_handler
from .handlers.two_weeks_result import check_result, refund
from .handlers.roll import roll3, roll3_cham

# === CONFIG ===
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
SHEET_URL = os.getenv('SHEET_URL')
WEB3_RPC = os.getenv('WEB3_RPC')
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')

# === GOOGLE SHEET ===
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
google_credentials = os.getenv("GOOGLE_CREDENTIALS")
if not google_credentials:
    raise ValueError("⚠️ Missing GOOGLE_CREDENTIALS environment variable")

creds_dict = json.loads(google_credentials)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).worksheet("Address")

w3 = Web3(Web3.HTTPProvider(WEB3_RPC))

logging.basicConfig(level=logging.INFO)


def get_rows(sheet):
    try:
        # Nếu header trong sheet không chuẩn, định nghĩa thủ công
        expected_headers = ["No","Tên", "Viction Address", "ONEID"]  # sửa theo sheet của bạn
        rows = sheet.get_all_records(expected_headers=expected_headers)
        print(f"Đã lấy {len(rows)} rows từ sheet.")
        return rows
    except Exception as e:
        print("Lỗi khi lấy rows từ sheet:", e)
        # Nếu có lỗi, lấy tất cả giá trị và xử lý thủ công
        all_values = sheet.get_all_values()
        if not all_values or len(all_values) < 2:
            return []
        headers = all_values[1]  # row đầu tiên
        data_rows = all_values[2:]
        rows = []
        for r in data_rows:
            row_dict = {headers[i] if i < len(headers) else f"Column{i}": r[i] if i < len(r) else "" for i in range(len(headers))}
            rows.append(row_dict)
        return rows



async def on_startup(application):
    try:
        rows = get_rows(sheet)
        application.bot_data['rows'] = rows
        print(f"Đã lưu {len(rows)} dòng rows vào bot_data\n")

        # In từng dòng dữ liệu để debug
        for i, row in enumerate(rows, start=1):
            print(f"Row {i}: {row}")
    except Exception as e:
        print("Lỗi khi lấy hoặc in rows:", e)


async def start(update, context):
    keyboard = [
        ["/check_balance", "/check_pool", "/pool_to_day","/pool_qr"],
        ["/lac_xuc_xac","/multi_send_50","/lac_cham","/update_sheet" ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Chọn con đường để đi   :",
        reply_markup=reply_markup
    )


async def update_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rows = get_rows(sheet)
        context.bot_data["rows"] = rows
        await update.message.reply_text(f"✅ Đã cập nhật dữ liệu từ Google Sheet, tổng {len(rows)} dòng.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi cập nhật dữ liệu: {e}")


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Đăng ký hàm chạy khi bot start
    app.post_init = on_startup
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check_balance", lambda u, c: check_balance(u, c, w3)))
    app.add_handler(CommandHandler("check_pool", lambda u, c: check_pool(u, c, w3)))
    app.add_handler(CommandHandler("test", lambda u, c: test(u, c, w3)))
    # app.add_handler(CommandHandler("add_member", lambda u, c: add_member(u, c, sheet)))
    # app.add_handler(CommandHandler("remove_member", lambda u, c: remove_member(u, c, sheet)))
    app.add_handler(CommandHandler("multi_send_50", lambda u, c: multi_send_prepare(u, c, 50_000)))
    app.add_handler(CommandHandler("multi_send_100", lambda u, c: multi_send_prepare(u, c, 100_000)))
    app.add_handler(CallbackQueryHandler(multi_send_button_handler, pattern="^multi_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_number_input))
    app.add_handler(CommandHandler("pool_to_day", pool_to_day))
    app.add_handler(CommandHandler("pool_qr", show_pool_buttons))
    app.add_handler(CallbackQueryHandler(pool_button_handler, pattern="^pool_(add|sub)\\|"))
    app.add_handler(CallbackQueryHandler(pool_button_handler, pattern="^pool_done"))           # cho Done
    app.add_handler(CallbackQueryHandler(show_pool_button_handler, pattern="^pool_")) 
    app.add_handler(CommandHandler("check_pool_received", pool_token_txns))
    app.add_handler(CallbackQueryHandler(pool_txns_handler, pattern=r"^pool_txns\|"))
    app.add_handler(CommandHandler("update_sheet", update_sheet))
    app.add_handler(CommandHandler("check_result",  lambda u, c: check_result(u, c, w3)))
    app.add_handler(CommandHandler("refund",  lambda u, c: check_result(u, c, w3)))
    app.add_handler(CommandHandler("lac_xuc_xac", roll3))
    # app.add_handler(CommandHandler("lac_cham", roll3_cham))
    app.add_handler(CommandHandler("help", help_handler))
    app.run_polling()


if __name__ == '__main__':
    main()
