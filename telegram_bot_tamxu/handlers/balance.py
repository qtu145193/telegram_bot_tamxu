from telegram import Update
from telegram.ext import ContextTypes
from ..utils.web3_utils import get_token_balance
from ..utils.format_utils import format_compact

token_address = '0x39dda3a886196148a7f295E1876BdfBE1424D147'
token_symbol = 'CHIP'
base_value = 10_000_000


async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE, w3):
    rows = context.bot_data.get("rows", [])
    if not rows:
        await update.message.reply_text("Không có dữ liệu nào.")
        return

    results = []
    for row in rows:
        # Ensure row is a dict
        if not isinstance(row, dict):
            continue

        # Try multiple possible header variants
        name = row.get("Tên") or row.get("Ten") or row.get("Name") or "Unknown"
        if "pool" in name.lower():
            continue

        address = row.get("Viction Address") or row.get("Address") or ""
        try:
            balance = get_token_balance(w3, token_address, address)
            diff = balance - base_value
            results.append({
                "name": name,
                "address": address,
                "balance": balance,
                "diff": diff
            })
        except Exception as e:
            results.append({
                "name": name,
                "address": address,
                "error": str(e)
            })

    # Split results
    win_results = [r for r in results if 'error' not in r and r['diff'] >= 0]
    lose_results = [r for r in results if 'error' not in r and r['diff'] < 0]
    error_results = [r for r in results if 'error' in r]

    # Add medals
    win_results.sort(key=lambda r: r['balance'], reverse=True)
    medals = ['🥇', '🥈', '🥉']
    for i, r in enumerate(win_results[:3]):
        r['medal'] = medals[i]

    # Format WIN table
    win_lines = [
        "*👑 NGÀI:*",
        "```",
        "Name            Balance     Change",
        "----------------------------------"
    ]
    for r in win_results:
        icon = r.get('medal', '👑')
        name = r['name'][:14].ljust(14)
        balance = format_compact(r['balance']).rjust(8)
        change = ("+" + format_compact(r['diff'])).rjust(8)
        win_lines.append(f"{icon} {name}  {balance}  {change}")
    win_lines.append("```")

    # Format LOSE table
    lose_results.sort(key=lambda r: r['balance'])
    lose_lines = [
        "*💀 NGHIỆN:*",
        "```",
        "Name            Balance     Change",
        "----------------------------------"
    ]
    for r in lose_results:
        name = r['name'][:14].ljust(14)
        balance = format_compact(r['balance']).rjust(8)
        change = format_compact(r['diff']).rjust(8)
        lose_lines.append(f"💀 {name}  {balance}  {change}")
    lose_lines.append("```")

    # Send messages
    if win_results:
        await update.message.reply_text("\n".join(win_lines), parse_mode="Markdown")
    if lose_results:
        await update.message.reply_text("\n".join(lose_lines), parse_mode="Markdown")


async def check_pool(update: Update, context: ContextTypes.DEFAULT_TYPE, w3):
    rows = context.bot_data.get("rows", [])
    if not rows:
        await update.message.reply_text("Không có dữ liệu.")
        return

    reply_lines = ["*💸 Pool Result Today:*"]

    for row in rows:
        try:
            name = row['Tên']
            if "pool" not in name.lower():
                continue

            user_address = row['Viction Address']
            token_balance = get_token_balance(w3, token_address, user_address)

            formatted_balance = format_compact(token_balance)

            name_fmt = name.ljust(15)
            bal_fmt = f"{formatted_balance} {token_symbol}".ljust(17)

            line = f"💰 {name_fmt} {bal_fmt}"
            reply_lines.append(line)

        except Exception as e:
            reply_lines.append(f"{row.get('Tên')} ({row.get('Viction Address')}): ❌ Lỗi: {str(e)}")

    await update.message.reply_text("\n".join(reply_lines), parse_mode="Markdown")
