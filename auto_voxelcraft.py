"""
====================================================================
  BOT AUTO PLAY 24/7 - VOXELCRAFT / IRON CRAFT FARM (@IronCraftFarmBot)
  Website: https://voxelcraft.online | Bot: @IronCraftFarmBot
  
  TÍNH NĂNG CHÍNH:
    - AUTO INDATA 100%: Tự động lấy init_data mới qua Telethon StringSession
      (kết nối trực tiếp @IronCraftFarmBot, chống văng token, không bao giờ hết hạn).
    - Tự động gọi /api/v1/game/summary để đồng bộ số dư, sắt và lò nung.
    - Tự động THU HOẠCH SẮT (Claim Harvest) khi mẻ nung hoàn tất:
      + Ưu tiên xem quảng cáo nhận 100% sắt không mất phí.
      + Fallback sang Fee Harvest nếu hết lượt quảng cáo.
    - Tự động BÁN SẮT (Sell Iron) đổi lấy Coin (+30 Coin/thỏi).
    - Tự động NHẬN THÀNH TÍCH (Achievements) thưởng Coin khủng:
      + Mẻ sắt đầu tiên (+100 Coin)
      + Giao dịch đầu tiên (+150 Coin)
      + Thợ nung chăm chỉ 100 sắt (+300 Coin)
      + Chủ xưởng Lv.2 (+500 Coin)
    - Tự động NÂNG CẤP LÒ NUNG (Upgrade Level) khi đủ Coin để tăng sản lượng.
    - Tự động BẮT ĐẦU MẺ NUNG MỚI (Start Run) liên tục 24/7.
    - Tự động CÀY QUẢNG CÁO COIN (Adsgram): +100 Coin/lượt, tự canh cooldown 15 phút.
    - Hỗ trợ chạy 24/7 trên GitHub Actions hoặc máy tính cá nhân.
====================================================================
"""

import time
import json
import urllib.parse
import re
import os
import uuid
import asyncio
import base64
import sqlite3
import tempfile
import requests
from datetime import datetime, timezone, timedelta
from colorama import Fore, Style, init

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.crypto import AuthKey
from telethon.tl.functions.messages import RequestWebViewRequest

init(autoreset=True)

# -----------------------------------------------------------------
#  CẤU HÌNH HỆ THỐNG
# -----------------------------------------------------------------
API_ID = 39182276
API_HASH = "f02b155d895a3a3fbf8a1cbe810b5338"

KNOWN_GOOD_STRING_SESSION = (
    "1BVtsOHIBuxmpWiBJ9hvwV9pSrzWw5U2I5Fe20Ww8l1LCk9rnsG6T6lLZEJXZE1JJC_qUH_yyWHnRoedRNI5lJYnfjRN4gyGeDrCxquDU12ZflrpCz0VLhMZx2C0LlyUCy2eHRSRE1wUCpEYZaymL0P7Z9eAHwMy4Oogewh5TqyO4x4MF6j0yTq8Zvfpv43O4aQDzErNv3GRqpx8DXBcOJIMP9yVhq-Mby5VH5J9cF-h-bJ5ws3xKjA4GY7YKjHxDt9OI-Zr7mr-V3qZy99UxJooThJj51f2RqOKhODdLh9XZQ0ygSoAd3iFAZDOPMEo8Ch5TrrzLXi2Q3N0HorIL1JfV0xoFQlY="
)

BASE_URL = "https://voxelcraft.online"
WEB_URL = "https://voxelcraft.online/"
BOT_USERNAME = "IronCraftFarmBot"

CURRENT_INIT_DATA = ""

HEADERS = {
    'Accept': '*/*',
    'Origin': BASE_URL,
    'Referer': f"{BASE_URL}/",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36',
    'Content-Type': 'application/json'
}

def log(tag, msg, color=Fore.WHITE):
    t = datetime.now().strftime("%H:%M:%S")
    print(f"[{t}] [{tag}] {color}{msg}{Style.RESET_ALL}", flush=True)

# -----------------------------------------------------------------
#  GIẢI MÃ SESSION AN TOÀN TRÊN RAM (CHỐNG LỖI MALFORMED)
# -----------------------------------------------------------------
def get_clean_string_session():
    raw = (
        os.getenv("TELEGRAM_STRING_SESSION") or
        os.getenv("TELEGRAM_SESSION_B64_ACC1") or
        os.getenv("TELEGRAM_SESSION_B64") or
        ""
    ).strip()

    if not raw:
        return KNOWN_GOOD_STRING_SESSION

    if raw.startswith("1") and 300 <= len(raw) <= 450:
        return raw

    try:
        bdata = base64.b64decode(raw)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".session") as tmp:
            tmp.write(bdata)
            tmp_path = tmp.name

        conn = sqlite3.connect(tmp_path)
        c = conn.cursor()
        c.execute("SELECT dc_id, server_address, port, auth_key FROM sessions")
        row = c.fetchone()
        conn.close()
        try: os.remove(tmp_path)
        except Exception: pass

        if row and row[3]:
            ss = StringSession()
            ss.set_dc(row[0], row[1], row[2])
            ss.auth_key = AuthKey(data=row[3])
            extracted = ss.save()
            if extracted:
                return extracted
    except Exception as e:
        log("WARN", f"Khong the trich xuat StringSession tu base64: {e}", Fore.YELLOW)

    return KNOWN_GOOD_STRING_SESSION

# -----------------------------------------------------------------
#  TỰ ĐỘNG LẤY INIT_DATA MỚI QUA TELETHON (AUTO INDATA 100%)
# -----------------------------------------------------------------
async def fetch_fresh_init_data():
    global CURRENT_INIT_DATA
    log("INIT", "Dang ket noi Telegram Telethon lay init_data moi cho VoxelCraft...", Fore.CYAN)
    session_str = get_clean_string_session()

    for attempt in range(1, 4):
        try:
            client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await client.connect()
            if not await client.is_user_authorized():
                log("WARN", f"Lan {attempt}: Session chua duoc xac thuc!", Fore.YELLOW)
                await client.disconnect()
                await asyncio.sleep(2)
                continue

            bot = await client.get_input_entity(BOT_USERNAME)
            web_view = await client(RequestWebViewRequest(
                peer=bot,
                bot=bot,
                platform="android",
                from_bot_menu=False,
                url=WEB_URL
            ))
            await client.disconnect()

            fragment = urllib.parse.urlparse(web_view.url).fragment
            params = urllib.parse.parse_qs(fragment)
            fresh = params.get("tgWebAppData", [None])[0]
            if fresh:
                CURRENT_INIT_DATA = fresh
                log("OK", "Da lay thanh cong init_data tuoi moi toanh tu Telegram!", Fore.GREEN)
                return CURRENT_INIT_DATA
        except Exception as e:
            log("WARN", f"Lan {attempt} loi Telethon ({e})", Fore.YELLOW)
            await asyncio.sleep(2)

    return CURRENT_INIT_DATA

def get_fresh_init_data_sync():
    return asyncio.run(fetch_fresh_init_data())

# -----------------------------------------------------------------
#  CÁC HÀM GỌI API GAME
# -----------------------------------------------------------------
def api_call(path, payload=None, retry_on_auth_err=True):
    global CURRENT_INIT_DATA
    if payload is None:
        payload = {}

    if not CURRENT_INIT_DATA:
        get_fresh_init_data_sync()

    payload["initData"] = CURRENT_INIT_DATA
    url = f"{BASE_URL}{path}"

    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=12)
        res = r.json()

        # Tu dong lam moi token neu het han
        if retry_on_auth_err and isinstance(res, dict) and not res.get("success"):
            err_code = str(res.get("error", {}).get("code", ""))
            if err_code in ["AUTH_EXPIRED", "AUTH_INVALID"]:
                log("REFRESH", "InitData het han, dang lay lai tu Telegram...", Fore.YELLOW)
                get_fresh_init_data_sync()
                payload["initData"] = CURRENT_INIT_DATA
                r2 = requests.post(url, json=payload, headers=HEADERS, timeout=12)
                return r2.json()

        return res
    except Exception as e:
        return {"success": False, "error": {"message": str(e)}}

def api_transact(action, input_data=None):
    if input_data is None:
        input_data = {}
    input_data["requestId"] = str(uuid.uuid4())
    return api_call(f"/api/v1/game/{action}", input_data)

def get_game_summary():
    return api_call("/api/v1/game/summary")

# -----------------------------------------------------------------
#  1. THU HOẠCH SẮT (CLAIM HARVEST)
# -----------------------------------------------------------------
def auto_claim_harvest(run_data):
    run_id = run_data.get("id")
    quantity = run_data.get("quantity", 0)
    fee_iron = run_data.get("feeIron", 1)

    log("HARVEST", f"Dang thu hoach me nung #{run_id[:8]} (+{quantity} Sat)...", Fore.CYAN)

    # 1. Thu xem quang cao de thu hoach mien phi 100%
    try:
        ad_res = api_call("/api/v1/game/ads/sessions", {
            "provider": "adsgram",
            "purpose": "harvest",
            "runId": run_id
        })
        if ad_res.get("success"):
            sess = ad_res.get("data", {})
            sess_id = sess.get("id")
            log("AD_HARVEST", f"Xem quang cao thu hoach mien phi (ID: {sess_id[:12]})...", Fore.YELLOW)
            time.sleep(3)
            comp_res = api_call(f"/api/v1/game/ads/sessions/{sess_id}/client-complete")
            if comp_res.get("success"):
                log("AD_OK", "Xac minh quang cao thu hoach thanh cong! Khong mat phi sat.", Fore.GREEN)
                c_res = api_transact("claim", {"runId": run_id})
                if c_res.get("success"):
                    log("CLAIM_OK", f"🎉 THU HOACH THANH CONG TRON VEN +{quantity} THOI SAT!", Fore.GREEN)
                    return True
    except Exception as e:
        log("WARN", f"Quang cao thu hoach khong kha dung: {e}", Fore.YELLOW)

    # 2. Neu khong co quang cao -> Thu hoach tru phi nho (Fee Harvest)
    log("FEE_HARVEST", f"Thu hoach qua mẻ phí (Trừ {fee_iron} sắt phí)...", Fore.CYAN)
    c_res = api_transact("claim", {
        "runId": run_id,
        "method": "fee",
        "feeIron": fee_iron
    })
    if c_res.get("success"):
        net = quantity - fee_iron
        log("CLAIM_OK", f"🎉 THU HOACH THANH CONG +{net} THOI SAT (Da tru {fee_iron} sat phi)!", Fore.GREEN)
        return True
    else:
        err = c_res.get("error", {}).get("message", "")
        log("CLAIM_FAIL", f"Chua the thu hoach: {err}", Fore.RED)
        return False

# -----------------------------------------------------------------
#  2. BÁN SẮT LẤY COIN (SELL IRON)
# -----------------------------------------------------------------
def auto_sell_iron(iron_quantity):
    if iron_quantity <= 0:
        return
    log("SELL", f"Tien hanh doi {iron_quantity} thoi sat lay Coin (+{iron_quantity * 30} Coins)...", Fore.CYAN)
    res = api_transact("sell", {
        "quantity": iron_quantity,
        "source": "warehouse"
    })
    if res.get("success"):
        st = res.get("data", {}).get("state", {})
        earned = st.get("lastSale", iron_quantity * 30)
        total_coins = st.get("coins", 0)
        log("SELL_OK", f"💰 BAN SAT THANH CONG! Nhan +{earned:,} Coin | Tong Coin vi: {total_coins:,}", Fore.GREEN)
    else:
        err = res.get("error", {}).get("message", "")
        log("SELL_ERR", f"Khong the ban sat: {err}", Fore.YELLOW)

# -----------------------------------------------------------------
#  3. TỰ ĐỘNG BẬT MẺ NUNG MỚI (START RUN 2H)
# -----------------------------------------------------------------
def auto_start_run():
    log("START", "Bat dau me nung sat moi trong lo...", Fore.CYAN)
    res = api_transact("start")
    if res.get("success"):
        st = res.get("data", {}).get("state", {})
        run = st.get("run", {})
        qty = run.get("quantity", 8)
        log("START_OK", f"🔥 DA KHOI DONG ME NUNG MOI! San luong du kien: {qty} thoi sat.", Fore.GREEN)
        return run
    else:
        err = res.get("error", {}).get("message", "")
        log("START_WARN", f"Chua the khoi dong me nung: {err}", Fore.YELLOW)
        return None

# -----------------------------------------------------------------
#  4. NHẬN THƯỞNG THÀNH TÍCH (ACHIEVEMENTS)
# -----------------------------------------------------------------
ACHIEVEMENT_LIST = [
    ("factory_first_haul", "Mẻ sắt đầu tiên", 100),
    ("factory_first_sale", "Giao dịch đầu tiên", 150),
    ("factory_100_iron", "Thợ nung chăm chỉ", 300),
    ("factory_level_2", "Chủ xưởng cấp 2", 500),
    ("factory_level_3", "Nhà máy phát triển", 750)
]

def auto_claim_achievements(state):
    claimed = state.get("claimedAchievements", [])
    total_iron = state.get("totalIron", 0)
    total_sold = state.get("totalSold", 0)
    level = state.get("level", 1)

    for a_id, name, reward in ACHIEVEMENT_LIST:
        if a_id in claimed:
            continue
        
        eligible = False
        if a_id == "factory_first_haul" and total_iron >= 10:
            eligible = True
        elif a_id == "factory_first_sale" and total_sold >= 10:
            eligible = True
        elif a_id == "factory_100_iron" and total_iron >= 100:
            eligible = True
        elif a_id == "factory_level_2" and level >= 2:
            eligible = True
        elif a_id == "factory_level_3" and level >= 3:
            eligible = True

        if eligible:
            log("ACHIEVE", f"Phat hien thanh tich [{name}] hoan tat! Dang nhan +{reward} Coin...", Fore.MAGENTA)
            res = api_transact("achievement", {"goalId": a_id})
            if res.get("success"):
                log("ACHIEVE_OK", f"🎉 Nhan thanh cong thanh tich [{name}] (+{reward} Coin)!", Fore.GREEN)
            else:
                log("ACHIEVE_WARN", f"Chua nhan duoc: {res.get('error', {}).get('message')}", Fore.YELLOW)

# -----------------------------------------------------------------
#  5. NÂNG CẤP LÒ NUNG (UPGRADE FACTORY)
# -----------------------------------------------------------------
def auto_upgrade_factory(state, economy):
    phase = state.get("phase")
    coins = state.get("coins", 0)
    level = state.get("level", 1)

    if phase not in ["idle", "haul"]:
        return

    first_cost = economy.get("firstUpgradeCost", 500)
    later_cost = economy.get("laterUpgradeCost", 1600)
    cost = first_cost if level == 1 else later_cost

    if coins >= cost:
        log("UPGRADE", f"Du Coin! Dang nang cap Nha may len Cap {level + 1} (Chi phi: {cost:,} Coin)...", Fore.MAGENTA)
        res = api_transact("upgrade", {"level": level})
        if res.get("success"):
            new_lvl = res.get("data", {}).get("state", {}).get("level", level + 1)
            log("UPGRADE_OK", f"⭐ NHA MAY DA DUOC NANG CAP LEN CAP {new_lvl} THANH CONG!", Fore.GREEN)
        else:
            log("UPGRADE_WARN", f"Chua the nang cap: {res.get('error', {}).get('message')}", Fore.YELLOW)

# -----------------------------------------------------------------
#  6. CÀY QUẢNG CÁO KIẾM COIN (ADSGRAM)
# -----------------------------------------------------------------
def auto_watch_coin_ads(ad_config):
    daily_limit = ad_config.get("coinLimit", 6)
    used = ad_config.get("coinUsed", 0)
    reward = ad_config.get("rewardCoins", 100)

    if used >= daily_limit:
        return 900

    log("ADS", f"Tien do xem Ads kiem Coin: {used}/{daily_limit} | Dang xem 1 luot (+{reward} Coin)...", Fore.CYAN)
    sess_res = api_call("/api/v1/game/ads/sessions", {
        "provider": "adsgram",
        "purpose": "coin"
    })

    if not sess_res.get("success"):
        err = sess_res.get("error", {}).get("message", "")
        log("ADS_COOLDOWN", f"Quang cao dang cho: {err}", Fore.WHITE)
        return 900

    sess = sess_res.get("data", {})
    sess_id = sess.get("id")
    time.sleep(15)

    comp_res = api_call(f"/api/v1/game/ads/sessions/{sess_id}/client-complete")
    if comp_res.get("success"):
        log("ADS_OK", f"🎉 Xem xong quang cao! Nhan thanh cong +{reward} Coin vao vi!", Fore.GREEN)
        get_game_summary()
        return 900
    else:
        log("ADS_ERR", f"Loi hoan tat quang cao: {comp_res.get('error')}", Fore.YELLOW)
        return 900

# -----------------------------------------------------------------
#  VÒNG LẶP CHÍNH 24/7
# -----------------------------------------------------------------
def run_loop():
    print(Fore.CYAN + """
====================================================================
      BOT AUTO VOXELCRAFT / IRON CRAFT FARM 24/7 ĐANG CHẠY
====================================================================
|  - TU DONG LAY INIT_DATA MOI QUA TELETHON (AUTO INDATA 100%)    |
|  - TU DONG NUNG SAT 2 TIENG/ME, THU HOACH MIEN PHI 100%         |
|  - TU DONG BAN SAT DOI COIN (+30 COIN / THOI)                    |
|  - TU DONG NHAN THUONG THANH TICH & NANG CAP NHA MAY            |
|  - TU DONG CAY ADS COIN (+100 COIN/LUOT) THEO COOLDOWN           |
====================================================================
    """ + Style.RESET_ALL)

    get_fresh_init_data_sync()

    cycle = 1
    last_refresh_init_time = time.time()

    while True:
        log("CYCLE", f"--- CHU KY #{cycle} ---", Fore.CYAN)

        try:
            sum_res = get_game_summary()
            if not sum_res.get("success"):
                log("WARN", f"Khong the lay summary: {sum_res.get('error')}", Fore.YELLOW)
                time.sleep(10)
                continue

            data = sum_res.get("data", {})
            state = data.get("state", {})
            economy = data.get("economy", {})
            ad_config = data.get("adConfig", {})
            server_now = data.get("serverNow", int(time.time() * 1000))

            phase = state.get("phase")
            coins = state.get("coins", 0)
            iron = state.get("iron", 0)
            level = state.get("level", 1)
            run = state.get("run")

            log("STATUS", f"Nha may Lv.{level} | Trang thai: [{phase.upper()}] | Sat: {iron} thoi | Vi: {coins:,} Coin (~{coins*5/1000:,.1f} VND)", Fore.GREEN)

            # 2. Tu dong kiem tra va nhan thanh tich
            auto_claim_achievements(state)

            # 3. Xu ly theo tung trang thai cua lo nung:
            if phase == "ready" and run:
                auto_claim_harvest(run)
                fresh_sum = get_game_summary().get("data", {}).get("state", {})
                if fresh_sum.get("iron", 0) > 0:
                    auto_sell_iron(fresh_sum.get("iron", 0))

            elif phase == "haul" and iron > 0:
                auto_sell_iron(iron)

            elif phase == "idle":
                auto_upgrade_factory(state, economy)
                if iron > 0:
                    auto_sell_iron(iron)
                run = auto_start_run()

            elif phase == "running" and run:
                ends_at = run.get("endsAt", 0)
                rem_sec = max(0, int((ends_at - server_now) / 1000))
                mins, secs = divmod(rem_sec, 60)
                log("RUNNING", f"Me nung dang chay, du kien xong sau {mins}m {secs}s...", Fore.YELLOW)
                if rem_sec <= 0:
                    get_game_summary()

            # 4. Kiem tra xem quang cao kiem Coin neu co
            auto_watch_coin_ads(ad_config)

            # 5. Lam moi init_data dinh ky sau moi 60 phut
            if time.time() - last_refresh_init_time > 3600:
                log("REFRESH", "Lam moi init_data tu Telegram...", Fore.MAGENTA)
                get_fresh_init_data_sync()
                last_refresh_init_time = time.time()

        except Exception as e:
            log("ERR", f"Loi trong chu ky: {e}", Fore.RED)

        cycle += 1
        time.sleep(30)

if __name__ == "__main__":
    run_loop()
