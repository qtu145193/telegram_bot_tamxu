# dice3_bot.py
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


async def roll3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # chat_id = update.effective_chat.id

    # dice_values = []
    # for _ in range(3):
    #     sent = await context.bot.send_dice(chat_id=chat_id, emoji="🎲")
    #     dice_values.append(sent)
    #     await asyncio.sleep(1.2)  # đợi animation cho đẹp

    # values = [d.dice.value for d in dice_values if d.dice]
    # total = sum(values)

    # await update.message.reply_text(f"🎲 Kết quả: {values} → Tổng = {total}")
    await update.message.reply_text(f"Đừng nghiện nữa bạn ơi!!!!!")


async def roll3_cham(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    dice_values = []
    for _ in range(3):
        sent = await context.bot.send_dice(chat_id=chat_id, emoji="🎲")
        dice_values.append(sent)
        
        # Nếu có animation_duration (tùy phiên bản thư viện), dùng nó
        duration = getattr(sent.dice, "animation_duration", 4)  # thường 4s
        await asyncio.sleep(duration + 0.5)  # chờ hẳn xong mới lắc tiếp

    values = [d.dice.value for d in dice_values if d.dice]
    total = sum(values)

    await update.message.reply_text(f"🎲 Kết quả: {values} → Tổng = {total}")