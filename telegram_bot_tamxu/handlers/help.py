from telegram import Update
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤡 *Nắc bot tutorial:*\n\n"
        # "/check_balance – Coi thằng nào sắp hết Chip\n"
        "/check_balance – Phân biệt Nghiện và Ngài\n"
        # "/add_member – Thêm con nghiện vào clb\n"
        "/pool_to_day – Note lại ai chơi tới cuối buổi truy thu\n"
        # "/remove_member – Cai nghiện thành công\n"
        "/multi_send_50 – Tạo multi send trưa\n"
        "/multi_send_100 – Tạo multi send tối\n\n"
    )
    await update.message.reply_text(help_text)
