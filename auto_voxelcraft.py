#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
  BOT AUTO PLAY 24/7 - VOXELCRAFT / IRON CRAFT FARM (@IronCraftFarmBot)
  Website: https://voxelcraft.online | Bot: @IronCraftFarmBot
  
  TINH NANG CHINH TOAN DIEN:
    - HO TRO DA TAI KHOAN: Acc 1..4 (hungzai22, gaylobucu, phanhhyy, Wind_trader)
    - AUTO INDATA 100%: Tu dong lay init_data moi qua Telethon StringSession
      (chay 100% tren RAM, khong loi SQLite disk, khong bao gio het han token).
    - TU DONG NUNG SAT 24/7 (Smelt Iron):
      + Tu dong phat hien va chay me Tap su (Trial Run - 60 giay) cho tai khoan moi.
      + Tu dong tao va xac thuc phien quang cao nhiem vu (Adsgram Task 55088)
        chuan co che trinh duyet (client-complete) de nung sat lien tuc khong gian doan.
    - TU DONG THU HOACH & BAN SAT (Harvest & Sell Iron):
      + Nhan 100% sat khong mat phi.
      + Tu dong ban sat vao kho d?i lay Coin (+30 Coin/thoi).
    - TU DONG NANG CAP NHA MAY (Upgrade Factory):
      + Tu dong dung Coin nang cap cap do nha may (Lv.1 -> Lv.2 -> Lv.8+)
        de tang san luong moi me nung.
    - TU DONG NHAN THANH TICH & NHIEM VU DOI TAC:
      + Nhan toan bo thanh tich thuong Coin (100 - 500 Coin).
      + Nhan nhiem vu doi tac (+5.000 Coin moi nhiem vu).
      + Tu dong nhap cac Giftcode con hoat dong.
    - TU DONG CAY QUANG CAO COIN (Adsgram Coin - 55082):
      + +100 Coin/luot, tu canh cooldown 15 phut.
    - BAN GIAO CA LIEN TUC 24/7 TREN GITHUB ACTIONS:
      + Concurrency group rieng cho tung acc voi cancel-in-progress: true.
====================================================================
"""

import os
import sys
import re
import time
import json
import uuid
import random
import base64
import asyncio
import argparse
import urllib.parse
from datetime import datetime, timezone
import requests
from colorama import Fore, Style, init

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import RequestWebViewRequest

init(autoreset=True)

# -----------------------------------------------------------------
#  DANH SACH TAI KHOAN HO TRO
# -----------------------------------------------------------------
ACCOUNTS_CONFIG = {
    1: {
        "name": "Acc 1 (hungzai22)",
        "api_id": 39182276,
        "api_hash": "f02b155d895a3a3fbf8a1cbe810b5338",
        "session": (
            "1BVtsOHIBuxmpWiBJ9hvwV9pSrzWw5U2I5Fe20Ww8l1LCk9rnsG6T6lLZEJXZE1JJC_qUH_yyWHnRoed"
            "RNI5lJYnfjRN4gyGeDrCxquDU12ZflrpCz0VLhMZx2C0LlyUCy2eHRSRE1wUCpEYZaymL0P7Z9eAHwMy4"
            "Oogewh5TqyO4x4MF6j0yTq8Zvfpv43O4aQDzErNv3GRqpx8DXBcOJIMP9yVhq-Mby5VH5J9cF-h-bJ5ws"
            "3xKjA4GY7YKjHxDt9OI-Zr7mr-V3qZy99UxJooThJj51f2RqOKhODdLh9XZQ0ygSoAd3iFAZDOPMEo8Ch"
            "5TrrzLXi2Q3N0HorIL1JfV0xoFQlY="
        )
    },
    2: {
        "name": "Acc 2 (gaylobucu)",
        "api_id": 39182276,
        "api_hash": "f02b155d895a3a3fbf8a1cbe810b5338",
        "session": (
            "1BVtsOHIBuzoeRtBOmpNGh2sdyxpZ5e0nY4MrFe-6KKbmJPaM0YnCJiKRI0L9mEh1C5rwqLQqucj456LRF7v"
            "V1YIPjZNqL6JevLM0Ww3FTml1NoKdwsiPINfsy9MbBlBhKOvha7py44L4pK5aEXjwpjpoNj4LaSmtWaPiQPuf"
            "JuTwPB86f4gYjSeXM3HtxhnFU7MtHR5vbZPBa9N2HQSlt2BMB47q00DbQVtvYA37R3R-TrtV2MtwixL9ozChAD"
            "Fq38NYcw4eRyRwKrkobVLccvz0_hvqgHXiQbrfcFLLRkRGwGlRCB-Ew4YhLLdnCbG1hjGEfxUrp9MRmF0JvS"
            "-u20MfAuvlcgQ="
        )
    },
    3: {
        "name": "Acc 3 (phanhhyy)",
        "api_id": 39182276,
        "api_hash": "f02b155d895a3a3fbf8a1cbe810b5338",
        "session": (
            "1BVtsOHIBuxrTG6Dt9a8C_J7D3bm1disV_mQiY_mw7AP5Gp-cEVAlKU1cfvOJiDnU6yi7PInfBRG_wJBQ3uNc-1k"
            "Oa8fM3ITgUcE7YkaCd77FoBTgIFqw6gMYeRfVJOS1U9S_botQyX5764dx94NBfHHm8HuQKejs0PrdAJQq6WUT"
            "DS3mkijWRWIvO4SwXSUrM5yNOFoGIrav8Mbuyl5ZFQaDPg_kwa11NT4kiqov8rVx0virTbGbQudyFeG80kP4zW2"
            "CxcuL6TObemIPJgR_2-jb8zVQRQMiI4oN829ZCfHU2JCQY2S2clWwI7onZV8AhYP1LoDBiu32dgQPuk4brS-r"
            "1DtkySc="
        )
    },
    4: {
        "name": "Acc 4 (Wind_trader)",
        "api_id": 34333329,
        "api_hash": "4f9371f95000578c84dbc670aaf1f819",
        "session": (
            "1BVtsOIIBuzNuH5Jfb4Uwek2dG7YRqSyFk-74KTokth0VB3_UTMwM8Edh_ikn83fJOGyN7JaWzIZXnro3ico"
            "Y8zsjYIlT5nQ4z_GgKknABQ74FRseCvNbz3yyTkPOfQ4xJfZnJIJHuY4EkzVOzQzYZFg_EJWOj_vvg6OVwSk"
            "Qv9Nd52tl_SlH4TofoxDXDNvxLJyFcoQFH6BegTybx-pFyX2tz0rMeR7AQujnGxqdWOd4zywoFVShzsCTFeq"
            "dsBP9itJvg1YB0ISmJEYXzGEQo37IddAFGw3PJcAIY4BBctxri9_Cw-FbxhMgLU9gsotA3Rrys2jLcGV4CGf"
            "Op_IzD0CmtNm845I="
        )
    }
}

parser = argparse.ArgumentParser()
parser.add_argument("--acc", type=int, default=int(os.getenv("ACC_NUM", "1")), help="Account index (1..4)")
parser.add_argument("--once", action="store_true", help="Chay 1 vong duy nhat roi thoat")
args, _ = parser.parse_known_args()

ACC_INDEX = args.acc
acc_data = ACCOUNTS_CONFIG.get(ACC_INDEX, ACCOUNTS_CONFIG[1])

API_ID = acc_data["api_id"]
API_HASH = acc_data["api_hash"]
STRING_SESSION = (
    os.getenv(f"TELEGRAM_STRING_SESSION_ACC{ACC_INDEX}")
    or os.getenv("TELEGRAM_STRING_SESSION")
    or os.getenv(f"TELEGRAM_SESSION_B64_ACC{ACC_INDEX}")
    or acc_data["session"]
)

BOT_USERNAME = "IronCraftFarmBot"
BASE_URL = "https://voxelcraft.online"

HEADERS = {
    'Content-Type': 'application/json',
    'Referer': f"{BASE_URL}/",
    'User-Agent': 'Mozilla/5.0 (Linux; Android 14; SM-S928B Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.82 Mobile Safari/537.36 Telegram-Android/10.11.1'
}

IS_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
SHIFT_SECONDS = int(os.getenv("MAX_RUNTIME_SECONDS", "17000" if IS_GITHUB_ACTIONS else "0"))  # ~4.7 tieng

CURRENT_INIT_DATA = ""
CURRENT_USER_NAME = ""
CURRENT_USER_ID = ""

KNOWN_REDEEMED_CODES = set()
LAST_COIN_AD_TIME = 0
LAST_PENDING_AD_SESS_ID = None

def log(tag, msg, color=Fore.WHITE):
    t = datetime.now().strftime("%H:%M:%S")
    print(f"[{t}] [{tag}] {color}{msg}{Style.RESET_ALL}", flush=True)

def fmt_num(val):
    try:
        return f"{int(val):,}"
    except:
        return str(val)

# -----------------------------------------------------------------
#  LAY INIT_DATA MOI QUA TELETHON
# -----------------------------------------------------------------
async def fetch_fresh_init_data():
    global CURRENT_INIT_DATA, CURRENT_USER_NAME, CURRENT_USER_ID
    acc_name = acc_data.get("name", f"Acc {ACC_INDEX}")
    log("TELETHON", f"Ket noi Telegram bang StringSession [{acc_name}]...", Fore.CYAN)

    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        log("ERR", f"Phien Telegram chua xac thuc cho [{acc_name}]!", Fore.RED)
        await client.disconnect()
        return None

    try:
        bot = await client.get_input_entity(BOT_USERNAME)
        res = await client(RequestWebViewRequest(
            peer=bot,
            bot=bot,
            platform="android",
            from_bot_menu=False,
            url=f"{BASE_URL}/"
        ))
        await client.disconnect()

        parsed = urllib.parse.urlparse(res.url)
        params = urllib.parse.parse_qs(parsed.fragment)
        CURRENT_INIT_DATA = params.get("tgWebAppData", [""])[0]

        qs = urllib.parse.parse_qs(CURRENT_INIT_DATA)
        user_json = json.loads(qs.get("user", ["{}"])[0])
        CURRENT_USER_ID = str(user_json.get("id"))
        CURRENT_USER_NAME = user_json.get("username", f"user_{CURRENT_USER_ID}")

        log("AUTH_OK", f"Lay init_data thanh cong! User: {CURRENT_USER_NAME} (ID: {CURRENT_USER_ID})", Fore.GREEN)
        return CURRENT_INIT_DATA
    except Exception as e:
        log("ERR", f"Loi khi lay webview init_data: {e}", Fore.RED)
        await client.disconnect()
        return None

def get_fresh_init_data_sync():
    return asyncio.run(fetch_fresh_init_data())

def api_call(path, payload=None, retry_on_auth_err=True):
    global CURRENT_INIT_DATA
    if payload is None:
        payload = {}
    if not CURRENT_INIT_DATA:
        get_fresh_init_data_sync()

    payload["initData"] = CURRENT_INIT_DATA
    url = f"{BASE_URL}{path}"
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        res = r.json()
        if retry_on_auth_err and isinstance(res, dict) and not res.get("success"):
            err_code = str(res.get("error", {}).get("code", ""))
            if err_code in ["AUTH_EXPIRED", "AUTH_INVALID"]:
                log("REFRESH", "InitData het han, dang lay lai tu Telegram...", Fore.YELLOW)
                get_fresh_init_data_sync()
                payload["initData"] = CURRENT_INIT_DATA
                r2 = requests.post(url, json=payload, headers=HEADERS, timeout=15)
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
#  1. XAC THUC PHIEN QUANG CAO (ADSGRAM TASK / REWARDED)
# -----------------------------------------------------------------
def create_and_verify_ad_session(purpose="smelt"):
    global LAST_PENDING_AD_SESS_ID

    # Neu co phien truoc do dang pending, thu hoan tat no truoc
    if LAST_PENDING_AD_SESS_ID:
        try:
            c_res = api_call(f"/api/v1/game/ads/sessions/{LAST_PENDING_AD_SESS_ID}/client-complete")
            if c_res.get("success"):
                log("AD_CLEAR", f"Da hoan tat phien pending cu: {LAST_PENDING_AD_SESS_ID[:12]}...", Fore.GREEN)
                sess = LAST_PENDING_AD_SESS_ID
                LAST_PENDING_AD_SESS_ID = None
                return sess
        except:
            pass

    ad_providers = ["adsgram_task", "adsgram"]
    for prov in ad_providers:
        try:
            log("AD_SMELT", f"Tao phien quang cao truoc khi nung ({prov})...", Fore.CYAN)
            ad_res = api_call("/api/v1/game/ads/sessions", {
                "provider": prov,
                "purpose": purpose
            })

            if not ad_res.get("success"):
                err = ad_res.get("error", {})
                err_code = err.get("code")
                err_msg = err.get("message", "")
                if err_code == "AD_PENDING":
                    log("AD_WARN", f"Phat hien phien dang pending tren server, cho 5s roi thu lai...", Fore.YELLOW)
                    time.sleep(5)
                else:
                    log("AD_WARN", f"Nha cung cap {prov}: [{err_code}] {err_msg}", Fore.YELLOW)
                continue

            sess = ad_res.get("data", {})
            sess_id = sess.get("id")
            if not sess_id:
                continue

            LAST_PENDING_AD_SESS_ID = sess_id

            # Mo phong thoi gian xem quang cao tu nhien (10-15s)
            watch_sec = round(random.uniform(10.5, 14.5), 2)
            log("AD_WATCH", f"Dang xem quang cao mo phong {prov} ({watch_sec}s)...", Fore.CYAN)
            time.sleep(watch_sec)

            comp_res = api_call(f"/api/v1/game/ads/sessions/{sess_id}/client-complete")
            if comp_res.get("success"):
                stat_data = comp_res.get("data", {})
                status = stat_data.get("status")
                if status == "REWARDED" or stat_data.get("clientCompleted"):
                    log("AD_OK", f"🎉 Xac minh phien quang cao ({prov}) thanh cong: {sess_id[:12]}...", Fore.GREEN)
                    LAST_PENDING_AD_SESS_ID = None
                    return sess_id
                else:
                    log("AD_WARN", f"Trang thai phien chua REWARDED ({status})", Fore.YELLOW)
            else:
                log("AD_WARN", f"Loi client-complete: {comp_res.get('error')}", Fore.YELLOW)

        except Exception as e:
            log("AD_ERR", f"Loi tao phien ad {prov}: {e}", Fore.LIGHTBLACK_EX)

    return None

# -----------------------------------------------------------------
#  2. KHOI DONG ME NUNG SAT (START RUN)
# -----------------------------------------------------------------
def auto_start_run(state, economy):
    log("START", "Bat dau me nung sat moi trong lo...", Fore.CYAN)
    payload = {}

    # Neu chua dung me tap su (trialUsed == False) -> Bat dau ngay khong can adSession
    trial_used = state.get("trialUsed", True)
    if not trial_used:
        log("TRIAL", "Phat hien me nung Tap su (Trial Run - 60 giay)! Khoi dong ngay...", Fore.GREEN)
        res = api_transact("start", payload)
        if res.get("success"):
            st = res.get("data", {}).get("state", {})
            run = st.get("run", {})
            log("START_OK", f"🔥 ME NUNG TAP SU DA KHOI DONG! Thoi luong 60s, Thuong +{run.get('quantity', 10)} Sat!", Fore.GREEN)
            return run
        else:
            log("START_ERR", f"Khong the bat dau me tap su: {res.get('error')}", Fore.RED)
            return None

    # Kiem tra bao tri lo nung neu can
    m_quote = get_maintenance_plan(state, economy)
    if m_quote and m_quote.get("due"):
        coins_needed = m_quote.get("coins", 0)
        user_coins = state.get("coins", 0)
        log("MAINT_DUE", f"⚙️ Lo nung can bao tri! Chi phi: {coins_needed} Coin (Hien co: {user_coins} Coin)", Fore.YELLOW)
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

    # Tao phien quang cao xac minh truoc khi nung neu co che taskBeforeSmelt bat
    task_before = economy.get("taskBeforeSmelt", True)
    if task_before:
        sess_id = create_and_verify_ad_session(purpose="smelt")
        if not sess_id:
            log("START_WARN", "Chua the tao phien quang cao hop le, he thong se thu lai o chu ky tiep theo.", Fore.YELLOW)
            return None
        payload["adSessionId"] = sess_id

    res = api_transact("start", payload)
    if res.get("success"):
        st = res.get("data", {}).get("state", {})
        run = st.get("run", {})
        qty = run.get("quantity", 8)
        ends_at = run.get("endsAt", 0)
        log("START_OK", f"🔥 ME NUNG SAT MOI DA KHOI DONG! San luong: +{qty} Thoi sat (~{qty*30} Coin)", Fore.GREEN)
        return run
    else:
        err = res.get("error", {})
        log("START_ERR", f"Loi khoi dong me nung: {err.get('code')} - {err.get('message')}", Fore.RED)
        return None

def get_maintenance_plan(state, economy):
    m_cfg = economy.get("maintenance")
    if not m_cfg or not isinstance(m_cfg, dict):
        return None
    interval = m_cfg.get("interval", 6)
    percent = m_cfg.get("percent", 10)
    total_completed = state.get("totalSold", 0) // max(1, economy.get("runIron", 8))
    run = state.get("run")
    if run:
        total_completed = max(total_completed, run.get("completedBatches", total_completed))
    level = state.get("level", 1)
    iron_price = economy.get("ironPrice", 30)
    iron_per_batch = economy.get("runIron", 8) * (1 + (level - 1) * economy.get("productionGrowth", 0.15))
    batch_revenue = iron_per_batch * iron_price
    cycle_revenue = batch_revenue * interval
    cost_coins = int(cycle_revenue * (percent / 100))
    cost_iron = int(cost_coins / iron_price)
    due = (total_completed > 0 and (total_completed % interval == 0))
    return {
        "policy": m_cfg.get("version", "maintenance-v1"),
        "interval": interval,
        "completed": total_completed,
        "level": level,
        "coins": max(10, cost_coins),
        "iron": max(1, cost_iron),
        "due": due
    }

# -----------------------------------------------------------------
#  3. THU HOACH & BAN SAT (CLAIM & SELL)
# -----------------------------------------------------------------
def auto_claim_harvest(run_data, economy=None):
    run_id = run_data.get("id")
    quantity = run_data.get("quantity", 0)
    log("HARVEST", f"Dang thu hoach me nung #{str(run_id)[:8]} (+{quantity} Sat)...", Fore.CYAN)

    direct_res = api_transact("claim", {"runId": run_id})
    if direct_res.get("success"):
        log("CLAIM_OK", f"🎉 THU HOACH THANH CONG TRON VEN +{quantity} THOI SAT!", Fore.GREEN)
        return True

    # Neu can xem quang cao de mien phi
    ad_sess = create_and_verify_ad_session(purpose="harvest")
    if ad_sess:
        c_res = api_transact("claim", {"runId": run_id, "adSessionId": ad_sess})
        if c_res.get("success"):
            log("CLAIM_OK", f"🎉 THU HOACH THANH CONG TRON VEN +{quantity} THOI SAT (Qua quang cao)!", Fore.GREEN)
            return True

    # Fallback tra phi
    fee_iron = run_data.get("feeIron", 1)
    c_res = api_transact("claim", {
        "runId": run_id,
        "method": "fee",
        "feeIron": fee_iron
    })
    if c_res.get("success"):
        net = quantity - fee_iron
        log("CLAIM_OK", f"Thu hoach thanh cong +{net} Sat (Tru phi {fee_iron} sat).", Fore.YELLOW)
        return True

    log("CLAIM_ERR", f"Loi thu hoach: {c_res.get('error')}", Fore.RED)
    return False

def auto_sell_iron(iron_quantity):
    if iron_quantity <= 0:
        return
    log("SELL", f"Ban {iron_quantity} thoi sat vao kho (+{iron_quantity * 30} Coins)...", Fore.CYAN)
    res = api_transact("sell", {
        "quantity": iron_quantity,
        "source": "warehouse"
    })
    if res.get("success"):
        st = res.get("data", {}).get("state", {})
        earned = st.get("lastSale", iron_quantity * 30)
        total_coins = st.get("coins", 0)
        log("SELL_OK", f"💰 BAN SAT THANH CONG! +{earned:,} Coin (So du vi: {total_coins:,} Coin)", Fore.GREEN)
        return True
    else:
        log("SELL_ERR", f"Loi ban sat: {res.get('error')}", Fore.RED)
        return False

# -----------------------------------------------------------------
#  4. NANG CAP NHA MAY (UPGRADE FACTORY)
# -----------------------------------------------------------------
def auto_upgrade_factory(state, economy):
    level = state.get("level", 1)
    coins = state.get("coins", 0)
    first_cost = economy.get("firstUpgradeCost", 500)
    later_cost = economy.get("laterUpgradeCost", 1600)
    growth = economy.get("upgradeGrowth", 1.55)

    if level == 1:
        needed = first_cost
    else:
        needed = int(later_cost * (growth ** (level - 2)))

    if coins >= needed:
        log("UPGRADE", f"Du Coin! Dang nang cap nha may len Lv.{level + 1} (Chi phi: {needed:,} / {coins:,} Coin)...", Fore.MAGENTA)
        res = api_transact("upgrade", {"level": level})
        if res.get("success"):
            new_lvl = res.get("data", {}).get("state", {}).get("level", level + 1)
            new_coins = res.get("data", {}).get("state", {}).get("coins", coins - needed)
            log("UPGRADE_OK", f"⭐ NHA MAY DA NANG CAP LEN LV.{new_lvl}! (Con lai: {new_coins:,} Coin)", Fore.GREEN)
            return True
        else:
            log("UPGRADE_ERR", f"Loi nang cap nha may: {res.get('error')}", Fore.RED)
    return False

# -----------------------------------------------------------------
#  5. THANH TICH, NHIEM VU DOI TAC & GIFTCODES
# -----------------------------------------------------------------
def auto_claim_achievements(state):
    claimed = set(state.get("claimedAchievements", []))
    achievements = [
        {"id": "factory_first_haul", "name": "Me sat dau tien", "reward": 100, "cond": state.get("totalIron", 0) > 0},
        {"id": "factory_first_sale", "name": "Giao dich dau tien", "reward": 150, "cond": state.get("totalSold", 0) > 0},
        {"id": "factory_100_iron", "name": "Tho nung cham chi (100 sat)", "reward": 300, "cond": state.get("totalIron", 0) >= 100},
        {"id": "factory_level_2", "name": "Nha may Lv.2", "reward": 200, "cond": state.get("level", 1) >= 2},
        {"id": "factory_level_3", "name": "Nha may Lv.3", "reward": 300, "cond": state.get("level", 1) >= 3},
        {"id": "factory_level_5", "name": "Nha may Lv.5", "reward": 500, "cond": state.get("level", 1) >= 5},
    ]

    for a in achievements:
        a_id = a["id"]
        name = a["name"]
        reward = a["reward"]
        if a["cond"] and a_id not in claimed:
            log("ACHIEVE", f"Nhan thanh tich [{name}]: +{reward} Coin...", Fore.MAGENTA)
            res = api_transact("achievement", {"goalId": a_id})
            if res.get("success"):
                log("ACHIEVE_OK", f"🎉 Nhan thanh cong thanh tich [{name}] (+{reward} Coin)!", Fore.GREEN)
                claimed.add(a_id)
            time.sleep(1)

def auto_claim_partner_tasks():
    res = api_call("/api/v1/game/tasks")
    if not res.get("success"):
        return
    tasks = res.get("data", {}).get("tasks", [])
    for t in tasks:
        t_id = t.get("id")
        title = t.get("title", t_id)
        reward = t.get("reward", 5000)
        is_completed = t.get("completed", False)
        if not is_completed:
            log("PARTNER", f"Phat hien nhiem vu [{title}] (+{reward:,} Coin), dang xac minh...", Fore.CYAN)
            claim_res = api_transact("partner-claim", {"taskId": t_id})
            if claim_res.get("success"):
                log("TASK_OK", f"🎉 NHAN THANH CONG +{reward:,} COIN TU NHIEM VU [{title}]!", Fore.GREEN)
            time.sleep(1)

def auto_redeem_giftcodes():
    giftcodes = ["VOXEL2026", "IRONCRAFT", "FREECOIN", "MINEFARM", "MINCAF247"]
    for code in giftcodes:
        if code in KNOWN_REDEEMED_CODES:
            continue
        res = api_transact("giftcode", {"code": code})
        KNOWN_REDEEMED_CODES.add(code)
        if res.get("success"):
            reward = res.get("data", {}).get("reward", 0)
            log("GIFTCODE_OK", f"🎁 NHAP GIFTCODE [{code}] THANH CONG: +{reward:,} COIN!", Fore.GREEN)
        time.sleep(0.5)

# -----------------------------------------------------------------
#  6. CAY QUANG CAO COIN (ADSGRAM COIN - +100 COIN/LUOT, 15M COOLDOWN)
# -----------------------------------------------------------------
def auto_watch_coin_ads(ad_config, phase="running"):
    global LAST_COIN_AD_TIME
    if not ad_config:
        return
    now = time.time()
    coin_limit = ad_config.get("coinLimit", 6)
    coin_used = ad_config.get("coinUsed", 0)
    cooldown = ad_config.get("cooldownSeconds", 900)

    if coin_used >= coin_limit:
        return
    if (now - LAST_COIN_AD_TIME) < cooldown:
        return

    try:
        log("AD_COIN", f"Phat hien luot xem quang cao Coin ({coin_used}/{coin_limit}). Dang tao phien...", Fore.CYAN)
        sess_res = api_call("/api/v1/game/ads/sessions", {
            "provider": "adsgram",
            "purpose": "coins"
        })
        if not sess_res.get("success"):
            return

        sess_id = sess_res.get("data", {}).get("id")
        if not sess_id:
            return

        watch_sec = round(random.uniform(11.0, 15.0), 2)
        log("AD_COIN", f"Dang xem video Adsgram Coin ({watch_sec}s)...", Fore.CYAN)
        time.sleep(watch_sec)

        comp = api_call(f"/api/v1/game/ads/sessions/{sess_id}/client-complete")
        if comp.get("success"):
            log("AD_COIN_OK", "🎉 Xem quang cao nhan Coin thanh cong! +100 Coin da cong vao vi.", Fore.GREEN)
            LAST_COIN_AD_TIME = now
    except Exception as e:
        log("AD_COIN_ERR", f"Loi xem quang cao Coin: {e}", Fore.LIGHTBLACK_EX)

# -----------------------------------------------------------------
#  VONG LAP CHINH 24/7
# -----------------------------------------------------------------
def run_loop():
    acc_name = acc_data.get("name", f"Acc {ACC_INDEX}")
    banner = [
        "=" * 64,
        f"   BOT AUTO VOXELCRAFT FARM 24/7 - {acc_name.upper()}",
        "=" * 64,
        f" Tai khoan : {CURRENT_USER_NAME} (ID: {CURRENT_USER_ID})",
        f" Bot Game  : @{BOT_USERNAME} | WebApp: {BASE_URL}",
        f" Che do    : Telethon StringSession (RAM 100% - Zero Disk SQLite Error)",
        f" Tinh nang : Auto Smelt | Auto Harvest | Auto Sell | Auto Upgrade",
        "=" * 64
    ]
    print("\n" + "\n".join(banner) + "\n", flush=True)

    start_time = time.time()
    cycle = 0
    last_refresh_init_time = time.time()

    while True:
        try:
            if SHIFT_SECONDS > 0 and (time.time() - start_time) >= SHIFT_SECONDS:
                log("DONE", f"Hoan thanh phien chay {SHIFT_SECONDS}s tren GitHub Actions. Ban giao ca!", Fore.GREEN)
                break

            cycle += 1
            log("CYCLE", f"--- CHU KY #{cycle} [{acc_name}] ---", Fore.CYAN)

            # 1. Lay thong tin tong quan nha may
            sum_res = get_game_summary()
            if not sum_res.get("success"):
                log("WARN", f"Chua the lay thong tin game: {sum_res.get('error')}", Fore.YELLOW)
                time.sleep(15)
                continue

            data = sum_res.get("data", {})
            state = data.get("state", {})
            economy = data.get("economy", {})
            ad_config = data.get("adConfig", {})
            server_now = data.get("serverNow", int(time.time() * 1000))

            phase = state.get("phase", "unknown")
            coins = state.get("coins", 0)
            iron = state.get("iron", 0)
            level = state.get("level", 1)
            run = state.get("run")

            log("STATUS", f"Nha may Lv.{level} | Trang thai: [{phase.upper()}] | Sat: {iron} thoi | Vi: {coins:,} Coin (~{coins*5/1000:,.1f} VND)", Fore.GREEN)

            # 2. Kiem tra va nhan thanh tich
            auto_claim_achievements(state)

            # 2.1 Kiem tra nhiem vu doi tac & giftcodes
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
                    get_game_summary()

            # 4. Kiem tra xem quang cao kiem Coin neu co
            auto_watch_coin_ads(ad_config, phase=phase)

            if args.once:
                log("DONE", "Da hoan thanh 1 chu ky theo tham so --once. Dung chuong trinh.", Fore.GREEN)
                break

            # 5. Lam moi init_data sau moi 60 phut
            if time.time() - last_refresh_init_time > 3600:
                log("REFRESH", "Lam moi init_data tu Telegram...", Fore.MAGENTA)
                get_fresh_init_data_sync()
                last_refresh_init_time = time.time()

        except KeyboardInterrupt:
            log("STOP", "Da dung bot theo yeu cau nguoi dung.", Fore.YELLOW)
            break
        except Exception as e:
            log("ERR", f"Loi trong chu ky: {e}", Fore.RED)

        time.sleep(30)

if __name__ == "__main__":
    init_tok = get_fresh_init_data_sync()
    if init_tok:
        run_loop()
    else:
        log("FATAL", "Khong the khoi dong bot do loi xac thuc Telegram. Dung chuong trinh.", Fore.RED)
