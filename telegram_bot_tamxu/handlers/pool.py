from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from pathlib import Path

# Hàm khởi tạo
async def pool_to_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = context.bot_data.get("rows", [])
    names = [row["Name"] for row in rows if "pool" not in row.get("Name", "").lower()]
    context.user_data["pool_counts"] = {name: 0 for name in names}
    await send_pool_buttons(update, context.user_data["pool_counts"])


# Hàm gửi/refresh nút bấm
async def send_pool_buttons(update_or_query, pool_counts):
    keyboard = []

    for name, count in pool_counts.items():
        row = [
            InlineKeyboardButton(f"➖", callback_data=f"pool_sub|{name}"),
            InlineKeyboardButton(f"{name}:{count}", callback_data="noop"),
            InlineKeyboardButton(f"➕", callback_data=f"pool_add|{name}")
        ]
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("✅ Done", callback_data="pool_done")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_query, "message"):
        await update_or_query.message.reply_text("📋 *Nghiện Làm Lại Cuộc Đời:*", reply_markup=reply_markup, parse_mode="Markdown")
    elif hasattr(update_or_query, "edit_message_reply_markup"):
        await update_or_query.edit_message_reply_markup(reply_markup=reply_markup)


# Handler cho các nút
async def pool_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    pool_counts = context.user_data.get("pool_counts", {})

    if "|" in data:
        action, name = data.split("|")

        if action == "pool_add":
            pool_counts[name] = pool_counts.get(name, 0) + 1
        elif action == "pool_sub":
            pool_counts[name] = max(pool_counts.get(name, 0) - 1, 0)

        context.user_data["pool_counts"] = pool_counts

        # Tạo bàn phím mới
        keyboard = []
        for n, count in pool_counts.items():
            keyboard.append([
                InlineKeyboardButton(f"➖ ", callback_data=f"pool_sub|{n}"),
                InlineKeyboardButton(f"{n}:{count}", callback_data="noop"),
                InlineKeyboardButton(f"➕", callback_data=f"pool_add|{n}")
            ])
        keyboard.append([InlineKeyboardButton("✅ Done", callback_data="pool_done")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_reply_markup(reply_markup=reply_markup)

    elif data == "pool_done":
        await send_pool_report(update, context)



# Gửi báo cáo cuối cùng
async def send_pool_report(update_or_query, context):
    pool_counts = context.user_data.get("pool_counts", {})
    reply_lines = ["💸 *Pool Today:*\n"]

    for name, count in pool_counts.items():
        if count > 0:
            reply_lines.append(f"💰 {name.ljust(15)} {count} Tụ")

    text = "\n".join(reply_lines) if len(reply_lines) > 1 else "❌ Không ai được chia tụ hôm nay."

    try:
        if hasattr(update_or_query, "callback_query") and update_or_query.callback_query:
            await update_or_query.callback_query.edit_message_text(text, parse_mode="Markdown")
        elif hasattr(update_or_query, "message") and update_or_query.message:
            await update_or_query.message.reply_text(text, parse_mode="Markdown")
        else:
            chat_id = getattr(update_or_query.effective_chat, "id", None)
            if chat_id:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
            else:
                print("⚠️ Không tìm thấy chat_id để gửi báo cáo")
    except Exception as e:
        print("⚠️ Gửi báo cáo lỗi:", str(e))

    # Reset
    context.user_data["pool_counts"] = {}


# Hiển thị nút pool
async def show_pool_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = context.bot_data.get("rows", [])
    if not rows:
        await update.message.reply_text("❌ Không có dữ liệu từ sheet.")
        return

    buttons = [
        [InlineKeyboardButton(row["Name"], callback_data=f"pool_{row['Address']}")]
        for row in rows if "pool" in row["Name"].lower()
    ]

    if not buttons:
        await update.message.reply_text("❌ Không có pool nào.")
        return

    await update.message.reply_text(
        "📌 Chọn pool để xem QR code:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# Xử lý khi click nút
async def show_pool_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    address = query.data.replace("pool_", "").strip()
    await query.message.reply_text(f"{address}: Đang tìm")

    rows = context.bot_data.get("rows", [])
    matched_row = next((row for row in rows if row["Address"].strip().lower() == address.lower()), None)

    if matched_row:
        name = matched_row["Name"]
        image_path = Path("D:/GitTool/bot_telegram/bot_telegram/img") / f"{address}.jpg"
        print(f"[DEBUG] Đường dẫn ảnh: {image_path}")

        if not image_path.exists():
            await query.message.reply_text(f"❌ Không tìm thấy dữ liệu")
            return

        try:
            with open(image_path, "rb") as img:
                await query.message.reply_photo(
                    photo=img,
                    caption=f"💸 Pool Info:\n👤 {name}\n🏦 {address}"
                )
        except Exception as e:
            await query.message.reply_text(f"⚠ Lỗi khi gửi ảnh: {e}")
    else:
        await query.message.reply_text("❌ Không tìm thấy dữ liệu.")

