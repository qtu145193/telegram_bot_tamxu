from telegram import Update
from telegram.ext import ContextTypes
from ..utils.web3_utils import get_token_balance
from ..utils.format_utils import format_compact

token_address = '0x39dda3a886196148a7f295E1876BdfBE1424D147'
token_symbol = 'CHIP'
base_value = 10_000_000

async def check_result(update: Update, context: ContextTypes.DEFAULT_TYPE, w3):
    rows = context.bot_data.get("rows", [])
    if not rows:
        await update.message.reply_text("Không có dữ liệu.")
        return

    token_address = context.bot_data.get("token_address")
    token_symbol = context.bot_data.get("token_symbol", "CHIP")
    # Default base = 10,000,000 (10M) — thay nếu bạn đã set khác trong context.bot_data
    base_value = int(context.bot_data.get("base_value", 10_000_000))

    results = []
    errors = []

    for row in rows:
        try:
            name = row.get("Tên", "").strip()
            if not name:
                continue
            # nếu vẫn muốn bỏ pool thì giữ dòng dưới, nếu không muốn bỏ thì xóa dòng này
            if "pool" in name.lower():
                continue

            address = row.get("AdViction Addressdress", "").strip()
            balance = get_token_balance(w3, token_address, address) or 0
            balance = int(balance)
            diff = balance - base_value

            # ẩn nếu diff == 0
            if diff == 0:
                continue

            results.append({
                "name": name,
                "address": address,
                "balance": balance,
                "diff": diff
            })
        except Exception as e:
            errors.append(f"{row.get('Tên')} ({row.get('Viction Address')}): {str(e)}")

    positives = [r for r in results if r["diff"] > 0]
    negatives = [r for r in results if r["diff"] < 0]

    # sort: positives theo diff giảm dần (ai hơn 10M nhiều nhất lên đầu)
    positives.sort(key=lambda r: r["diff"], reverse=True)
    # negatives theo diff tăng dần (ví dụ: -5M, -3M, -1M) => người lỗ nặng nhất lên trước
    negatives.sort(key=lambda r: r["diff"])

    # gán huy chương cho top3 theo diff
    medals = ["🥇", "🥈", "🥉"]
    for i, r in enumerate(positives[:3]):
        r["medal"] = medals[i]

    lines = []

    if positives:
        lines.append(f"*📈 DƯƠNG (so với {format_compact(base_value)}):*")
        lines.append("```")
        lines.append("Name            Balance     Change")
        lines.append("----------------------------------")
        for r in positives:
            icon = r.get("medal", "👑")
            name = r["name"][:14].ljust(14)
            bal = format_compact(r["balance"]).rjust(8)
            change = ("+" + format_compact(r["diff"])).rjust(8)
            lines.append(f"{icon} {name}  {bal} {token_symbol}  {change}")
        lines.append("```")

    if negatives:
        lines.append(f"*📉 ÂM (so với {format_compact(base_value)}):*")
        lines.append("```")
        lines.append("Name            Balance     Change")
        lines.append("----------------------------------")
        for r in negatives:
            name = r["name"][:14].ljust(14)
            bal = format_compact(r["balance"]).rjust(8)
            change = format_compact(r["diff"]).rjust(8)  # negative already has '-' from format_compact
            lines.append(f"💀 {name}  {bal} {token_symbol}  {change}")
        lines.append("```")

    if not lines:
        lines.append(f"✅ Tất cả bằng {format_compact(base_value)}")

    # lỗi nếu có
    if errors:
        lines.append("\n*⚠️ LỖI:*")
        lines.extend(errors)

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def refund(update: Update, context: ContextTypes.DEFAULT_TYPE, w3):
    rows = context.bot_data.get("rows", [])

    output_lines = []
    names = []
    for row in rows:
        name = row.get("Tên", "")
        if "pool" in name.lower():
            continue
        address = row.get("Viction Address", "")
        balance = get_token_balance(w3, token_address, address)
        if balance < base_value:
            amount_needed = base_value - balance
            output_lines.append(f"{address}?{amount_needed}")
            names.append(name)

    if not output_lines:
        text = "✅ Không ai bị âm."
    else:
        text = f"📤 Refund cho: {', '.join(names)}\n" + ";".join(output_lines)

    await update.message.reply_text(text, parse_mode="Markdown")
