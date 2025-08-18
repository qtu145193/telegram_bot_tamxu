from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from web3 import Web3
from datetime import datetime, timedelta
from collections import defaultdict

w3 = Web3(Web3.HTTPProvider("https://rpc5.viction.xyz/"))  # Thay URL node

transfer_event_sig = w3.keccak(text="Transfer(address,address,uint256)").hex()
TOKEN_CONTRACT = "0x39dda3a886196148a7f295E1876BdfBE1424D147".lower()

async def pool_token_txns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = context.bot_data.get("rows", [])
    pool_rows = [r for r in rows if "pool" in r["Tên"].lower()]
    if not pool_rows:
        await update.message.reply_text("❌ Không có pool nào.")
        return

    buttons = [
        [InlineKeyboardButton(r["Tên"], callback_data=f"pool_txns|{r['Viction Address']}")]
        for r in pool_rows
    ]

    await update.message.reply_text(
        "📌 Chọn pool để xem token transactions hôm nay:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def pool_txns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pool_address = query.data.split("|")[1].lower()

    # Lấy ngày hôm nay UTC để lọc txns theo timestamp
    date_to_check = datetime.utcnow().date()
    start_ts = int(datetime.combine(date_to_check, datetime.min.time()).timestamp())
    end_ts = int(datetime.combine(date_to_check + timedelta(days=1), datetime.min.time()).timestamp())

    params = {
        "module": "account",
        "action": "tokentx",
        "address": pool_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": API_KEY
    }

    resp = requests.get(BSCSCAN_API_URL, params=params)
    data = resp.json()

    txns_today = []
    for tx in data.get("result", []):
        # Lọc theo timestamp trong ngày
        ts = int(tx["timeStamp"])
        if not (start_ts <= ts < end_ts):
            continue
        # Lọc theo contract token
        if tx["contractAddress"].lower() != TOKEN_CONTRACT:
            continue
        txns_today.append(tx)

    if not txns_today:
        await query.edit_message_text("❌ Không có giao dịch token hôm nay gửi tới pool.")
        return

    lines = [f"💸 Token transactions hôm nay gửi tới pool {pool_address}:\n"]
    for tx in txns_today:
        token_symbol = tx["tokenSymbol"]
        token_name = tx["tokenName"]
        decimals = int(tx["tokenDecimal"])
        value = int(tx["value"]) / (10 ** decimals)
        from_addr = tx["from"]
        lines.append(f"- Từ {from_addr}: {value:.4f} {token_symbol}")

    await query.edit_message_text("\n".join(lines))