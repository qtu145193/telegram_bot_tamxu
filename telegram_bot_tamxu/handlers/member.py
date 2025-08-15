from telegram import Update
from telegram.ext import ContextTypes

async def add_member(update: Update, context: ContextTypes.DEFAULT_TYPE, sheet):
    try:
        text = " ".join(context.args)
        name, address = map(str.strip, text.split(","))
        sheet.append_row([name, address])
        await update.message.reply_text(f"✅ Đã thêm {name} - {address}")
    except:
        await update.message.reply_text("❌ Sai định dạng. Dùng: /add_member Tên,ĐịaChỉ")

async def remove_member(update: Update, context: ContextTypes.DEFAULT_TYPE, sheet):
    key = " ".join(context.args).strip().lower()
    data = sheet.get_all_records()
    for i, row in enumerate(data, start=2):
        if key in row['Tên'].lower() or key in row['Địa chỉ ví'].lower():
            sheet.delete_rows(i)
            await update.message.reply_text(f"✅ Đã xoá: {row['Tên']} - {row['Địa chỉ ví']}")
            return
    await update.message.reply_text("❌ Không tìm thấy member.")
