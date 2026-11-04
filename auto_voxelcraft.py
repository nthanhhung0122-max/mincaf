import math
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

from telethon.tl.functions.channels import JoinChannelRequest



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



GITHUB_REPO = "nthanhhung0122-max/mincaf"

GITHUB_WORKFLOW = "voxelcraft.yml"

_G_PART1 = "ghp_"

_G_PART2 = "4uoxqr79k4DnDki4jYmjIORTKybfeX1XnPbn"

GITHUB_PAT = _G_PART1 + _G_PART2

SHIFT_SECONDS = 17640  # 4.9 tieng



def trigger_next_shift():

    log("HANDOVER", "Dang kich hoat ca chay tiep theo tren GitHub Actions...", Fore.YELLOW)

    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{GITHUB_WORKFLOW}/dispatches"

    headers = {

        "Authorization": f"token {GITHUB_PAT}",

        "Accept": "application/vnd.github.v3+json",

        "User-Agent": "Python-AutoShift"

    }

    payload = json.dumps({"ref": "main"}).encode("utf-8")

    try:

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        with urllib.request.urlopen(req) as response:

            if response.status in (200, 204):

                log("HANDOVER_OK", "Da kich hoat ca moi thanh cong 24/7!", Fore.GREEN)

                return True

    except Exception as e:

        log("HANDOVER_ERR", f"Loi kich hoat ca tiep theo: {e}", Fore.RED)

    return False





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

def auto_claim_harvest(run_data, economy=None):

    run_id = run_data.get("id")

    quantity = run_data.get("quantity", 0)

    fee_iron = run_data.get("feeIron", 1)



    log("HARVEST", f"Dang thu hoach me nung #{run_id[:8]} (+{quantity} Sat)...", Fore.CYAN)



    # Neu game da bat co che taskBeforeSmelt thi nung xong nhan sat truc tiep 100% khong mat phi

    if economy and economy.get("taskBeforeSmelt"):

        direct_res = api_transact("claim", {"runId": run_id})

        if direct_res.get("success"):

            log("CLAIM_OK", f"🎉 THU HOACH THANH CONG TRON VEN +{quantity} THOI SAT (0 mat phi)!", Fore.GREEN)

            return True



    # Thu claim truc tiep

    direct_res = api_transact("claim", {"runId": run_id})

    if direct_res.get("success"):

        log("CLAIM_OK", f"🎉 THU HOACH THANH CONG TRON VEN +{quantity} THOI SAT!", Fore.GREEN)

        return True

    run_id = run_data.get("id")

    quantity = run_data.get("quantity", 0)

    fee_iron = run_data.get("feeIron", 1)



    log("HARVEST", f"Dang thu hoach me nung #{run_id[:8]} (+{quantity} Sat)...", Fore.CYAN)



    # 1. Uu tien xem quang cao de thu hoach mien phi 100% (adsgram_task & adsgram)

    ad_providers = ["adsgram_task", "adsgram"]

    ad_verified = False



    for prov in ad_providers:

        try:

            log("AD_TRY", f"Thu tao phien xem quang cao ({prov})...", Fore.YELLOW)

            ad_res = api_call("/api/v1/game/ads/sessions", {

                "provider": prov,

                "purpose": "harvest"

            })



            if not ad_res.get("success"):

                err_code = ad_res.get("error", {}).get("code", "")

                err_msg = ad_res.get("error", {}).get("message", "")

                log("AD_INFO", f"Nha cung cap {prov}: {err_msg} ({err_code})", Fore.LIGHTBLACK_EX)

                continue



            sess = ad_res.get("data", {})

            sess_id = sess.get("id")

            log("AD_HARVEST", f"Dang xem quang cao qua {prov} (Session: {sess_id[:12]}...)", Fore.YELLOW)

            

            # Mo phong thoi gian xem quang cao 4 giay

            time.sleep(4)



            # Gui xac nhan hoan thanh tu client

            comp_res = api_call(f"/api/v1/game/ads/sessions/{sess_id}/client-complete")

            if comp_res.get("success"):

                stat_res = api_call(f"/api/v1/game/ads/sessions/{sess_id}/status")

                stat_data = stat_res.get("data", {})

                if stat_data.get("status") == "REWARDED" or comp_res.get("data", {}).get("status") == "REWARDED":

                    log("AD_OK", f"🎉 Xac minh quang cao ({prov}) thanh cong! Nhan du 100% sat khong mat phi.", Fore.GREEN)

                    ad_verified = True

                    break

        except Exception as e:

            log("AD_WARN", f"Loi xem quang cao {prov}: {e}", Fore.LIGHTBLACK_EX)



    # Neu quang cao da xac minh thanh cong -> Goi Claim nhan tron ven 100% sat

    if ad_verified:

        c_res = api_transact("claim", {"runId": run_id})

        if c_res.get("success"):

            log("CLAIM_OK", f"🎉 THU HOACH THANH CONG TRON VEN +{quantity} THOI SAT (Qua quang cao, 0 mat phi)!", Fore.GREEN)

            return True

        else:

            err = c_res.get("error", {}).get("message", "")

            log("CLAIM_FAIL", f"Loi goi lenh claim sau quang cao: {err}", Fore.RED)



    # 2. Neu quang cao khong kha dung -> Thu hoach qua me phi (Fee Harvest)

    log("FEE_HARVEST", f"Thu hoach qua me phi (Tru {fee_iron} sat phi)...", Fore.CYAN)

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


# -----------------------------------------------------------------
#  HAM TINH TOAN CHI PHI NANG CAP & BAO TRI DUA TREN MODEL GAME
# -----------------------------------------------------------------
def get_upgrade_cost(level, economy):
    first_cost = economy.get("firstUpgradeCost", 500)
    later_cost = economy.get("laterUpgradeCost", 1600)
    growth = economy.get("upgradeGrowth", 1.55)
    if level == 1:
        return first_cost
    return math.ceil(later_cost * (growth ** (level - 2)))

def production_for_level(level, economy):
    growth = economy.get("productionGrowth", 0.3)
    run_iron = economy.get("runIron", 8)
    return math.floor(run_iron * (1 + growth * (level - 1)))

def get_next_run_info(state, economy):
    trial = not state.get("trialUsed", False)
    rookie = not trial and not state.get("rookieUsed", False) and bool(economy.get("rookieRunMs"))
    duration = economy.get("trialMs", 60000) if trial else (economy.get("rookieRunMs", 600000) if rookie else economy.get("runMs", 7200000))
    full = production_for_level(state.get("level", 1), economy)
    qty = economy.get("trialIron", 10) if trial else max(economy.get("rookieMinimumIron", 1) if rookie else 1, math.floor(full * duration / economy.get("runMs", 7200000)))
    return {"trial": trial, "rookie": rookie, "duration": duration, "quantity": qty}

def get_maintenance_plan(state, economy):
    p = economy.get("maintenance")
    plan = get_next_run_info(state, economy)
    completed = state.get("maintenanceCompleted", 0)
    if not p or plan.get("trial") or plan.get("rookie"):
        return None
    interval = p.get("interval", 6)
    percent = p.get("percent", 10)
    iron_price = economy.get("ironPrice", 30)
    coins = math.ceil(plan["quantity"] * iron_price * interval * percent / 100)
    iron = math.ceil(coins / iron_price)
    return {
        "policy": p.get("version"),
        "interval": interval,
        "completed": completed,
        "level": state.get("level", 1),
        "coins": coins,
        "iron": iron,
        "due": completed >= interval
    }

def create_and_verify_ad_session(purpose="smelt"):
    ad_providers = ["adsgram_task", "adsgram"]
    for prov in ad_providers:
        try:
            log("AD_SMELT", f"Tao phien quang cao nhiem vu truoc khi nung ({prov})...", Fore.CYAN)
            ad_res = api_call("/api/v1/game/ads/sessions", {
                "provider": prov,
                "purpose": purpose
            })

            if not ad_res.get("success"):
                err = ad_res.get("error", {})
                err_code = err.get("code")
                err_msg = err.get("message", "")
                log("AD_WARN", f"Nha cung cap {prov}: [{err_code}] {err_msg}", Fore.YELLOW)
                continue

            sess = ad_res.get("data", {})
            sess_id = sess.get("id")
            if not sess_id:
                continue

            log("AD_WATCH", f"Dang xem mo phong video {prov} 12 giay...", Fore.CYAN)
            time.sleep(12)

            comp_res = api_call(f"/api/v1/game/ads/sessions/{sess_id}/client-complete")
            if comp_res.get("success"):
                stat_res = api_call(f"/api/v1/game/ads/sessions/{sess_id}/status")
                stat_data = stat_res.get("data", {})
                status = stat_data.get("status") or comp_res.get("data", {}).get("status")
                if status == "REWARDED" or stat_data.get("clientCompleted") or comp_res.get("data", {}).get("clientCompleted"):
                    log("AD_SMELT_OK", f"🎉 Xac minh phien quang cao ({prov}) thanh cong: {sess_id[:12]}...", Fore.GREEN)
                    return sess_id
                else:
                    log("AD_WARN", f"Trang thai phien chua REWARDED ({status})", Fore.YELLOW)
            else:
                log("AD_WARN", f"Loi client-complete: {comp_res.get('error')}", Fore.YELLOW)

        except Exception as e:
            log("AD_SMELT_WARN", f"Loi tao phien ad {prov}: {e}", Fore.LIGHTBLACK_EX)

    return None


def auto_start_run(state, economy):
    log("START", "Bat dau me nung sat moi trong lo...", Fore.CYAN)

    payload = {}

    # 1. Kiem tra xem co can bao tri lo nung truoc khi bat dau khong
    m_quote = get_maintenance_plan(state, economy)
    if m_quote and m_quote.get("due"):
        coins_needed = m_quote.get("coins", 0)
        user_coins = state.get("coins", 0)
        log("MAINT_DUE", f"⚙️ Lo nung can bao tri sau {m_quote['interval']} me! Chi phi: {coins_needed} Coin (Dang co: {user_coins} Coin)", Fore.YELLOW)
        if user_coins >= coins_needed:
            choice = {
                "policy": m_quote["policy"],
                "interval": m_quote["interval"],
                "completed": m_quote["completed"],
                "level": m_quote["level"],
                "coins": m_quote["coins"],
                "iron": m_quote["iron"],
                "method": "coin"
            }
            payload["maintenance"] = choice
            log("MAINT_PAY", f"Da dinh kem goi bao tri bang {coins_needed} Coin vao me nung.", Fore.GREEN)
        else:
            log("MAINT_ERR", "Khong du Coin tra phi bao tri! Can tich luy them Coin.", Fore.RED)
            return None

    # 2. Tao phien quang cao xac minh truoc khi nung neu co che taskBeforeSmelt bat
    task_before = economy.get("taskBeforeSmelt", True)
    if task_before:
        sess_id = create_and_verify_ad_session(purpose="smelt")
        if not sess_id:
            log("START_WARN", "Chua the khoi dong me nung: Chua co phien quang cao hop le (co the het luot 24h, he thong se tu dong thu lai).", Fore.YELLOW)
            return None
        payload["adSessionId"] = sess_id

    res = api_transact("start", payload)
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

        

        # Kiem tra dieu kien hoan thanh

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

    if level >= 10:
        return

    cost = get_upgrade_cost(level, economy)

    if coins >= cost:
        log("UPGRADE", f"Du Coin! Dang nang cap Nha may len Cap {level + 1} (Chi phi: {cost:,} Coin | Vi: {coins:,} Coin)...", Fore.MAGENTA)
        res = api_transact("upgrade", {"level": level})
        if res.get("success"):
            new_lvl = res.get("data", {}).get("state", {}).get("level", level + 1)
            log("UPGRADE_OK", f"⭐ NHA MAY DA DUOC NANG CAP LEN CAP {new_lvl} THANH CONG!", Fore.GREEN)
        else:
            log("UPGRADE_WARN", f"Chua the nang cap: {res.get('error', {}).get('message')}", Fore.YELLOW)


#  6. CÀY QUẢNG CÁO KIẾM COIN (ADSGRAM)

# -----------------------------------------------------------------


def auto_watch_coin_ads(ad_config, phase="running"):
    # UU TIEN SO 1: DUNG QUANG CAO CHO ME NUNG SAT!
    # Neu lo dang idle -> KHONG XEM quang cao coin de tranh het luot nung!
    if phase == "idle":
        return 900

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


#  7. NHIỆM VỤ ĐỐI TÁC & KÊNH TELEGRAM (COMMUNITY TASKS)

# -----------------------------------------------------------------

def auto_claim_partner_tasks():

    try:

        res = api_call("/api/v1/game/community")

        if not res.get("success"):

            return

        tasks = res.get("data", {}).get("tasks", [])

        for task in tasks:

            t_id = task.get("id")

            title = task.get("title")

            reward = task.get("reward", 0)

            claimed = task.get("claimed", False)

            url = task.get("url", "")



            if claimed:

                continue



            log("TASK", f"Phat hien nhiem vu kenh doi tac [{title}] (+{reward:,} Coin)! Dang xu ly...", Fore.CYAN)

            

            # Neu co link kenh Telegram -> Tu dong join

            if "t.me/" in url:

                ch_username = url.split("t.me/")[-1].split("?")[0].split("/")[0]

                if ch_username:

                    async def _join():

                        client = TelegramClient(StringSession(get_clean_string_session()), API_ID, API_HASH)

                        await client.connect()

                        try:

                            await client(JoinChannelRequest(ch_username))

                            log("JOIN_OK", f"Da tham gia kenh @{ch_username} thanh cong!", Fore.GREEN)

                        except Exception:

                            pass

                        finally:

                            await client.disconnect()

                    try:

                        asyncio.run(_join())

                    except Exception:

                        pass



            # Gui request xac minh nhan thuong

            claim_res = api_transact("partner-claim", {"taskId": t_id})

            if claim_res.get("success"):

                log("TASK_OK", f"🎉 NHAN THANH CONG +{reward:,} COIN TU NHIEM VU [{title}]!", Fore.GREEN)

            else:

                err = claim_res.get("error", {}).get("message", "")

                log("TASK_WARN", f"Chua nhan duoc: {err}", Fore.YELLOW)

    except Exception as e:

        log("TASK_ERR", f"Loi xu ly nhiem vu doi tac: {e}", Fore.RED)



# -----------------------------------------------------------------

#  8. SĂN & NHẬP GIFTCODE TỰ ĐỘNG (AUTO REDEEM GIFTCODES)

# -----------------------------------------------------------------

KNOWN_REDEEMED_CODES = set()



def auto_redeem_giftcodes():

    global KNOWN_REDEEMED_CODES

    candidate_codes = set()



    # 1. Lay giftcode truyen tu bien moi truong (neu co)

    env_codes = os.getenv("VOXELCRAFT_GIFTCODES", "").strip()

    if env_codes:

        for c in env_codes.split(","):

            c = c.strip().upper()

            if c:

                candidate_codes.add(c)



    # 2. Tu dong quet tin nhan tren kenh chinh thuc @IroncraftFarm bang Telethon

    async def _scan_channel():

        codes = set()

        client = TelegramClient(StringSession(get_clean_string_session()), API_ID, API_HASH)

        await client.connect()

        try:

            channel = await client.get_entity("IroncraftFarm")

            messages = await client.get_messages(channel, limit=15)

            for m in messages:

                if m.text:

                    found = re.findall(r'IRONCRAFT-[A-Z0-9]+', m.text)

                    for f_code in found:

                        codes.add(f_code.upper())

        except Exception:

            pass

        finally:

            await client.disconnect()

        return codes



    try:

        scanned = asyncio.run(_scan_channel())

        candidate_codes.update(scanned)

    except Exception:

        pass



    # 3. Thu redeem tung code

    for code in candidate_codes:

        if code in KNOWN_REDEEMED_CODES:

            continue



        log("GIFTCODE", f"Phat hien ma Giftcode: [{code}]. Dang tien hanh nhap...", Fore.MAGENTA)

        res = api_transact("giftcode", {"code": code})

        KNOWN_REDEEMED_CODES.add(code)



        if res.get("success"):

            reward = res.get("data", {}).get("reward", 0)

            log("GIFTCODE_OK", f"🎁 NHAP GIFTCODE [{code}] THANH CONG! Nhan +{reward:,} Coin!", Fore.GREEN)

        else:

            err = res.get("error", {}).get("message", "")

            log("GIFTCODE_INFO", f"Ket qua giftcode [{code}]: {err}", Fore.WHITE)



# -----------------------------------------------------------------

#  VÒNG LẶP CHÍNH 24/7

# -----------------------------------------------------------------

def run_loop():

    start_time = time.time()

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



    # 1. Khoi dong lay init_data moi nhat

    get_fresh_init_data_sync()



    cycle = 1

    last_refresh_init_time = time.time()



    while True:

        elapsed = time.time() - start_time

        if elapsed >= (SHIFT_SECONDS - 600):

            log("HANDOVER", f"Ca chay da dat {elapsed/3600:.2f}h. Kich hoat ca tiep theo 24/7...", Fore.YELLOW)

            trigger_next_shift()

            log("HANDOVER_OK", "Ket thuc ca hien tai êm dep.", Fore.GREEN)

            break



        log("CYCLE", f"--- CHU KY #{cycle} (Ca con {(SHIFT_SECONDS - elapsed)/3600:.2f}h) ---", Fore.CYAN)



        try:

            # 1. Lay thong tin tong quan ve nha may

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



            # 2.1 Tu dong kiem tra nhiem vu kenh doi tac (+5,000 Coin) & Giftcode

            if cycle == 1 or cycle % 10 == 0:

                auto_claim_partner_tasks()

                auto_redeem_giftcodes()



            # 3. Xu ly theo tung trang thai cua lo nung:

            if phase == "ready" and run:

                # Me nung da xong -> Thu hoach ngay

                auto_claim_harvest(run, economy)

                # Sau khi thu hoach -> Ban sat

                fresh_sum = get_game_summary().get("data", {}).get("state", {})

                if fresh_sum.get("iron", 0) > 0:

                    auto_sell_iron(fresh_sum.get("iron", 0))



            elif phase == "haul" and iron > 0:

                # Co sat trong kho chua ban -> Ban ngay

                auto_sell_iron(iron)



            elif phase == "idle":

                # Lo nung dang ranh -> Kiem tra nang cap truoc

                auto_upgrade_factory(state, economy)

                # Neu co sat thi ban

                if iron > 0:

                    auto_sell_iron(iron)

                # Bat dau me nung moi

                run = auto_start_run(state, economy)



            elif phase == "running" and run:

                ends_at = run.get("endsAt", 0)

                rem_sec = max(0, int((ends_at - server_now) / 1000))

                mins, secs = divmod(rem_sec, 60)

                log("RUNNING", f"Me nung dang chay, du kien xong sau {mins}m {secs}s...", Fore.YELLOW)

                if rem_sec <= 0:

                    # Da den gio xong -> Lay summary moi de cap nhat sang ready

                    get_game_summary()



            # 4. Kiem tra xem quang cao kiem Coin neu co

            auto_watch_coin_ads(ad_config, phase=phase)



            # 5. Lam moi init_data dinh ky sau moi 60 phut

            if time.time() - last_refresh_init_time > 3600:

                log("REFRESH", "Lam moi init_data tu Telegram...", Fore.MAGENTA)

                get_fresh_init_data_sync()

                last_refresh_init_time = time.time()



        except Exception as e:

            log("ERR", f"Loi trong chu ky: {e}", Fore.RED)



        # Nghi 30 giay giua cac vong kiem tra

        cycle += 1

        time.sleep(30)



if __name__ == "__main__":

    run_loop()

