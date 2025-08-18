from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters

# Khởi tạo multi send
async def multi_send_prepare(update: Update, context: ContextTypes.DEFAULT_TYPE, multiplier: int):
    rows = context.bot_data.get("rows", [])
    names = [row["Tên"] for row in rows if "pool" not in row.get("Tên", "").lower()]
    context.user_data["multi_send_counts"] = {name: 0 for name in names}
    context.user_data["multiplier"] = multiplier
    await send_multi_send_buttons(update, context.user_data["multi_send_counts"])


# Gửi bảng chọn
async def send_multi_send_buttons(update_or_query, multi_send_counts):
    keyboard = []
    for name, count in multi_send_counts.items():
        keyboard.append([InlineKeyboardButton(f"{name}:{count}", callback_data=f"multi_edit|{name}")])

    keyboard.append([InlineKeyboardButton("✅ Done", callback_data="multi_done")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_query, "message"):
        await update_or_query.message.reply_text(
            text="📋 *Chọn tên để nhập số lượng:*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif hasattr(update_or_query, "edit_message_reply_markup"):
        await update_or_query.edit_message_reply_markup(reply_markup=reply_markup)


# Xử lý click nút
async def multi_send_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("multi_edit|"):
        _, name = data.split("|", 1)
        context.user_data["waiting_for_number"] = name
        await query.message.reply_text(f"💬 Nhập số lượng cho *{name}*:", parse_mode="Markdown")

    elif data == "multi_done":
        await send_multi_send_result(update, context)


# Xử lý nhập số
async def handle_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "waiting_for_number" in context.user_data:
        name = context.user_data.pop("waiting_for_number")
        try:
            count = int(update.message.text.strip())
            if count < 0:
                raise ValueError
            # Lưu số lượng vào state
            context.user_data["multi_send_counts"][name] = count
            await update.message.reply_text(f"✅ Đã set {count} cho {name}")
            # Cập nhật lại bảng ngay
            await send_multi_send_buttons(update, context.user_data["multi_send_counts"])
        except ValueError:
            await update.message.reply_text("❌ Vui lòng nhập số hợp lệ.")


# Kết quả cuối
async def send_multi_send_result(update_or_query, context):
    rows = context.bot_data.get("rows", [])
    counts = context.user_data.get("multi_send_counts", {})
    multiplier = context.user_data.get("multiplier", 1)

    output_lines = []
    names = []

    for name, count in counts.items():
        if count > 0:
            matched_row = next((row for row in rows if row.get("Tên", "").strip() == name), None)
            if matched_row:
                address = matched_row.get("Viction Address", "").strip()
                amount = count * multiplier
                output_lines.append(f"{address}?{amount}")
                names.append(name)

    if not output_lines:
        text = "❌ Không có ai được gửi tụ."
    else:
        names_line = " - ".join(names)
        text = f"Em Fan mấy a đại: {names_line}\n" + ";".join(output_lines)

    if hasattr(update_or_query, "callback_query"):
        await update_or_query.callback_query.edit_message_text(text, parse_mode="Markdown")
    elif hasattr(update_or_query, "message"):
        await update_or_query.message.reply_text(text, parse_mode="Markdown")

    # Reset
    context.user_data["multi_send_counts"] = {}


# Đăng ký handler
# application.add_handler(CallbackQueryHandler(multi_send_button_handler, pattern="multi_"))
# application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number_input))
