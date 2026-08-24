import datetime
import re
import asyncio
import threading
import time
import logging
import random
import json
import os
import atexit
import signal
from collections import defaultdict
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)
from telegram.request import HTTPXRequest
from telegram.constants import ParseMode

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_FILE = 'bot_data.json'
SAVE_LOCK = asyncio.Lock()
AUTO_SAVE_INTERVAL = 15
REPORT_REASON = 1

TOKEN = '8121648149:AAHgl_lOAcn3B5HcwSd8eBjvJc1wQTO5ajs'
ADMIN_IDS = [8329653179, 7138763220]
OWNER_ID = 8329653179
OWNER_USERNAME = "@L1nker_Official"
OWNER_CHANNEL = "https://t.me/L1nkerChaserYT"
OWNER_CHAT = "https://t.me/ChatL1nkeChaser"

# ==================== ВСЕ ДАННЫЕ ИЗ TWISTED ====================
CARS = {
    'Chevy 454ss': {'name': '🚗 Chevy 454ss', 'price': 0, 'max_speed': 85, 'hp': 10, 'desc': 'Самая базовая тачка', 'fixation': 0},
    'F-150': {'name': '🚙 F-150', 'price': 2500, 'max_speed': 100, 'hp': 12, 'desc': 'Средняя гражданская', 'fixation': 0},
    'SCOUT': {'name': '🚗 SCOUT', 'price': 0, 'max_speed': 125, 'hp': 15, 'desc': 'ЛУЧШАЯ ГРАЖДАНСКАЯ!', 'fixation': 0},
    'Tornado Puncher': {'name': '💪 Tornado Puncher', 'price': 75000, 'max_speed': 200, 'hp': 40, 'desc': 'Первый перехватчик', 'fixation': 5},
    'Dominator 1': {'name': '🏎️ Dominator 1', 'price': 100000, 'max_speed': 220, 'hp': 44, 'desc': 'Классика', 'fixation': 4},
    'TIV 1': {'name': '🛡️ TIV 1', 'price': 100000, 'max_speed': 225, 'hp': 45, 'desc': 'Легенда', 'fixation': 3},
    'Tornado Attack': {'name': '🌪️ Tornado Attack', 'price': 125000, 'max_speed': 250, 'hp': 50, 'desc': 'Агрессивный', 'fixation': 27},
    'Dominator 2': {'name': '🏎️ Dominator 2', 'price': 150000, 'max_speed': 250, 'hp': 50, 'desc': 'Улучшенный', 'fixation': 4},
    'UTAV': {'name': '🚁 UTAV', 'price': 175000, 'max_speed': 280, 'hp': 56, 'desc': 'Военный', 'fixation': 14},
    'Dorothy': {'name': '🌪️ Dorothy', 'price': 200000, 'max_speed': 200, 'hp': 40, 'desc': 'Уникальный', 'fixation': 0},
    'Dominator 3': {'name': '🏎️ Dominator 3', 'price': 250000, 'max_speed': 325, 'hp': 65, 'desc': 'ТОП-перехватчик', 'fixation': 4},
    'TIV 2': {'name': '🛡️ TIV 2', 'price': 300000, 'max_speed': 400, 'hp': 80, 'desc': 'САМАЯ ДОРОГАЯ!', 'fixation': 3}
}

RADARS = {
    'KHZL': {'name': '📡 KHZL', 'price': 200000, 'accuracy': 0.6, 'desc': 'Дальний радар', 'type': 'стационарный', 'color': 'черно-белый'},
    'THIB': {'name': '📡 THIB', 'price': 300000, 'accuracy': 0.8, 'desc': 'Короткий радар', 'type': 'стационарный', 'color': 'цветной'},
    'DOW': {'name': '🚗 DOW', 'price': 500000, 'accuracy': 0.95, 'desc': 'МОБИЛЬНЫЙ РАДАР!', 'type': 'мобильный', 'color': 'цветной'},
    'Raxpol': {'name': '📡 Raxpol', 'price': 300000, 'accuracy': 1.0, 'desc': 'Точный 100%', 'type': 'стационарный', 'color': 'цветной'},
    'Dow-7': {'name': '📡 Dow-7', 'price': 500000, 'accuracy': 1.0, 'desc': 'ТОП-радар', 'type': 'стационарный', 'color': 'цветной'}
}

PROBES = {
    'Turtle Probe': {'name': '🐢 Turtle Probe', 'price': 750, 'max_hp': 3, 'bonus': 1.2, 'desc': 'Базовый'},
    'Doto Probe': {'name': '📡 Doto Probe', 'price': 1000, 'max_hp': 4, 'bonus': 1.5, 'desc': 'Средний'},
    'Twisted Probe': {'name': '🌀 Twisted Probe', 'price': 1250, 'max_hp': 5, 'bonus': 2.0, 'desc': 'Мощный'},
    'Storm Shield': {'name': '🛡️ Storm Shield', 'price': 2000, 'max_hp': 8, 'bonus': 2.5, 'desc': 'Защитный'},
    'Invincible': {'name': '⭐ Invincible', 'price': 5000, 'max_hp': 15, 'bonus': 3.0, 'desc': 'НЕУЯЗВИМЫЙ!'}
}

EF_SCALE = {
    1: {'min': 0, 'max': 125, 'reward_min': 1000, 'reward_max': 3000, 'weight': 20, 'name': 'EF-1', 'color': '🟢', 'desc': 'Слабое'},
    2: {'min': 125, 'max': 200, 'reward_min': 3000, 'reward_max': 5000, 'weight': 30, 'name': 'EF-2', 'color': '🟡', 'desc': 'Умеренное'},
    3: {'min': 200, 'max': 280, 'reward_min': 5000, 'reward_max': 8000, 'weight': 30, 'name': 'EF-3', 'color': '🟠', 'desc': 'Сильное'},
    4: {'min': 280, 'max': 350, 'reward_min': 8000, 'reward_max': 12000, 'weight': 15, 'name': 'EF-4', 'color': '🔴', 'desc': 'Очень сильное'},
    5: {'min': 350, 'max': 450, 'reward_min': 12000, 'reward_max': 25000, 'weight': 5, 'name': 'EF-5', 'color': '⚫', 'desc': 'АПОКАЛИПСИС!'}
}

STAR_PACKAGES = [
    {'stars': 5, 'money': 100000},
    {'stars': 10, 'money': 200000},
    {'stars': 15, 'money': 300000},
    {'stars': 20, 'money': 500000},
    {'stars': 35, 'money': 700000},
    {'stars': 50, 'money': 1000000},
    {'stars': 100, 'money': 2500000}
]

BAN_CHATS = ["https://t.me/BOBZIchat", "https://t.me/BecChat1"]

# ==================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ====================
user_data = {}
chat_settings = {}
reports = []
bot_chats = set()
private_messages = []
chat_messages = {}
chat_user_stats = {}
cooldowns = {}
user_warn_count = {}
promocodes = {}
user_msg_times = {}
pending_purchases = {}
last_breakdown_check = {}
approved_admins = []
blocked_users = {}
active_storms = {}
active_hunters = {}
daily_quests = {}
achievements_data = {}
clans = {}
clan_members = {}
shop_items = {}
auction_items = {}
custom_interceptors = {}

bot_instance = None

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def get_user(user_id):
    return user_data.get(str(user_id))

def ensure_user(uid, full_name=None, username=None):
    uid = str(uid)
    if uid not in user_data:
        first = full_name.split()[0] if full_name else f'User{uid}'
        user_data[uid] = {
            'username': username, 'first_name': first, 'last_name': '',
            'messages_total': 0, 'messages_today': 0, 'last_message_date': None,
            'warned': 0, 'banned': False, 'muted': False, 'mute_until': None,
            'rank': 0, 'awards': 0, 'blocked': False,
            'balance': 5000, 'current_car': 'SCOUT', 'cars_owned': ['SCOUT'],
            'probes': {}, 'radars': [], 'current_radar': None, 'frozen': False,
            'total_intercepts': 0, 'successful_intercepts': 0, 'total_scans': 0,
            'storm_kills': 0, 'level': 1, 'xp': 0, 'xp_to_next': 100,
            'streak': 0, 'best_streak': 0, 'daily_streak': 0, 'last_daily': None,
            'vip_expires': None, 'clan': None, 'profession': None,
            'achievements': [], 'quests': {}, 'last_quest_reset': None
        }
        asyncio.create_task(save_data())

def is_blocked(user_id):
    return str(user_id) in blocked_users

def get_block_reason(user_id):
    return blocked_users.get(str(user_id), {}).get('reason', 'Неизвестна')

def block_user(user_id, reason="Неизвестна"):
    blocked_users[str(user_id)] = {'reason': reason, 'date': str(datetime.datetime.now())}
    asyncio.create_task(save_data())

def unblock_user(user_id):
    if str(user_id) in blocked_users:
        del blocked_users[str(user_id)]
        asyncio.create_task(save_data())

def get_user_rank(user_id):
    user = get_user(str(user_id))
    return user.get('rank', 0) if user else 0

def is_owner(user_id):
    return str(user_id) in [str(a) for a in ADMIN_IDS]

def is_owner_or_creator(user_id):
    return is_owner(user_id)

def is_approved_admin(user_id):
    return str(user_id) in [str(a) for a in approved_admins]

def can_mute_admin(user_id):
    return is_owner(user_id) or is_approved_admin(user_id)

def can_mute(user_id):
    return is_owner(user_id) or get_user_rank(user_id) >= 1

def can_warn(user_id):
    return is_owner(user_id) or get_user_rank(user_id) >= 2

def can_ban(user_id):
    return is_owner(user_id) or get_user_rank(user_id) >= 3

def can_kick(user_id):
    return is_owner(user_id) or get_user_rank(user_id) in (2, 3)

def get_setting(chat_id, key):
    return chat_settings.get(str(chat_id), {}).get(key, '')

def update_setting(chat_id, key, value):
    chat_id = str(chat_id)
    if chat_id not in chat_settings:
        chat_settings[chat_id] = {}
    chat_settings[chat_id][key] = value
    asyncio.create_task(save_data())

def parse_time(t):
    if not t:
        return 0
    try:
        if t.endswith('м'):
            return int(t[:-1]) * 60
        if t.endswith('ч'):
            return int(t[:-1]) * 3600
        if t.endswith('д'):
            return int(t[:-1]) * 86400
        if t.endswith('м') and len(t) > 1 and t[-2].isdigit():
            return int(t[:-1]) * 2592000
        return 0
    except:
        return 0

def format_time(s):
    if s <= 0:
        return "навсегда"
    d = s // 86400
    h = (s % 86400) // 3600
    m = (s % 3600) // 60
    parts = []
    if d > 0:
        parts.append(f"{d}д")
    if h > 0:
        parts.append(f"{h}ч")
    if m > 0:
        parts.append(f"{m}м")
    return " ".join(parts) if parts else "0м"

def add_xp(user_id, amount):
    user = get_user(user_id)
    if not user:
        return False
    user['xp'] = user.get('xp', 0) + amount
    user['xp_to_next'] = user.get('xp_to_next', 100)
    leveled = False
    while user['xp'] >= user['xp_to_next']:
        user['xp'] -= user['xp_to_next']
        user['level'] = user.get('level', 1) + 1
        user['xp_to_next'] = int(user['xp_to_next'] * 1.5)
        leveled = True
    asyncio.create_task(save_data())
    return leveled

def is_vip(user_id):
    user = get_user(user_id)
    if not user:
        return False
    vip_expires = user.get('vip_expires')
    if not vip_expires:
        return False
    try:
        return datetime.datetime.fromisoformat(vip_expires) > datetime.datetime.now()
    except:
        return False

def get_vip_multiplier(user_id):
    return 1.5 if is_vip(user_id) else 1.0

# ==================== БД ====================
async def save_data():
    async with SAVE_LOCK:
        try:
            data = {
                'user_data': user_data, 'chat_settings': chat_settings,
                'reports': reports, 'bot_chats': list(bot_chats),
                'private_messages': private_messages, 'chat_messages': chat_messages,
                'chat_user_stats': chat_user_stats, 'cooldowns': cooldowns,
                'user_warn_count': user_warn_count, 'promocodes': promocodes,
                'pending_purchases': pending_purchases, 'last_breakdown_check': last_breakdown_check,
                'approved_admins': approved_admins, 'blocked_users': blocked_users,
                'clans': clans, 'clan_members': clan_members, 'shop_items': shop_items,
                'auction_items': auction_items, 'achievements_data': achievements_data,
                'custom_interceptors': custom_interceptors
            }
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f'Ошибка сохранения: {e}')

def load_data():
    global user_data, chat_settings, reports, bot_chats, private_messages, chat_messages, chat_user_stats, cooldowns, user_warn_count, promocodes, pending_purchases, last_breakdown_check, approved_admins, blocked_users, clans, clan_members, shop_items, auction_items, achievements_data, custom_interceptors
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        user_data = data.get('user_data', {})
        chat_settings = data.get('chat_settings', {})
        reports = data.get('reports', [])
        bot_chats = set(data.get('bot_chats', []))
        private_messages = data.get('private_messages', [])
        chat_messages = data.get('chat_messages', {})
        chat_user_stats = data.get('chat_user_stats', {})
        cooldowns = data.get('cooldowns', {})
        user_warn_count = data.get('user_warn_count', {})
        promocodes = data.get('promocodes', {})
        pending_purchases = data.get('pending_purchases', {})
        last_breakdown_check = data.get('last_breakdown_check', {})
        approved_admins = data.get('approved_admins', [])
        blocked_users = data.get('blocked_users', {})
        clans = data.get('clans', {})
        clan_members = data.get('clan_members', {})
        shop_items = data.get('shop_items', {})
        auction_items = data.get('auction_items', {})
        achievements_data = data.get('achievements_data', {})
        custom_interceptors = data.get('custom_interceptors', {})

        for uid, udata in user_data.items():
            for field in ['current_car', 'cars_owned', 'probes', 'radars', 'current_radar',
                         'rank', 'awards', 'messages_total', 'messages_today', 'warned', 'balance',
                         'total_intercepts', 'successful_intercepts', 'total_scans', 'storm_kills',
                         'level', 'xp', 'xp_to_next', 'streak', 'best_streak', 'daily_streak']:
                if field not in udata:
                    if field in ('cars_owned',):
                        udata[field] = ['SCOUT']
                    elif field in ('probes', 'achievements', 'quests'):
                        udata[field] = {}
                    elif field in ('radars',):
                        udata[field] = []
                    elif field in ('last_daily', 'last_quest_reset', 'vip_expires', 'mute_until'):
                        udata[field] = None
                    elif field in ('banned', 'muted', 'frozen', 'blocked'):
                        udata[field] = False
                    elif field == 'current_car':
                        udata[field] = 'SCOUT'
                    elif field == 'current_radar':
                        udata[field] = None
                    else:
                        udata[field] = 0
    except Exception as e:
        logger.error(f'Ошибка загрузки: {e}')

def sync_save():
    try:
        loop = asyncio.get_running_loop()
        if loop and loop.is_running():
            asyncio.create_task(save_data())
        else:
            asyncio.run(save_data())
    except:
        pass

atexit.register(sync_save)

async def auto_save():
    while True:
        await asyncio.sleep(AUTO_SAVE_INTERVAL)
        await save_data()

# ==================== БЛОК-ЧЕК ====================
def block_check(func):
    async def wrapper(update, context, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if is_blocked(user_id):
            try:
                await update.message.delete()
                keyboard = [[InlineKeyboardButton("📩 Связаться", callback_data=f"support||{user_id}")]]
                await update.message.reply_text(
                    f'🚫 ВЫ ЗАБЛОКИРОВАНЫ!\n📌 {get_block_reason(user_id)}\n👤 {OWNER_USERNAME}',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# ==================== АНТИ-СПАМ ====================
async def check_spam(update, context):
    user_id = str(update.effective_user.id)
    now = time.time()
    if user_id not in user_msg_times:
        user_msg_times[user_id] = []
    user_msg_times[user_id] = [t for t in user_msg_times[user_id] if now - t < 2]
    user_msg_times[user_id].append(now)
    if len(user_msg_times[user_id]) > 4:
        try:
            await update.message.delete()
        except:
            pass
        if user_id not in user_warn_count:
            user_warn_count[user_id] = 0
        user_warn_count[user_id] += 1
        warn = user_warn_count[user_id]
        if warn == 1:
            await update.message.reply_text(f'⚠️ {update.effective_user.first_name}, флуд!')
        elif warn == 2:
            try:
                until = datetime.datetime.now() + datetime.timedelta(minutes=10)
                await update.effective_chat.restrict_member(update.effective_user.id, ChatPermissions(can_send_messages=False), until_date=until)
                await update.message.reply_text(f'🔇 {update.effective_user.first_name} замучен на 10 мин')
                user = get_user(user_id)
                if user:
                    user['muted'] = True
            except:
                pass
        elif warn >= 3:
            try:
                until = datetime.datetime.now() + datetime.timedelta(minutes=30)
                await update.effective_chat.ban_member(update.effective_user.id, until_date=until)
                await update.message.reply_text(f'🔨 {update.effective_user.first_name} забанен на 30 мин')
                user = get_user(user_id)
                if user:
                    user['banned'] = True
                user_warn_count[user_id] = 0
            except:
                pass
        await save_data()
        return True
    return False

# ==================== РАЗРУШЕНИЕ ====================
async def breakdown_check():
    today = datetime.date.today().isoformat()
    for user_id, user in user_data.items():
        last = last_breakdown_check.get(user_id)
        if not last:
            last_breakdown_check[user_id] = today
            continue
        try:
            last_date = datetime.date.fromisoformat(last)
            days = (datetime.date.today() - last_date).days
        except:
            last_breakdown_check[user_id] = today
            continue
        if days >= 4:
            broken = []
            cars = user.get('cars_owned', ['SCOUT'])
            if len(cars) > 1:
                old = [c for c in cars if c not in ['SCOUT', 'Chevy 454ss', 'F-150']]
                if old:
                    user['cars_owned'] = ['SCOUT']
                    user['current_car'] = 'SCOUT'
                    for c in old:
                        broken.append(f"🚗 {CARS.get(c, {}).get('name', c)}")
            probes = user.get('probes', {})
            if probes:
                for p in list(probes.keys()):
                    broken.append(f"☂️ {PROBES.get(p, {}).get('name', p)}")
                user['probes'] = {}
            radars = user.get('radars', [])
            if radars:
                for r in radars:
                    broken.append(f"🛰️ {RADARS.get(r, {}).get('name', r)}")
                user['radars'] = []
                user['current_radar'] = None
            if broken and bot_instance:
                try:
                    await bot_instance.bot.send_message(int(user_id), f"💥 СЛОМАЛИСЬ! (4 дня)\n" + "\n".join(broken) + "\n\n🔄 Купи новые!")
                except:
                    pass
            last_breakdown_check[user_id] = today
            await save_data()

async def breakdown_loop():
    while True:
        await asyncio.sleep(21600)
        try:
            await breakdown_check()
        except Exception as e:
            logger.error(f'Ошибка разрушения: {e}')

# ==================== БАН-ЧАТЫ ====================
async def check_ban_chats(update, context, user_id):
    for chat_link in BAN_CHATS:
        try:
            chat_username = chat_link.split('/')[-1]
            chat_info = await context.bot.get_chat(f"@{chat_username}")
            member = await context.bot.get_chat_member(chat_info.id, int(user_id))
            if member.status not in ['left', 'kicked']:
                user = get_user(user_id)
                if user and not user.get('muted', False):
                    user['muted'] = True
                    await save_data()
                    try:
                        await context.bot.restrict_member(update.effective_chat.id, int(user_id), ChatPermissions(can_send_messages=False))
                    except:
                        pass
                    keyboard = [
                        [InlineKeyboardButton("🔇 Размутить", callback_data=f"unmute||{user_id}")],
                        [InlineKeyboardButton("⏳ Оставить", callback_data=f"keep||{user_id}")]
                    ]
                    await update.message.reply_text(
                        f"🚫 **АВТОМАТИЧЕСКИЙ МУТ!**\n👤 {update.effective_user.full_name}\n📌 Причина: участие в {chat_link}",
                        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN
                    )
                    try:
                        await context.bot.send_message(OWNER_ID, f"🚫 **АВТОМУТ!**\n👤 {update.effective_user.full_name} (ID: {user_id})\n📌 {chat_link}")
                    except:
                        pass
                return
        except:
            pass

# ==================== КОМАНДЫ ====================
@block_check
async def start(update, context):
    user_id = str(update.effective_user.id)
    ensure_user(user_id, update.effective_user.full_name, update.effective_user.username)
    await check_ban_chats(update, context, user_id)
    user = get_user(user_id)
    await update.message.reply_text(
        f"🌪️ **STORM CHASER — TWISTED EDITION** 🌪️\n\n"
        f"🚗 SCOUT — бесплатно!\n💰 ${user.get('balance', 5000):,}\n\n"
        f"📝 /help — команды\n🌪️ /intercept — охота\n🎁 /daily — бонус",
        parse_mode=ParseMode.MARKDOWN
    )

@block_check
async def help_command(update, context):
    await update.message.reply_text(
        "🌪️ **STORM CHASER — TWISTED EDITION** 🌪️\n\n"
        "⚡ **ОСНОВНЫЕ КОМАНДЫ:**\n"
        "/intercept — начать охоту\n"
        "/daily — ежедневный бонус\n"
        "/profile — твой профиль\n"
        "/balance — баланс\n"
        "/level — уровень и XP\n"
        "/stats — полная статистика\n\n"
        "🚗 **МАШИНЫ:**\n"
        "/shop_cars — магазин машин\n"
        "/buy_car <название> — купить машину\n"
        "/my_cars — мои машины\n"
        "/wear <название> — надеть машину\n"
        "/sell_car <название> — продать машину\n\n"
        "📡 **РАДАРЫ:**\n"
        "/shop_radars — магазин радаров\n"
        "/buy_radar <название> — купить радар\n"
        "/my_radars — мои радары\n"
        "/wear_radar <название> — надеть радар\n\n"
        "☂️ **ЗОНДЫ:**\n"
        "/shop_probes — магазин зондов\n"
        "/buy_probe <название> — купить зонд\n"
        "/my_probes — мои зонды\n\n"
        "💰 **ЭКОНОМИКА:**\n"
        "/buy_money <звёзды> — купить деньги\n"
        "/buy_vip [период] — купить VIP\n"
        "/vip — статус VIP\n\n"
        "🔨 **МОДЕРАЦИЯ (ответ на сообщение):**\n"
        "/mute [время] — замутить\n"
        "/unmute — размутить\n"
        "/warn — предупреждение\n"
        "/unwarn — снять предупреждение\n"
        "/ban [время] — забанить\n"
        "/banofdeath — бан навсегда\n"
        "/unban <ID> — разбанить\n"
        "/kick — выгнать\n"
        "/mute_admin [время] — замутить админа\n"
        "/unmute_admin — размутить админа\n\n"
        "👑 **ВЛАДЕЛЕЦ:**\n"
        "/block [причина] — добавить в ЧС\n"
        "/unblock <ID> — убрать из ЧС\n"
        "/block_list — список ЧС\n"
        "/promote <ID> <уровень> — повысить (1-4)\n"
        "/demote <ID> — сбросить ранг\n"
        "/approve_admin <ID> — дать права\n"
        "/unapprove_admin <ID> — снять права\n"
        "/say <ID> <текст> — отправить в чат\n"
        "/say_all <текст> — во все чаты\n"
        "/chats — список чатов\n"
        "/check_chat <ID> — сообщения в чате\n"
        "/check_chat_all <ID> — все сообщения\n"
        "/add_interceptor <название> <цена> <выносливость> — добавить машину\n"
        "/remove_interceptor <название> — удалить машину\n"
        "/join <ссылка> — добавить бота в чат\n"
        "/clean [кол-во] — удалить сообщения\n\n"
        "📋 **ИНФО:**\n"
        "/rules — правила чата\n"
        "/staff — сотрудники\n"
        "/help — помощь",
        parse_mode=ParseMode.MARKDOWN
    )

@block_check
async def profile(update, context):
    u = get_user(str(update.effective_user.id))
    if not u:
        return await update.message.reply_text('❌ Профиль не найден')
    ranks = {0:'Пользователь', 1:'Мл. модер', 2:'Ср. модер', 3:'Ст. модер', 4:'Создатель'}
    xp = u.get('xp', 0)
    xp_to = u.get('xp_to_next', 100)
    pct = int((xp / xp_to) * 100) if xp_to > 0 else 0
    vip = "✅" if is_vip(str(update.effective_user.id)) else "❌"
    clan = u.get('clan', 'Нет')
    prof = u.get('profession', 'Нет')
    await update.message.reply_text(
        f"🌪️ **ПРОФИЛЬ ОХОТНИКА** 🌪️\n\n"
        f"👤 Имя: {u.get('first_name', '')} {u.get('last_name', '')}\n"
        f"📊 Ранг: {ranks.get(u.get('rank', 0), 'Неизвестно')}\n"
        f"⭐ Уровень: {u.get('level', 1)} (XP: {xp}/{xp_to} • {pct}%)\n"
        f"💰 Баланс: ${u.get('balance', 0):,}\n"
        f"🚗 Машина: {u.get('current_car', 'SCOUT')}\n"
        f"🛰️ Радар: {u.get('current_radar', 'Нет')}\n"
        f"☂️ Зонды: {len(u.get('probes', {}))} шт.\n"
        f"⭐ VIP: {vip}\n"
        f"🏛️ Клан: {clan}\n"
        f"💼 Профессия: {prof}\n\n"
        f"📈 **СТАТИСТИКА:**\n"
        f"🎯 Перехватов: {u.get('total_intercepts', 0)}\n"
        f"✅ Успешных: {u.get('successful_intercepts', 0)}\n"
        f"📡 Сканирований: {u.get('total_scans', 0)}\n"
        f"💀 Уничтожено торнадо: {u.get('storm_kills', 0)}\n"
        f"🔥 Серия: {u.get('streak', 0)} (рекорд: {u.get('best_streak', 0)})\n"
        f"🏆 Наград: {u.get('awards', 0)}\n"
        f"⚠️ Варнов: {u.get('warned', 0)}",
        parse_mode=ParseMode.MARKDOWN
    )

@block_check
async def balance(update, context):
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    await update.message.reply_text(f'💰 **Баланс:** ${user.get("balance", 0):,}', parse_mode=ParseMode.MARKDOWN)

@block_check
async def level_command(update, context):
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    xp = user.get('xp', 0)
    xp_to = user.get('xp_to_next', 100)
    pct = int((xp / xp_to) * 100) if xp_to > 0 else 0
    await update.message.reply_text(
        f"⭐ **УРОВЕНЬ ОХОТНИКА** ⭐\n\n"
        f"Уровень: {user.get('level', 1)}\n"
        f"XP: {xp}/{xp_to} ({pct}%)\n\n"
        f"📊 **Прогресс:**\n"
        f"{'█' * int(pct // 5)}{'░' * int(20 - pct // 5)}",
        parse_mode=ParseMode.MARKDOWN
    )

@block_check
async def stats_command(update, context):
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    await update.message.reply_text(
        f"📊 **СТАТИСТИКА ОХОТНИКА** 📊\n\n"
        f"🎯 Перехватов: {user.get('total_intercepts', 0)}\n"
        f"✅ Успешных: {user.get('successful_intercepts', 0)}\n"
        f"📡 Сканирований: {user.get('total_scans', 0)}\n"
        f"💀 Уничтожено торнадо: {user.get('storm_kills', 0)}\n"
        f"🔥 Серия: {user.get('streak', 0)}\n"
        f"🏆 Рекорд серии: {user.get('best_streak', 0)}\n"
        f"📝 Сообщений: {user.get('messages_total', 0)}\n"
        f"🏆 Наград: {user.get('awards', 0)}",
        parse_mode=ParseMode.MARKDOWN
    )

@block_check
async def top_command(update, context):
    top_users = []
    for uid, data in user_data.items():
        if data.get('level', 0) > 0:
            top_users.append((uid, data.get('level', 0), data.get('first_name', uid), data.get('balance', 0)))
    top_users.sort(key=lambda x: x[1], reverse=True)
    top_users = top_users[:10]
    if not top_users:
        return await update.message.reply_text('📊 Нет данных для топа')
    text = "🏆 **ТОП ОХОТНИКОВ** 🏆\n\n"
    for i, (uid, level, name, balance) in enumerate(top_users, 1):
        medal = ['🥇', '🥈', '🥉'][i - 1] if i <= 3 else f'{i}.'
        text += f"{medal} **{name}** — Уровень {level} (💰 ${balance:,})\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== ЕЖЕДНЕВНЫЙ БОНУС ====================
@block_check
async def daily(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    today = datetime.date.today().isoformat()
    last = user.get('last_daily')
    if last == today:
        return await update.message.reply_text('🎁 Ты уже забирал бонус сегодня! Приходи завтра.')
    if last:
        try:
            last_date = datetime.date.fromisoformat(last)
            if (datetime.date.today() - last_date).days == 1:
                user['daily_streak'] = user.get('daily_streak', 0) + 1
            else:
                user['daily_streak'] = 1
        except:
            user['daily_streak'] = 1
    else:
        user['daily_streak'] = 1
    streak = min(user.get('daily_streak', 1), 7)
    bonuses = {1: 15000, 2: 20000, 3: 30000, 4: 40000, 5: 55000, 6: 75000, 7: 100000}
    base = bonuses.get(streak, 15000)
    bonus = int(base * get_vip_multiplier(user_id))
    user['balance'] = user.get('balance', 0) + bonus
    user['last_daily'] = today
    extra = 0
    if streak == 7:
        extra = 100000
        user['balance'] += extra
        user['daily_streak'] = 0
    await save_data()
    text = f"🎁 **ЕЖЕДНЕВНЫЙ БОНУС!**\n\n📅 День: {streak}/7\n💰 Получено: ${bonus:,}\n🔥 Серия: {streak} дней\n⭐ VIP бонус: x{get_vip_multiplier(user_id)}\n"
    if extra:
        text += f"🏆 **БОНУС ЗА 7 ДНЕЙ!** +${extra:,}\n"
    text += f"💰 Новый баланс: ${user['balance']:,}"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== МАГАЗИН МАШИН ====================
@block_check
async def shop_cars(update, context):
    text = "🚗 **МАГАЗИН МАШИН** 🚗\n\n"
    for k, c in CARS.items():
        if c['price'] == 0:
            text += f"{c['name']} — **БЕСПЛАТНО**\n"
        else:
            text += f"{c['name']} — 💰 ${c['price']:,}\n"
        text += f"   💪 Выносливость: {c['max_speed']} mph\n"
        text += f"   🛡️ HP: {c['hp']}\n"
        if c['fixation'] > 0:
            text += f"   🔒 Фиксация: {c['fixation']} сек\n"
        text += f"   📝 {c['desc']}\n\n"
    text += "📝 **/buy_car <название>** — купить машину\n"
    text += "📝 **/sell_car <название>** — продать машину (50% цены)"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def buy_car(update, context):
    if not context.args:
        return await update.message.reply_text('📝 **/buy_car Dominator 1**\n\nДоступные машины:\n• Dom-1\n• Dom-2\n• Dom-3\n• Tiv-1\n• Tiv-2\n• Tornado Attack\n• Dorothy\n• Tornado Puncher\n• Titus\n• StormBreaker\n• Thunder\n• Cyclone')
    name = ' '.join(context.args).strip()
    found = None
    for k in CARS:
        if k.lower() == name.lower():
            found = k
            break
    if not found or found == 'civil':
        return await update.message.reply_text(f'❌ Машина "{name}" не найдена')
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    car = CARS[found]
    if user.get('balance', 0) < car['price']:
        return await update.message.reply_text(f'❌ Нужно ${car["price"]:,}. У тебя ${user["balance"]:,}')
    if found in user.get('cars_owned', []):
        return await update.message.reply_text('❌ У тебя уже есть эта машина!')
    user['balance'] -= car['price']
    user['cars_owned'].append(found)
    user['current_car'] = found
    await save_data()
    await update.message.reply_text(f'✅ **Куплена {car["name"]}** за ${car["price"]:,}\n💰 Баланс: ${user["balance"]:,}')

@block_check
async def sell_car(update, context):
    if not context.args:
        return await update.message.reply_text('📝 **/sell_car Dominator 1**')
    name = ' '.join(context.args).strip()
    found = None
    for k in CARS:
        if k.lower() == name.lower():
            found = k
            break
    if not found or found == 'civil':
        return await update.message.reply_text(f'❌ Машина "{name}" не найдена')
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    if found not in user.get('cars_owned', []):
        return await update.message.reply_text('❌ У тебя нет этой машины')
    if len(user.get('cars_owned', [])) <= 1:
        return await update.message.reply_text('❌ Нельзя продать последнюю машину!')
    car = CARS[found]
    price = int(car['price'] * 0.5)
    user['balance'] += price
    user['cars_owned'].remove(found)
    if user.get('current_car') == found:
        user['current_car'] = user['cars_owned'][0] if user['cars_owned'] else 'SCOUT'
    await save_data()
    await update.message.reply_text(f'✅ **Продана {car["name"]}** за ${price:,}\n💰 Баланс: ${user["balance"]:,}')

@block_check
async def my_cars(update, context):
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    owned = user.get('cars_owned', ['SCOUT'])
    if not owned or owned == ['SCOUT']:
        return await update.message.reply_text('🚫 У тебя нет машин')
    current = user.get('current_car', 'SCOUT')
    text = "🏎️ **ТВОИ МАШИНЫ:**\n\n"
    for key in owned:
        car = CARS.get(key)
        if not car:
            continue
        marker = ' ✅ ТЕКУЩАЯ' if key == current else ''
        speed = car.get('max_speed', 'случайная')
        text += f"{car['name']}{marker}\n"
        text += f"   💪 {speed} mph\n\n"
    text += "📝 **/wear <название>** — надеть машину"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def wear_car(update, context):
    if not context.args:
        return await update.message.reply_text('📝 **/wear Dominator 1**')
    name = ' '.join(context.args).strip()
    found = None
    for k in CARS:
        if k.lower() == name.lower():
            found = k
            break
    if not found:
        return await update.message.reply_text('❌ Машина не найдена')
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    if found not in user.get('cars_owned', []):
        return await update.message.reply_text('❌ У тебя нет этой машины')
    user['current_car'] = found
    await save_data()
    await update.message.reply_text(f'✅ **Текущая машина:** {CARS[found]["name"]}')

# ==================== МАГАЗИН РАДАРОВ ====================
@block_check
async def shop_radars(update, context):
    text = "🛰️ **МАГАЗИН РАДАРОВ** 🛰️\n\n"
    for k, r in RADARS.items():
        text += f"{r['name']} — 💰 ${r['price']:,}\n"
        text += f"   🎯 Точность: {int(r['accuracy'] * 100)}%\n"
        text += f"   📡 Тип: {r['type']}\n"
        text += f"   📝 {r['desc']}\n\n"
    text += "📝 **/buy_radar <название>** — купить радар"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def buy_radar(update, context):
    if not context.args:
        return await update.message.reply_text('📝 **/buy_radar KHZL**')
    name = ' '.join(context.args).strip()
    found = None
    for k in RADARS:
        if k.lower() == name.lower():
            found = k
            break
    if not found:
        return await update.message.reply_text('❌ Радар не найден')
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    radar = RADARS[found]
    if user.get('balance', 0) < radar['price']:
        return await update.message.reply_text(f'❌ Нужно ${radar["price"]:,}. У тебя ${user["balance"]:,}')
    if found in user.get('radars', []):
        return await update.message.reply_text('❌ У тебя уже есть этот радар!')
    user['balance'] -= radar['price']
    user['radars'].append(found)
    if not user.get('current_radar'):
        user['current_radar'] = found
    await save_data()
    await update.message.reply_text(f'✅ **Куплен {radar["name"]}** за ${radar["price"]:,}')

@block_check
async def my_radars(update, context):
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    radars = user.get('radars', [])
    if not radars:
        return await update.message.reply_text('🚫 Нет радаров')
    current = user.get('current_radar')
    text = "🛰️ **ТВОИ РАДАРЫ:**\n\n"
    for r in radars:
        radar = RADARS.get(r)
        if not radar:
            continue
        marker = ' ✅ АКТИВНЫЙ' if r == current else ''
        text += f"{radar['name']}{marker}\n"
        text += f"   🎯 Точность: {int(radar['accuracy'] * 100)}%\n\n"
    text += "📝 **/wear_radar <название>** — надеть радар"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def wear_radar(update, context):
    if not context.args:
        return await update.message.reply_text('📝 **/wear_radar KHZL**')
    name = ' '.join(context.args).strip()
    found = None
    for k in RADARS:
        if k.lower() == name.lower():
            found = k
            break
    if not found:
        return await update.message.reply_text('❌ Радар не найден')
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    if found not in user.get('radars', []):
        return await update.message.reply_text('❌ У тебя нет этого радара')
    user['current_radar'] = found
    await save_data()
    await update.message.reply_text(f'✅ **Активный радар:** {RADARS[found]["name"]}')

# ==================== МАГАЗИН ЗОНДОВ ====================
@block_check
async def shop_probes(update, context):
    text = "☂️ **МАГАЗИН ЗОНДОВ** ☂️\n\n"
    for k, p in PROBES.items():
        text += f"{p['name']} — 💰 ${p['price']:,}\n"
        text += f"   💪 HP: {p['max_hp']}\n"
        text += f"   🎯 Бонус: x{p['bonus']}\n"
        text += f"   📝 {p['desc']}\n\n"
    text += "📝 **/buy_probe <название>** — купить зонд"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def buy_probe(update, context):
    if not context.args:
        return await update.message.reply_text('📝 **/buy_probe "Twisted Probe"**')
    name = ' '.join(context.args).strip()
    found = None
    for k in PROBES:
        if k.lower() == name.lower():
            found = k
            break
    if not found:
        return await update.message.reply_text('❌ Зонд не найден')
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    probe = PROBES[found]
    if user.get('balance', 0) < probe['price']:
        return await update.message.reply_text(f'❌ Нужно ${probe["price"]:,}. У тебя ${user["balance"]:,}')
    if found in user.get('probes', {}):
        return await update.message.reply_text('❌ У тебя уже есть этот зонд!')
    user['probes'][found] = probe['max_hp']
    user['balance'] -= probe['price']
    await save_data()
    await update.message.reply_text(f'✅ **Куплен {probe["name"]}** за ${probe["price"]:,}')

@block_check
async def my_probes(update, context):
    user = get_user(str(update.effective_user.id))
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    probes = user.get('probes', {})
    if not probes:
        return await update.message.reply_text('🚫 Нет зондов')
    text = "☂️ **ТВОИ ЗОНДЫ:**\n\n"
    for pkey, hp in probes.items():
        probe = PROBES.get(pkey)
        if not probe:
            continue
        text += f"{probe['name']}\n"
        text += f"   💪 HP: {hp}/{probe['max_hp']}\n"
        text += f"   🎯 Бонус: x{probe['bonus']}\n\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== VIP СИСТЕМА ====================
@block_check
async def buy_vip(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    if not context.args:
        return await update.message.reply_text(
            "⭐ **ПОКУПКА VIP** ⭐\n\n"
            "📝 /buy_vip [период]\n\n"
            "Доступные периоды:\n"
            "• 1д — 1 день ($25,000)\n"
            "• 7д — 7 дней ($150,000)\n"
            "• 30д — 30 дней ($500,000)\n"
            "• forever — НАВСЕГДА ($2,000,000)\n\n"
            f"💰 Твой баланс: ${user.get('balance', 0):,}",
            parse_mode=ParseMode.MARKDOWN
        )
    period = context.args[0].lower()
    prices = {'1d': (25000, 1), '7d': (150000, 7), '30d': (500000, 30), 'forever': (2000000, 9999)}
    if period not in prices:
        return await update.message.reply_text('❌ Неверный период. Используй: 1д, 7д, 30д, forever')
    price, days = prices[period]
    if user.get('balance', 0) < price:
        return await update.message.reply_text(f'❌ Нужно ${price:,}. У тебя ${user["balance"]:,}')
    user['balance'] -= price
    if days == 9999:
        user['vip_expires'] = "9999-12-31"
    else:
        expire_date = datetime.datetime.now() + datetime.timedelta(days=days)
        user['vip_expires'] = expire_date.isoformat()
    await save_data()
    text = f"⭐ **VIP КУПЛЕН!** ⭐\n\n"
    text += f"💰 Снято: ${price:,}\n"
    text += f"📅 Период: {days if days < 9999 else 'НАВСЕГДА'} дней\n"
    text += f"💰 Новый баланс: ${user['balance']:,}\n\n"
    text += "🔥 **Бонусы VIP:**\n"
    text += "• x1.5 к ежедневному бонусу\n"
    text += "• x1.2 к награде за перехват\n"
    text += "• x1.5 к награде за сканирование\n"
    text += "• Эксклюзивные скины\n"
    text += "• Приоритет в очереди"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def vip_status(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    vip_active = is_vip(user_id)
    vip_expires = user.get('vip_expires')
    text = "⭐ **VIP СТАТУС** ⭐\n\n"
    if vip_active:
        text += "Статус: ✅ **АКТИВЕН**\n"
        if vip_expires and vip_expires != "9999-12-31":
            try:
                expire_date = datetime.datetime.fromisoformat(vip_expires)
                days_left = (expire_date - datetime.datetime.now()).days
                text += f"Осталось: {days_left} дней\n"
            except:
                pass
        else:
            text += "⏳ **НАВСЕГДА!**\n"
        text += "\n🔥 **Активные бонусы:**\n"
        text += "• x1.5 к ежедневному бонусу\n"
        text += "• x1.2 к награде за перехват\n"
        text += "• x1.5 к награде за сканирование\n"
    else:
        text += "Статус: ❌ **Нет**\n\n"
        text += "📝 **/buy_vip [период]** — купить VIP\n"
        text += "• 1д — $25,000\n"
        text += "• 7д — $150,000\n"
        text += "• 30д — $500,000\n"
        text += "• forever — $2,000,000"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== ПОКУПКА ЗА ЗВЁЗДЫ ====================
@block_check
async def buy_money(update, context):
    text = "⭐ **ПОКУПКА ДЕНЕГ ЗА ЗВЁЗДЫ** ⭐\n\n"
    for p in STAR_PACKAGES:
        text += f"⭐ {p['stars']} → 💰 {p['money']:,} $\n"
    text += "\n📝 **/buy_money <звёзды>** — купить\n\n"
    text += f"👤 Владелец: {OWNER_USERNAME}\n"
    text += "⏳ После отправки запроса, владелец подтвердит покупку."
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def buy_money_cmd(update, context):
    if not context.args:
        return await update.message.reply_text('📝 **/buy_money 10**')
    try:
        stars = int(context.args[0])
    except:
        return await update.message.reply_text('❌ Введите число')
    found = None
    for p in STAR_PACKAGES:
        if p['stars'] == stars:
            found = p
            break
    if not found:
        text = "❌ Нет такого пакета.\n\nДоступные:\n"
        for p in STAR_PACKAGES:
            text += f"⭐ {p['stars']} → 💰 {p['money']:,} $\n"
        return await update.message.reply_text(text)
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    pending_purchases[user_id] = {'stars': stars, 'money': found['money'], 'timestamp': time.time(), 'name': update.effective_user.full_name}
    await save_data()
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm||{user_id}")],
        [InlineKeyboardButton("❌ Отказать", callback_data=f"deny||{user_id}")]
    ]
    try:
        await context.bot.send_message(
            OWNER_ID,
            f"💰 **ЗАПРОС НА ПОКУПКУ!**\n\n"
            f"👤 Пользователь: {update.effective_user.full_name}\n"
            f"🆔 ID: {user_id}\n"
            f"⭐ Звёзд: {stars}\n"
            f"💰 Сумма: {found['money']:,}$",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN
        )
    except:
        pass
    await update.message.reply_text(f"✅ Запрос отправлен!\n⭐ {stars} → 💰 {found['money']:,}$")

# ==================== ОБРАБОТЧИКИ СООБЩЕНИЙ ====================
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        if user.is_bot:
            chat_id = str(update.effective_chat.id)
            bot_chats.add(chat_id)
            await save_data()
            await update.message.reply_text(f"👋 Привет! Я Storm Chaser. Используй /help для команд")
        else:
            user_id = str(user.id)
            ensure_user(user_id, user.full_name, user.username)

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    chat_id = str(update.effective_chat.id)
    text = update.message.text or update.message.caption or "[медиа]"
    
    ensure_user(user_id, update.effective_user.full_name, update.effective_user.username)
    user = get_user(user_id)
    if user:
        user['messages_total'] += 1
        user['messages_today'] += 1
    
    if chat_id not in chat_messages:
        chat_messages[chat_id] = []
    chat_messages[chat_id].append({'user_id': user_id, 'text': text[:50], 'msg_id': update.message.message_id})
    
    if chat_id not in chat_user_stats:
        chat_user_stats[chat_id] = {}
    if user_id not in chat_user_stats[chat_id]:
        chat_user_stats[chat_id][user_id] = 0
    chat_user_stats[chat_id][user_id] += 1
    
    await check_spam(update, context)
    await save_data()

async def support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('||')
    action = data[0]
    
    if action == 'support':
        user_id = data[1] if len(data) > 1 else str(update.effective_user.id)
        try:
            await context.bot.send_message(int(user_id), f"📩 Владелец: {OWNER_USERNAME}\n🔗 {OWNER_CHANNEL}")
        except:
            pass
    elif action == 'confirm':
        user_id = data[1] if len(data) > 1 else str(update.effective_user.id)
        if user_id in pending_purchases:
            purchase = pending_purchases[user_id]
            user = get_user(user_id)
            if user:
                user['balance'] = user.get('balance', 0) + purchase['money']
                await save_data()
            try:
                await context.bot.send_message(int(user_id), f"✅ Покупка подтверждена!\n💰 +${purchase['money']:,}")
            except:
                pass
            del pending_purchases[user_id]
    elif action == 'deny':
        user_id = data[1] if len(data) > 1 else str(update.effective_user.id)
        if user_id in pending_purchases:
            try:
                await context.bot.send_message(int(user_id), f"❌ Покупка отклонена")
            except:
                pass
            del pending_purchases[user_id]

# ==================== МОДЕРАЦИЯ ====================
async def get_target(update, context):
    if update.message.reply_to_message:
        u = update.message.reply_to_message.from_user
        return str(u.id), u.full_name, u.username
    if context.args:
        arg = context.args[0]
        if arg.startswith('@'):
            username = arg[1:]
            for uid, data in user_data.items():
                if data.get('username') == username:
                    return uid, f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or username, username
            return None, None, None
        try:
            uid = str(int(arg))
            user = get_user(uid)
            if user:
                return uid, f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get('username') or uid, user.get('username')
            ensure_user(uid, f'User {uid}')
            return uid, f'User {uid}', None
        except:
            return None, None, None
    return None, None, None

def get_time(context):
    if len(context.args) > 1:
        seconds = parse_time(context.args[1])
        if seconds > 0:
            return seconds, format_time(seconds)
    return 0, "навсегда"

@block_check
async def mute(update, context):
    if not can_mute(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав (ранг >= 1)')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение или укажите ID')
    sec, t = get_time(context)
    try:
        if sec > 0:
            until = datetime.datetime.now() + datetime.timedelta(seconds=sec)
            await update.effective_chat.restrict_member(int(target_id), ChatPermissions(can_send_messages=False), until_date=until)
            await update.message.reply_text(f'🔇 {name} замучен на {t}')
        else:
            await update.effective_chat.restrict_member(int(target_id), ChatPermissions(can_send_messages=False))
            await update.message.reply_text(f'🔇 {name} замучен навсегда')
        user = get_user(target_id)
        if user:
            user['muted'] = True
        await save_data()
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

@block_check
async def unmute(update, context):
    if not can_mute(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение или укажите ID')
    try:
        await update.effective_chat.restrict_member(int(target_id), ChatPermissions(can_send_messages=True))
        user = get_user(target_id)
        if user:
            user['muted'] = False
        await save_data()
        await update.message.reply_text(f'✅ {name} размучен')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

@block_check
async def ban(update, context):
    if not can_ban(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав (ранг >= 3)')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение или укажите ID')
    sec, t = get_time(context)
    try:
        if sec > 0:
            until = datetime.datetime.now() + datetime.timedelta(seconds=sec)
            await update.effective_chat.ban_member(int(target_id), until_date=until)
            await update.message.reply_text(f'🔨 {name} забанен на {t}')
        else:
            await update.effective_chat.ban_member(int(target_id))
            await update.message.reply_text(f'🔨 {name} забанен навсегда')
        user = get_user(target_id)
        if user:
            user['banned'] = True
        await save_data()
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

@block_check
async def banofdeath(update, context):
    if not is_owner_or_creator(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец или создатель')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение или укажите ID')
    try:
        await update.effective_chat.ban_member(int(target_id))
        user = get_user(target_id)
        if user:
            user['banned'] = True
        await save_data()
        await update.message.reply_text(f'💀 {name} забанен навсегда')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

@block_check
async def unban(update, context):
    if not can_ban(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    if not context.args:
        return await update.message.reply_text('📝 /unban 123456789')
    try:
        uid = int(context.args[0])
        await update.effective_chat.unban_member(uid)
        user = get_user(str(uid))
        if user:
            user['banned'] = False
        await save_data()
        await update.message.reply_text('✅ Пользователь разбанен')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

@block_check
async def warn(update, context):
    if not can_warn(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав (ранг >= 2)')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение или укажите ID')
    user = get_user(target_id)
    if not user:
        ensure_user(target_id, name)
        user = get_user(target_id)
    user['warned'] = user.get('warned', 0) + 1
    warns = user['warned']
    chat = update.effective_chat
    if warns == 1:
        await update.message.reply_text(f'⚠️ {name} предупреждение (1/6)')
    elif warns == 2:
        until = datetime.datetime.now() + datetime.timedelta(minutes=10)
        await chat.restrict_member(int(target_id), ChatPermissions(can_send_messages=False), until_date=until)
        await update.message.reply_text(f'⚠️ {name} Варн 2/6. Мут 10 минут')
    elif warns == 3:
        until = datetime.datetime.now() + datetime.timedelta(hours=1)
        await chat.restrict_member(int(target_id), ChatPermissions(can_send_messages=False), until_date=until)
        await update.message.reply_text(f'⚠️ {name} Варн 3/6. Мут 1 час')
    elif warns == 4:
        until = datetime.datetime.now() + datetime.timedelta(days=1)
        await chat.restrict_member(int(target_id), ChatPermissions(can_send_messages=False), until_date=until)
        await update.message.reply_text(f'⚠️ {name} Варн 4/6. Мут 1 день')
    elif warns == 5:
        until = datetime.datetime.now() + datetime.timedelta(days=7)
        await chat.ban_member(int(target_id), until_date=until)
        await update.message.reply_text(f'⚠️ {name} Варн 5/6. Бан 7 дней')
    elif warns >= 6:
        until = datetime.datetime.now() + datetime.timedelta(days=30)
        await chat.ban_member(int(target_id), until_date=until)
        user['warned'] = 0
        await update.message.reply_text(f'⚠️ {name} Варн 6/6. Бан 1 месяц')
    await save_data()

@block_check
async def unwarn(update, context):
    if not can_warn(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение или укажите ID')
    user = get_user(target_id)
    if not user:
        return await update.message.reply_text('❌ Пользователь не найден')
    if user.get('warned', 0) <= 0:
        return await update.message.reply_text('❌ У пользователя нет варнов')
    user['warned'] = user.get('warned', 0) - 1
    await save_data()
    await update.message.reply_text(f'✅ Снято предупреждение у {name}. Осталось: {user["warned"]}')

@block_check
async def resetwarns(update, context):
    if not can_warn(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение или укажите ID')
    user = get_user(target_id)
    if not user:
        return await update.message.reply_text('❌ Пользователь не найден')
    user['warned'] = 0
    await save_data()
    await update.message.reply_text(f'✅ Варны пользователя {name} сброшены')

@block_check
async def warn_list(update, context):
    if not can_warn(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    warned = [(uid, data.get('warned', 0)) for uid, data in user_data.items() if data.get('warned', 0) > 0]
    if not warned:
        return await update.message.reply_text('📊 Нет пользователей с варнами')
    warned.sort(key=lambda x: x[1], reverse=True)
    text = '⚠️ **СПИСОК ВАРНОВ:**\n\n'
    for uid, w in warned:
        user = get_user(uid)
        name = user.get('first_name', uid) if user else uid
        text += f"• {name} — {w} предупреждений\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def ban_list(update, context):
    if not can_ban(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    banned = [uid for uid, data in user_data.items() if data.get('banned', False)]
    if not banned:
        return await update.message.reply_text('📊 Нет забаненных')
    text = '🔨 **ЗАБАНЕННЫЕ:**\n\n'
    for uid in banned:
        user = get_user(uid)
        name = user.get('first_name', uid) if user else uid
        text += f"• {name} (ID: {uid})\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def mute_list(update, context):
    if not can_mute(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    muted = [uid for uid, data in user_data.items() if data.get('muted', False)]
    if not muted:
        return await update.message.reply_text('📊 Нет замученных')
    text = '🔇 **ЗАМУЧЕННЫЕ:**\n\n'
    for uid in muted:
        user = get_user(uid)
        name = user.get('first_name', uid) if user else uid
        text += f"• {name} (ID: {uid})\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def kick(update, context):
    if not can_kick(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав (нужен ранг 2-3)')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение или укажите ID')
    try:
        await update.effective_chat.ban_member(int(target_id))
        await update.effective_chat.unban_member(int(target_id))
        await update.message.reply_text(f'👢 {name} выгнан из чата')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

# ==================== MUTE_ADMIN ====================
@block_check
async def mute_admin(update, context):
    if not can_mute_admin(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец или approved_admin')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение админа или укажите ID')
    if target_id == str(update.effective_user.id):
        return await update.message.reply_text('❌ Нельзя замутить себя')
    target_rank = get_user_rank(target_id)
    if target_rank < 1:
        return await update.message.reply_text('❌ Это не админ. Используйте /mute')
    sec, t = get_time(context)
    try:
        if sec > 0:
            until = datetime.datetime.now() + datetime.timedelta(seconds=sec)
            await update.effective_chat.restrict_member(int(target_id), ChatPermissions(can_send_messages=False), until_date=until)
            await update.message.reply_text(f'🔇 Админ {name} замучен на {t}')
        else:
            await update.effective_chat.restrict_member(int(target_id), ChatPermissions(can_send_messages=False))
            await update.message.reply_text(f'🔇 Админ {name} замучен навсегда')
        user = get_user(target_id)
        if user:
            user['muted'] = True
        await save_data()
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

@block_check
async def unmute_admin(update, context):
    if not can_mute_admin(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец или approved_admin')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('📝 Ответьте на сообщение админа или укажите ID')
    target_rank = get_user_rank(target_id)
    if target_rank < 1:
        return await update.message.reply_text('❌ Это не админ')
    try:
        await update.effective_chat.restrict_member(int(target_id), ChatPermissions(can_send_messages=True))
        user = get_user(target_id)
        if user:
            user['muted'] = False
        await save_data()
        await update.message.reply_text(f'✅ Админ {name} размучен')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

# ==================== АДМИНСКИЕ КОМАНДЫ ====================
@block_check
async def approve_admin(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('❌ Не удалось определить пользователя')
    if target_id not in approved_admins:
        approved_admins.append(target_id)
        await save_data()
        await update.message.reply_text(f'✅ {name} добавлен в список approved_admin')
    else:
        await update.message.reply_text(f'❌ {name} уже в списке')

@block_check
async def unapprove_admin(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('❌ Не удалось определить пользователя')
    if target_id in approved_admins:
        approved_admins.remove(target_id)
        await save_data()
        await update.message.reply_text(f'✅ {name} удалён из списка')
    else:
        await update.message.reply_text(f'❌ {name} не в списке')

@block_check
async def promote(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if len(context.args) < 2:
        return await update.message.reply_text('📝 /promote <ID> <уровень (1-4)>')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('❌ Не удалось определить пользователя')
    try:
        rank = int(context.args[1])
    except:
        return await update.message.reply_text('❌ Уровень должен быть числом (1-4)')
    if rank < 1 or rank > 4:
        return await update.message.reply_text('❌ Уровень от 1 до 4')
    user = get_user(target_id)
    if not user:
        ensure_user(target_id, name)
        user = get_user(target_id)
    user['rank'] = rank
    await save_data()
    rank_names = {1:'Младший модер', 2:'Средний модер', 3:'Старший модер', 4:'Создатель'}
    await update.message.reply_text(f'⭐ {name} повышен до ранга: {rank_names[rank]}')

@block_check
async def demote(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('❌ Не удалось определить пользователя')
    user = get_user(target_id)
    if not user:
        return await update.message.reply_text('❌ Пользователь не найден')
    user['rank'] = 0
    await save_data()
    await update.message.reply_text(f'⬇️ Ранг пользователя {name} сброшен до 0')

# ==================== БЛОКИРОВКА ====================
@block_check
async def block_user_cmd(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    target_id, name, _ = await get_target(update, context)
    if not target_id:
        return await update.message.reply_text('❌ Не удалось определить пользователя')
    if target_id == str(update.effective_user.id):
        return await update.message.reply_text('❌ Нельзя заблокировать себя')
    if is_blocked(target_id):
        return await update.message.reply_text('❌ Уже в ЧС')
    reason = ' '.join(context.args[1:]) if len(context.args) > 1 else 'Неизвестна'
    block_user(target_id, reason)
    ensure_user(target_id, name)
    await update.message.reply_text(f'🚫 {name} добавлен в ЧС\nПричина: {reason}')
    try:
        keyboard = [[InlineKeyboardButton("📩 Связаться с владельцем", callback_data=f"support||{target_id}")]]
        await context.bot.send_message(
            int(target_id),
            f'🚫 ВЫ ЗАБЛОКИРОВАНЫ В БОТЕ!\n\n📌 Причина: {reason}\n\n👤 Владелец: {OWNER_USERNAME}',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        pass

@block_check
async def unblock_user_cmd(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if not context.args:
        return await update.message.reply_text('📝 /unblock 123456789')
    try:
        target_id = str(int(context.args[0]))
    except:
        return await update.message.reply_text('❌ Введите корректный ID')
    if not is_blocked(target_id):
        return await update.message.reply_text('❌ Не в ЧС')
    unblock_user(target_id)
    await update.message.reply_text(f'✅ Пользователь (ID: {target_id}) удалён из ЧС')

@block_check
async def block_list(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if not blocked_users:
        return await update.message.reply_text('📊 Нет заблокированных пользователей')
    text = '🚫 **ЧЕРНЫЙ СПИСОК:**\n\n'
    for uid, data in blocked_users.items():
        user = get_user(uid)
        name = user.get('first_name', uid) if user else uid
        reason = data.get('reason', 'Неизвестна')
        date = data.get('date', 'Неизвестно')
        text += f'• {name} (ID: {uid})\n   Причина: {reason}\n   Дата: {date}\n\n'
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== STAFF ====================
@block_check
async def staff_command(update, context):
    chat_id = str(update.effective_chat.id)
    staff = []
    try:
        admins = await context.bot.get_chat_administrators(int(chat_id))
        for admin in admins:
            uid = str(admin.user.id)
            user = get_user(uid)
            if user:
                rank = user.get('rank', 0)
                if rank >= 1:
                    name = admin.user.full_name or admin.user.username or uid
                    staff.append((uid, rank, name, True))
    except:
        pass
    chat_users = chat_user_stats.get(chat_id, {})
    for uid in chat_users.keys():
        user = get_user(uid)
        if user:
            rank = user.get('rank', 0)
            if rank >= 1:
                if not any(s[0] == uid for s in staff):
                    name = user.get('first_name', '') + user.get('last_name', '')
                    if not name.strip():
                        name = user.get('username', uid)
                    staff.append((uid, rank, name, False))
    if not staff:
        return await update.message.reply_text('📋 В этом чате нет сотрудников.')
    rank_names = {1:'👤 Младший модер', 2:'👤 Средний модер', 3:'👤 Старший модер', 4:'👑 Создатель'}
    staff.sort(key=lambda x: x[1], reverse=True)
    text = '👥 **СОТРУДНИКИ В ЧАТЕ:**\n\n'
    for uid, rank, name, is_admin in staff:
        status = "✅" if is_admin else "❌"
        text += f"{status} {rank_names.get(rank, 'Неизвестно')}: {name}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== SAY И SAY_ALL ====================
@block_check
async def say_command(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if update.effective_chat.type != 'private':
        return await update.message.reply_text('📝 Только в личке')
    if len(context.args) < 2:
        return await update.message.reply_text('📝 /say <chat_id> <текст>')
    try:
        chat_id = int(context.args[0])
        msg = ' '.join(context.args[1:])
        chat_info = await context.bot.get_chat(chat_id)
        chat_name = chat_info.title or chat_info.first_name or str(chat_id)
        chat_link = f"https://t.me/{chat_info.username}" if chat_info.username else "нет ссылки"
        owner = "Неизвестно"
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            for admin in admins:
                if admin.status == 'creator':
                    owner = f"@{admin.user.username}" if admin.user.username else admin.user.full_name
                    break
            if owner == "Неизвестно" and admins:
                owner = f"@{admins[0].user.username}" if admins[0].user.username else admins[0].user.full_name
        except:
            pass
        await context.bot.send_message(chat_id, msg)
        await update.message.reply_text(
            f'✅ Отправлено в: {chat_name}\n'
            f'🔗 Ссылка: {chat_link}\n'
            f'👑 Владелец/Админ: {owner}'
        )
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

@block_check
async def say_all(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if update.effective_chat.type != 'private':
        return await update.message.reply_text('📝 Только в личке')
    if not context.args:
        return await update.message.reply_text('📝 /say_all <текст>')
    msg = ' '.join(context.args)
    if not bot_chats:
        return await update.message.reply_text('❌ Бот не добавлен ни в один чат')
    sent = 0
    failed = 0
    chat_list = []
    for chat_id in bot_chats:
        try:
            chat = await context.bot.get_chat(int(chat_id))
            chat_name = chat.title or chat.first_name or str(chat_id)
            chat_link = f"https://t.me/{chat.username}" if chat.username else f"ID: {chat_id}"
            await context.bot.send_message(int(chat_id), f"📢 {msg}")
            sent += 1
            chat_list.append(f"✅ {chat_name} - {chat_link}")
        except:
            failed += 1
    result_text = f"✅ Отправлено в {sent} чатов\n❌ Ошибок: {failed}\n\n📋 **Список чатов:**\n" + "\n".join(chat_list[:15])
    if len(chat_list) > 15:
        result_text += f"\n... и ещё {len(chat_list) - 15} чатов"
    await update.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN)

# ==================== CHATS ====================
@block_check
async def chats_command(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if update.effective_chat.type != 'private':
        return await update.message.reply_text('📝 Только в личке')
    if not bot_chats:
        return await update.message.reply_text('❌ Бот не добавлен ни в один чат')
    text = '📋 **ВСЕ ЧАТЫ:**\n\n'
    for chat_id in bot_chats:
        try:
            chat = await context.bot.get_chat(int(chat_id))
            name = chat.title or chat.first_name or str(chat_id)
            chat_link = f"https://t.me/{chat.username}" if chat.username else "Нет ссылки"
            members_count = len(chat_user_stats.get(str(chat_id), {}))
            text += f"• **{name}**\n"
            text += f"  Ссылка: {chat_link}\n"
            text += f"  ID: `{chat_id}`\n"
            text += f"  Участников: {members_count}\n\n"
        except:
            text += f"• Приватный чат (ID: `{chat_id}`)\n\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== CHECK_CHAT ====================
@block_check
async def check_chat(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if update.effective_chat.type != 'private':
        return await update.message.reply_text('📝 Только в личке')
    if not context.args:
        return await update.message.reply_text('📝 /check_chat <ID>')
    try:
        chat_id = int(context.args[0])
        chat_info = await context.bot.get_chat(chat_id)
        chat_id_str = str(chat_id)
        messages = chat_messages.get(chat_id_str, [])
        if not messages:
            return await update.message.reply_text(f'📊 Нет сохранённых сообщений в чате "{chat_info.title or chat_id}"')
        chat_name = chat_info.title or chat_info.first_name or str(chat_id)
        chat_link = f"https://t.me/{chat_info.username}" if chat_info.username else f"ID: {chat_id}"
        text = f"📋 **ПОСЛЕДНИЕ СООБЩЕНИЯ В ЧАТЕ:**\n"
        text += f"📌 {chat_name}\n"
        text += f"🔗 {chat_link}\n\n"
        count = 0
        for msg in reversed(messages[-20:]):
            user = get_user(msg.get('user_id'))
            name = user.get('first_name', 'Неизвестно') if user else 'Неизвестно'
            msg_text = msg.get('text', '[медиа]')
            text += f"👤 {name}: {msg_text}\n"
            count += 1
            if len(text) > 3500:
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
                text = f"📋 **ПРОДОЛЖЕНИЕ:**\n\n"
        if text:
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

# ==================== CHECK_CHAT_ALL ====================
@block_check
async def check_chat_all(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if update.effective_chat.type != 'private':
        return await update.message.reply_text('📝 Только в личке')
    if not context.args:
        return await update.message.reply_text('📝 /check_chat_all <ID>')
    try:
        chat_id = int(context.args[0])
        chat_info = await context.bot.get_chat(chat_id)
        chat_id_str = str(chat_id)
        messages = chat_messages.get(chat_id_str, [])
        if not messages:
            return await update.message.reply_text(f'📊 Нет сохранённых сообщений в чате "{chat_info.title or chat_id}"')
        chat_name = chat_info.title or chat_info.first_name or str(chat_id)
        chat_link = f"https://t.me/{chat_info.username}" if chat_info.username else f"ID: {chat_id}"
        text = f"📋 **ВСЕ СООБЩЕНИЯ В ЧАТЕ:**\n"
        text += f"📌 {chat_name}\n"
        text += f"🔗 {chat_link}\n"
        text += f"📊 Всего: {len(messages)} сообщений\n\n"
        count = 0
        for msg in messages:
            user = get_user(msg.get('user_id'))
            name = user.get('first_name', 'Неизвестно') if user else 'Неизвестно'
            msg_text = msg.get('text', '[медиа]')
            text += f"👤 {name}: {msg_text}\n"
            count += 1
            if len(text) > 3500:
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
                text = f"📋 **ПРОДОЛЖЕНИЕ ({count}/{len(messages)}):**\n\n"
        if text:
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        await update.message.reply_text(f"✅ Показано {len(messages)} сообщений из чата {chat_name}")
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

# ==================== ADD_INTERCEPTOR ====================
@block_check
async def add_interceptor(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if update.effective_chat.type != 'private':
        return await update.message.reply_text('📝 Только в личке')
    if len(context.args) < 3:
        return await update.message.reply_text(
            '📝 /add_interceptor <название> <цена> <выносливость>\n'
            'Пример: /add_interceptor "Супер-машина" 500000 350'
        )
    args = context.args
    if args[0].startswith('"'):
        name_parts = []
        idx = 0
        while idx < len(args):
            if args[idx].startswith('"'):
                name_parts.append(args[idx][1:])
                idx += 1
                while idx < len(args) and not args[idx].endswith('"'):
                    name_parts.append(args[idx])
                    idx += 1
                if idx < len(args):
                    name_parts.append(args[idx][:-1])
                    idx += 1
                break
            else:
                name_parts.append(args[idx])
                idx += 1
        name = ' '.join(name_parts).strip()
        if idx >= len(args):
            return await update.message.reply_text('❌ Не указана цена или выносливость')
        price_str = args[idx]
        speed_str = args[idx + 1] if idx + 1 < len(args) else None
        if speed_str is None:
            return await update.message.reply_text('❌ Не указана выносливость')
    else:
        name = args[0]
        price_str = args[1]
        speed_str = args[2]
    try:
        price = int(price_str)
        max_speed = int(speed_str)
    except ValueError:
        return await update.message.reply_text('❌ Цена и выносливость должны быть числами')
    if price <= 0 or max_speed <= 0:
        return await update.message.reply_text('❌ Цена и выносливость должны быть положительными')
    all_cars = dict(CARS)
    all_cars.update(custom_interceptors)
    if name in all_cars:
        return await update.message.reply_text(f'❌ Перехватчик с именем "{name}" уже существует')
    custom_interceptors[name] = {
        'name': f'🚗 {name}',
        'price': price,
        'max_speed': max_speed,
        'desc': f'Выдерживает до {max_speed} mph (кастомный)'
    }
    await save_data()
    await update.message.reply_text(f'✅ Добавлен перехватчик "{name}"\n💰 Цена: ${price:,}\n💪 Выносливость: {max_speed} mph')

@block_check
async def remove_interceptor(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if update.effective_chat.type != 'private':
        return await update.message.reply_text('📝 Только в личке')
    if not context.args:
        return await update.message.reply_text('📝 /remove_interceptor "Название"')
    name = ' '.join(context.args).strip()
    if name not in custom_interceptors:
        return await update.message.reply_text(f'❌ Перехватчик "{name}" не найден в кастомных')
    del custom_interceptors[name]
    await save_data()
    await update.message.reply_text(f'✅ Перехватчик "{name}" удалён')

# ==================== JOIN ====================
@block_check
async def join_command(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    if update.effective_chat.type != 'private':
        return await update.message.reply_text('📝 Только в личке')
    if not context.args:
        return await update.message.reply_text('📝 /join <ссылка или юзернейм чата>')
    target = context.args[0]
    try:
        chat_info = None
        if 't.me/' in target or 'telegram.me/' in target:
            if 't.me/' in target:
                parts = target.split('t.me/')
            else:
                parts = target.split('telegram.me/')
            if len(parts) > 1:
                username = parts[1].split('/')[0].split('?')[0]
                if username.startswith('@'):
                    username = username[1:]
                try:
                    chat_info = await context.bot.get_chat(f"@{username}")
                except:
                    pass
        elif target.startswith('@'):
            try:
                chat_info = await context.bot.get_chat(target)
            except:
                pass
        else:
            try:
                chat_info = await context.bot.get_chat(int(target))
            except:
                pass
        if chat_info:
            if chat_info.type in ['group', 'supergroup']:
                bot_chats.add(str(chat_info.id))
                await save_data()
                await update.message.reply_text(f'✅ Бот добавлен в чат "{chat_info.title}"\nID: {chat_info.id}')
            else:
                await update.message.reply_text(f'ℹ️ Это не группа: {chat_info.type}')
        else:
            await update.message.reply_text('❌ Не удалось найти чат. Проверьте ссылку или юзернейм.')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

# ==================== CLEAN ====================
@block_check
async def clean(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text('🚫 Только владелец')
    chat_id = str(update.effective_chat.id)
    try:
        bot_member = await update.effective_chat.get_member(context.bot.id)
        if not bot_member.can_delete_messages:
            return await update.message.reply_text('❌ Бот не админ')
    except:
        return await update.message.reply_text('❌ Ошибка прав')
    if context.args:
        try:
            n = int(context.args[0])
            if n <= 0:
                return await update.message.reply_text('❌ Введите положительное число')
        except:
            return await update.message.reply_text('❌ Введите число')
    else:
        n = None
    msg_ids = chat_messages.get(chat_id, [])
    if not msg_ids:
        return await update.message.reply_text('📊 Нет сохранённых сообщений')
    to_delete = msg_ids[-n:] if n is not None else msg_ids
    deleted = 0
    for m in to_delete:
        try:
            await context.bot.delete_message(int(chat_id), m['msg_id'])
            deleted += 1
            await asyncio.sleep(0.1)
        except:
            pass
    if n is not None:
        chat_messages[chat_id] = msg_ids[:-n] if len(msg_ids) > n else []
    else:
        chat_messages[chat_id] = []
    await save_data()
    await update.message.reply_text(f'🗑️ Удалено {deleted} сообщений')

# ==================== RULES ====================
@block_check
async def rules(update, context):
    chat_id = str(update.effective_chat.id)
    await update.message.reply_text(f'📋 **ПРАВИЛА ЧАТА:**\n\n{get_setting(chat_id, "rules")}', parse_mode=ParseMode.MARKDOWN)

@block_check
async def add_greetings(update, context):
    if not is_owner_or_creator(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    text = ' '.join(context.args)
    if not text:
        return await update.message.reply_text('📝 Напишите текст приветствия')
    update_setting(update.effective_chat.id, 'greetings', text)
    await update.message.reply_text(f'✅ Приветствие установлено:\n{text}')

# ==================== OFF/ON CHAT ====================
@block_check
async def off_chat(update, context):
    if not is_owner_or_creator(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    try:
        await update.effective_chat.set_permissions(ChatPermissions(can_send_messages=False))
        await update.message.reply_text('🔒 Чат ЗАКРЫТ')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

@block_check
async def on_chat(update, context):
    if not is_owner_or_creator(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    try:
        await update.effective_chat.set_permissions(ChatPermissions(can_send_messages=True))
        await update.message.reply_text('🔓 Чат ОТКРЫТ')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка: {e}')

# ==================== REPORTS ====================
@block_check
async def report_start(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text('📝 Ответь на сообщение')
    context.user_data['reported_id'] = str(update.message.reply_to_message.from_user.id)
    await update.message.reply_text('📝 Напиши причину жалобы')
    return REPORT_REASON

@block_check
async def report_reason(update, context):
    reason = update.message.text
    reported_id = context.user_data.get('reported_id')
    if not reported_id:
        await update.message.reply_text('❌ Ошибка, начни заново')
        return ConversationHandler.END
    reports.append({
        'chat_id': str(update.effective_chat.id),
        'reporter_id': str(update.effective_user.id),
        'reported_id': reported_id,
        'reason': reason,
        'date': str(datetime.datetime.now()),
        'status': 'pending'
    })
    await save_data()
    await update.message.reply_text('✅ Репорт отправлен')
    return ConversationHandler.END

@block_check
async def reports_list(update, context):
    if not is_owner_or_creator(update.effective_user.id):
        return await update.message.reply_text('🚫 Нет прав')
    pending = [r for r in reports if r.get('status') == 'pending']
    if not pending:
        return await update.message.reply_text('📊 Нет новых репортов')
    text = '📋 **НОВЫЕ РЕПОРТЫ:**\n\n'
    for r in pending:
        text += f"ID {id(r)}: от [user](tg://user?id={r['reporter_id']}) на [user](tg://user?id={r['reported_id']})\nПричина: {r['reason']}\nВремя: {r['date']}\n\n"
        if len(text) > 4000:
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            text = ''
    if text:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== INTERCEPT ====================
@block_check
async def intercept(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text('💰 Сначала /start')
    
    cooldown_key = f'{user_id}_intercept'
    now = time.time()
    if cooldown_key in cooldowns and now - cooldowns[cooldown_key] < 30:
        remaining = int(30 - (now - cooldowns[cooldown_key]))
        return await update.message.reply_text(f'⏰ Подождите {remaining} секунд')
    
    cooldowns[cooldown_key] = now
    await save_data()
    
    current_car_key = user.get('current_car', 'SCOUT')
    car_data = CARS.get(current_car_key, CARS['SCOUT'])
    has_radar = user.get('current_radar') is not None
    radar_name = RADARS[user['current_radar']]['name'] if has_radar else None
    
    session_id = f"{user_id}_{int(time.time())}_{random.randint(1000, 9999)}"
    
    if 'active_intercepts' not in context.bot_data:
        context.bot_data['active_intercepts'] = {}
    
    context.bot_data['active_intercepts'][session_id] = {
        'user_id': user_id,
        'chat_id': str(update.effective_chat.id),
        'car_key': current_car_key,
        'has_radar': has_radar,
        'radar_name': radar_name,
        'radar_type': user.get('current_radar') if has_radar else None,
        'use_probes': False,
        'mode': None,
        'start_time': time.time(),
        'ef_level': None,
        'wind_speed': None,
        'final_speed': None,
        'last_action': time.time(),
        'scan_reward_given': False
    }
    
    keyboard = [
        [InlineKeyboardButton("📡 Сканировать", callback_data=f"intercept_mode_scan||{session_id}")],
        [InlineKeyboardButton("🌪️ Перехватывать", callback_data=f"intercept_mode_intercept||{session_id}")]
    ]
    
    await update.message.reply_text(
        f"🌪️ **ТОРНАДО ОБНАРУЖЕНО!** 🌪️\n\n"
        f"🚗 Машина: {car_data['name']}\n"
        f"{'🛰️ Радар: ' + radar_name if has_radar else '❌ Радар не установлен'}\n\n"
        f"⏰ У вас 40 секунд.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

@block_check
async def intercept_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    if '||' not in callback_data:
        return await query.edit_message_text('❌ Ошибка данных')
    
    parts = callback_data.split('||')
    if len(parts) != 2:
        return await query.edit_message_text('❌ Ошибка данных')
    
    session_id = parts[1].strip()
    if not session_id:
        return await query.edit_message_text('❌ Ошибка данных')
    
    if 'active_intercepts' not in context.bot_data:
        context.bot_data['active_intercepts'] = {}
    
    session = context.bot_data['active_intercepts'].get(session_id)
    if not session:
        return await query.edit_message_text('⏰ Сессия не найдена. Начните заново /intercept')
    
    if session.get('user_id') != str(update.effective_user.id):
        return await query.edit_message_text('⏰ Сессия не принадлежит вам')
    
    now = time.time()
    if now - session.get('last_action', 0) > 40:
        await query.edit_message_text('⏰ Сессия истекла (40 сек). Начните заново /intercept')
        if session_id in context.bot_data['active_intercepts']:
            del context.bot_data['active_intercepts'][session_id]
        return
    
    session['last_action'] = now
    context.bot_data['active_intercepts'][session_id] = session
    
    action_data = parts[0]
    action_parts = action_data.split('_')
    action = action_parts[1]
    
    user_id = session['user_id']
    user = get_user(user_id)
    
    if action == 'leave':
        await intercept_leave(update, context, session, session_id)
        return
    elif action == 'stay':
        await intercept_stay(update, context, session, session_id)
        return
    elif action == 'mode':
        mode = action_parts[2]
        session['mode'] = mode
        session['last_action'] = time.time()
        context.bot_data['active_intercepts'][session_id] = session
        
        has_probes = len(user.get('probes', {})) > 0
        keyboard = []
        if has_probes:
            keyboard.append([InlineKeyboardButton("☂️ Поставить зонты", callback_data=f"intercept_probes_on||{session_id}")])
        keyboard.append([InlineKeyboardButton("❌ Без зонтов", callback_data=f"intercept_probes_off||{session_id}")])
        
        mode_text = "📡 СКАНИРОВАНИЕ" if mode == 'scan' else "🌪️ ПЕРЕХВАТ"
        car_name = CARS.get(session['car_key'], {}).get('name', 'Неизвестно')
        
        await query.edit_message_text(
            f"{mode_text}\n\n🚗 Машина: {car_name}\n"
            f"{'🛰️ Радар: ' + session['radar_name'] if session['has_radar'] else '❌ Без радара'}\n"
            f"Выберите опции:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif action == 'probes':
        use_probes = action_parts[2] == 'on'
        session['use_probes'] = use_probes
        session['last_action'] = time.time()
        context.bot_data['active_intercepts'][session_id] = session
        
        if session['mode'] == 'scan':
            await start_scanning(update, context, session, session_id)
        else:
            await start_intercept(update, context, session, session_id)

async def start_scanning(update: Update, context: ContextTypes.DEFAULT_TYPE, session, session_id):
    chat_id = session['chat_id']
    user_id = session['user_id']
    user = get_user(user_id)
    
    if not session['has_radar']:
        await context.bot.send_message(chat_id, '❌ Нет радара для сканирования')
        if session_id in context.bot_data.get('active_intercepts', {}):
            del context.bot_data['active_intercepts'][session_id]
        return
    
    await context.bot.send_message(chat_id, "🔄 Начинаю сканирование торнадо...")
    
    ef_levels = list(EF_SCALE.keys())
    weights = [EF_SCALE[l]['weight'] for l in ef_levels]
    ef_choice = random.choices(ef_levels, weights=weights, k=1)[0]
    ef_info = EF_SCALE[ef_choice]
    real_speed = random.randint(ef_info['min'], ef_info['max'])
    
    session['ef_level'] = ef_choice
    session['final_speed'] = real_speed
    session['last_action'] = time.time()
    context.bot_data['active_intercepts'][session_id] = session
    
    for i in range(3):
        approx_speed = real_speed + random.randint(-30, 30)
        if approx_speed < 0:
            approx_speed = 0
        await context.bot.send_message(chat_id, f"🔄 Радар крутится... {i+1}/3\n💨 ~{approx_speed} mph")
        await asyncio.sleep(1)
        session['last_action'] = time.time()
        context.bot_data['active_intercepts'][session_id] = session
    
    for i in range(2):
        growth = real_speed + random.randint(10, 50)
        await context.bot.send_message(chat_id, f"🌪️ Торнадо растет! {i+1}/2\n💨 {growth} mph")
        await asyncio.sleep(1)
        session['last_action'] = time.time()
        context.bot_data['active_intercepts'][session_id] = session
    
    await context.bot.send_message(
        chat_id,
        f"🎯 **СКАНИРОВАНИЕ ЗАВЕРШЕНО:**\n"
        f"💨 Скорость: {real_speed} mph\n"
        f"📊 Категория: {EF_SCALE[ef_choice]['name']}",
        parse_mode=ParseMode.MARKDOWN
    )
    
    if user and not session.get('scan_reward_given', False):
        scan_reward = random.randint(5000, 10000)
        user['balance'] = user.get('balance', 0) + scan_reward
        session['scan_reward_given'] = True
        await save_data()
        await context.bot.send_message(chat_id, f"💰 +${scan_reward:,}. Баланс: ${user['balance']:,}")
    
    if session.get('use_probes') and user.get('probes'):
        probes = user.get('probes', {})
        new_probes = {}
        broken = []
        for pkey, hp in probes.items():
            new_hp = hp - 1
            if new_hp <= 0:
                broken.append(PROBES[pkey]['name'])
            else:
                new_probes[pkey] = new_hp
        user['probes'] = new_probes
        if broken:
            await context.bot.send_message(chat_id, f"☂️ Зонты сломаны: {', '.join(broken)}")
        await save_data()
    
    if ef_choice >= 2 and random.random() < 0.4:
        keyboard = [
            [InlineKeyboardButton("🏃 Уехать", callback_data=f"intercept_leave||{session_id}")],
            [InlineKeyboardButton("🔄 Остаться", callback_data=f"intercept_stay||{session_id}")]
        ]
        await context.bot.send_message(chat_id, "⚠️ Торнадо меняет траекторию!", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    await finish_scan(update, context, session, session_id)

async def finish_scan(update: Update, context: ContextTypes.DEFAULT_TYPE, session, session_id):
    chat_id = session['chat_id']
    ef_choice = session['ef_level']
    real_speed = session['final_speed']
    
    await context.bot.send_message(chat_id, f"✅ Сканирование завершено!\n📊 {EF_SCALE[ef_choice]['name']}\n💨 {real_speed} mph")
    
    await asyncio.sleep(30)
    await context.bot.send_message(chat_id, "🌪️ Торнадо ушло. /intercept для нового")
    
    if session_id in context.bot_data.get('active_intercepts', {}):
        del context.bot_data['active_intercepts'][session_id]

async def start_intercept(update: Update, context: ContextTypes.DEFAULT_TYPE, session, session_id):
    chat_id = session['chat_id']
    user_id = session['user_id']
    user = get_user(user_id)
    car_key = session['car_key']
    car_data = CARS.get(car_key, CARS['SCOUT'])
    
    await context.bot.send_message(chat_id, f"🌪️ **ПЕРЕХВАТ НАЧАЛСЯ!**\n🚗 Машина: {car_data['name']}", parse_mode=ParseMode.MARKDOWN)
    
    ef_levels = list(EF_SCALE.keys())
    weights = [EF_SCALE[l]['weight'] for l in ef_levels]
    ef_choice = random.choices(ef_levels, weights=weights, k=1)[0]
    ef_info = EF_SCALE[ef_choice]
    wind_speed = random.randint(ef_info['min'], ef_info['max'])
    
    session['ef_level'] = ef_choice
    session['wind_speed'] = wind_speed
    session['last_action'] = time.time()
    context.bot_data['active_intercepts'][session_id] = session
    
    for i in range(3):
        await asyncio.sleep(1)
        current_speed = wind_speed + random.randint(-20, 20)
        if current_speed < 0:
            current_speed = 0
        await context.bot.send_message(chat_id, f"🌪️ Тряска... {i+1}/3\n💨 ~{current_speed} mph")
        session['last_action'] = time.time()
        context.bot_data['active_intercepts'][session_id] = session
    
    if car_key == 'civil':
        car_endurance = random.randint(0, 300)
    else:
        car_endurance = car_data.get('max_speed', 0)
    
    success = wind_speed <= car_endurance
    
    probe_bonus = 1.0
    if session.get('use_probes') and user.get('probes'):
        for pkey in user.get('probes', {}):
            if pkey in PROBES:
                probe_bonus = max(probe_bonus, PROBES[pkey]['bonus'])
    
    if success:
        reward = random.randint(ef_info['reward_min'], ef_info['reward_max'])
        bonus = int(reward * (probe_bonus - 1))
        total = reward + bonus
        user['balance'] = user.get('balance', 0) + total
        
        if session.get('use_probes') and user.get('probes'):
            probes = user.get('probes', {})
            new_probes = {}
            for pkey, hp in probes.items():
                new_hp = hp - 1
                if new_hp > 0:
                    new_probes[pkey] = new_hp
            user['probes'] = new_probes
        
        await context.bot.send_message(
            chat_id,
            f"🎉 **ПЕРЕХВАТ УСПЕШЕН!**\n"
            f"📊 {EF_SCALE[ef_choice]['name']}\n"
            f"💨 {wind_speed} mph\n"
            f"💰 +${total:,}. Баланс: ${user['balance']:,}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        reward = random.randint(ef_info['reward_min'] // 2, ef_info['reward_max'] // 2)
        bonus = int(reward * (probe_bonus - 1))
        total = reward + bonus
        user['balance'] = user.get('balance', 0) + total
        
        if session.get('use_probes') and user.get('probes'):
            probes = user.get('probes', {})
            new_probes = {}
            for pkey, hp in probes.items():
                new_hp = hp - 1
                if new_hp > 0:
                    new_probes[pkey] = new_hp
            user['probes'] = new_probes
        
        await context.bot.send_message(
            chat_id,
            f"💥 **ПЕРЕХВАТ ПРОВАЛЕН!**\n"
            f"📊 {EF_SCALE[ef_choice]['name']}\n"
            f"💨 {wind_speed} mph\n"
            f"⚠️ Машина НЕ уничтожена!\n"
            f"💰 +${total:,}. Баланс: ${user['balance']:,}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    await save_data()
    if session_id in context.bot_data.get('active_intercepts', {}):
        del context.bot_data['active_intercepts'][session_id]

async def intercept_leave(update: Update, context: ContextTypes.DEFAULT_TYPE, session, session_id):
    query = update.callback_query
    await query.answer()
    chat_id = session['chat_id']
    user_id = session['user_id']
    user = get_user(user_id)
    
    if user and not session.get('scan_reward_given', False):
        scan_reward = random.randint(5000, 10000)
        user['balance'] = user.get('balance', 0) + scan_reward
        session['scan_reward_given'] = True
        await save_data()
        await context.bot.send_message(chat_id, f"💰 +${scan_reward:,}")
    
    if random.random() < 0.5:
        await query.edit_message_text("🏃 Вы успели уехать! Радар сохранен")
    else:
        await query.edit_message_text(f"💨 Радар {session['radar_name']} унесло!")
        if user and user.get('current_radar'):
            radars = user.get('radars', [])
            radar = user['current_radar']
            if radar in radars:
                radars.remove(radar)
                user['radars'] = radars
                user['current_radar'] = radars[0] if radars else None
            await save_data()
    
    await asyncio.sleep(10)
    await context.bot.send_message(chat_id, "🌪️ Торнадо ушло")
    
    if session_id in context.bot_data.get('active_intercepts', {}):
        del context.bot_data['active_intercepts'][session_id]

async def intercept_stay(update: Update, context: ContextTypes.DEFAULT_TYPE, session, session_id):
    query = update.callback_query
    await query.answer()
    chat_id = session['chat_id']
    user_id = session['user_id']
    user = get_user(user_id)
    
    if user and not session.get('scan_reward_given', False):
        scan_reward = random.randint(5000, 10000)
        user['balance'] = user.get('balance', 0) + scan_reward
        session['scan_reward_given'] = True
        await save_data()
        await context.bot.send_message(chat_id, f"💰 +${scan_reward:,}")
    
    await query.edit_message_text("🔄 Вы остались сканировать")
    
    if random.random() < 0.5:
        await context.bot.send_message(chat_id, f"💨 Радар {session['radar_name']} унесло!")
        if user and user.get('current_radar'):
            radars = user.get('radars', [])
            radar = user['current_radar']
            if radar in radars:
                radars.remove(radar)
                user['radars'] = radars
                user['current_radar'] = radars[0] if radars else None
            await save_data()
    else:
        await context.bot.send_message(chat_id, "✅ Радар уцелел!")
    
    await finish_scan(update, context, session, session_id)

# ==================== КАРТА KEYSOTA ====================
@block_check
async def map_command(update, context):
    storm_status = "🌪️ Торнадо: Активно!" if 'active_storm' in context.bot_data else "🌤️ Торнадо: Не обнаружено"
    text = f"""
🌪️ **КАРТА KEYSOTA** 🌪️
━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    🌲🌲
         🏙️ CITY   🌲🌲
         📍📍📍    🌲🌲
    🌾🌾       🌾🌾   🌲
    🌾🌾  📍   🌾🌾   🌲
         🌾🌾🌾🌾🌾   🌲
              🌊🌊🌊🌊🌊
              🌊🌊🌊🌊🌊
    🏜️🏜️🏜️     🌊🌊🌊
    🏜️🏜️🏜️     ⛰️⛰️
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Твоя позиция: Forest Hills
{storm_status}

📡 Выбери радар:
    """
    keyboard = [
        [InlineKeyboardButton("📡 KHZL (дальний)", callback_data="radar_khzl")],
        [InlineKeyboardButton("📡 THIB (точный)", callback_data="radar_thib")],
        [InlineKeyboardButton("🚗 DOW (мобильный)", callback_data="radar_dow")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

async def radar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    radar_type = query.data.split('_')[1]
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await query.edit_message_text("💰 Сначала /start")
    radar_data = RADARS.get(radar_type.upper())
    if not radar_data:
        return await query.edit_message_text("❌ Радар не найден")
    if radar_type.upper() not in user.get('radars', []):
        return await query.edit_message_text(f"❌ У тебя нет радара {radar_data['name']}! Купи в /shop_radars")
    
    if 'active_storm' in context.bot_data:
        ef = context.bot_data['active_storm']
        ef_info = EF_SCALE[ef]
        colors = ['🟢', '🟡', '🟠', '🔴', '⚫']
        color = colors[ef - 1] if ef <= 5 else '⚫'
        tvs_color = ['🟢', '🟡', '🟠', '🔴', '🟣'][ef - 1] if ef <= 5 else '🟣'
        text = f"""
📡 **{radar_data['name']}** ({int(radar_data['accuracy']*100)}%)

🔍 **Обнаружено:**
📍 {context.bot_data.get('storm_location', 'Неизвестно')}
{color} Пиксели: {random.randint(3, 8)} шт.
🔽 TVS: {tvs_color} (сила: {ef_info['name']})

📊 **Данные:**
💨 Скорость: {random.randint(ef_info['min'], ef_info['max'])} mph
🌡️ Температура: {random.randint(20, 35)}°C
💧 Влажность: {random.randint(60, 95)}%

🎯 Точность: {int(radar_data['accuracy']*100)}%
        """
    else:
        text = f"""
📡 **{radar_data['name']}** ({int(radar_data['accuracy']*100)}%)

🔍 **Ничего не обнаружено**

🌤️ Погода ясная, торнадо нет.
        """
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== КЛАНЫ ====================
@block_check
async def clan_create(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text("💰 Сначала /start")
    if user.get('clan'):
        return await update.message.reply_text(f"🏛️ Ты уже в клане {user['clan']}!")
    if not context.args:
        return await update.message.reply_text("📝 **/clan_create <название>**")
    clan_name = ' '.join(context.args).strip()
    if clan_name in clans:
        return await update.message.reply_text("❌ Клан с таким названием уже существует!")
    clans[clan_name] = {
        'owner': user_id,
        'members': [user_id],
        'balance': 0,
        'created': str(datetime.datetime.now())
    }
    user['clan'] = clan_name
    await save_data()
    await update.message.reply_text(f"🏛️ **Клан {clan_name} создан!**\nТы — лидер клана!")

@block_check
async def clan_invite(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text("💰 Сначала /start")
    clan_name = user.get('clan')
    if not clan_name:
        return await update.message.reply_text("🏛️ Ты не в клане!")
    if clans.get(clan_name, {}).get('owner') != user_id:
        return await update.message.reply_text("🚫 Только лидер клана может приглашать!")
    if not context.args:
        return await update.message.reply_text("📝 **/clan_invite <ID>**")
    try:
        target_id = str(int(context.args[0]))
    except:
        return await update.message.reply_text("❌ Введите корректный ID")
    target = get_user(target_id)
    if not target:
        return await update.message.reply_text("❌ Пользователь не найден")
    if target.get('clan'):
        return await update.message.reply_text("❌ Пользователь уже в клане")
    clans[clan_name]['members'].append(target_id)
    target['clan'] = clan_name
    await save_data()
    await update.message.reply_text(f"✅ {target.get('first_name', 'Пользователь')} добавлен в клан {clan_name}!")

@block_check
async def clan_info(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text("💰 Сначала /start")
    clan_name = user.get('clan')
    if not clan_name:
        return await update.message.reply_text("🏛️ Ты не в клане!")
    clan = clans.get(clan_name)
    if not clan:
        return await update.message.reply_text("❌ Клан не найден")
    text = f"""
🏛️ **КЛАН {clan_name}** 🏛️

👑 Лидер: {get_user(clan['owner']).get('first_name', 'Неизвестно') if get_user(clan['owner']) else 'Неизвестно'}
👥 Участников: {len(clan['members'])}
💰 Банк: ${clan.get('balance', 0):,}
📅 Создан: {clan.get('created', 'Неизвестно')}

👤 **Участники:**
"""
    for mid in clan['members']:
        m = get_user(mid)
        if m:
            text += f"• {m.get('first_name', 'Неизвестно')}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== ДОСТИЖЕНИЯ ====================
ACHIEVEMENTS = {
    'first_hunt': {'name': '🏆 Первая охота', 'desc': 'Поймать первое торнадо', 'icon': '🏆'},
    'hunter_10': {'name': '🏆 Охотник', 'desc': 'Поймать 10 торнадо', 'icon': '🏆'},
    'hunter_50': {'name': '🏆 Мастер-охотник', 'desc': 'Поймать 50 торнадо', 'icon': '🏆'},
    'hunter_100': {'name': '🏆 Легендарный охотник', 'desc': 'Поймать 100 торнадо', 'icon': '🏆'},
    'millionaire': {'name': '💰 Миллионер', 'desc': 'Заработать $1,000,000', 'icon': '💰'},
    'streak_10': {'name': '🔥 Серия 10', 'desc': 'Собрать серию 10', 'icon': '🔥'},
    'streak_25': {'name': '🔥 Серия 25', 'desc': 'Собрать серию 25', 'icon': '🔥'},
    'streak_50': {'name': '🔥 Серия 50', 'desc': 'Собрать серию 50', 'icon': '🔥'},
    'vip_owner': {'name': '⭐ VIP', 'desc': 'Купить VIP', 'icon': '⭐'},
    'clan_leader': {'name': '🏛️ Лидер клана', 'desc': 'Создать клан', 'icon': '🏛️'}
}

@block_check
async def achievements(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text("💰 Сначала /start")
    user_achievements = user.get('achievements', [])
    text = "🏆 **ТВОИ ДОСТИЖЕНИЯ** 🏆\n\n"
    for key, ach in ACHIEVEMENTS.items():
        if key in user_achievements:
            text += f"{ach['icon']} **{ach['name']}** — ✅ {ach['desc']}\n"
        else:
            text += f"{ach['icon']} {ach['name']} — ❌ {ach['desc']}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== МИНИ-ИГРЫ ====================
@block_check
async def casino(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text("💰 Сначала /start")
    text = """
🎰 **КАЗИНО** 🎰

Выбери игру:
• /slot — слоты ($1,000)
• /guess — угадай число ($500)
• /roulette — русская рулетка ($5,000)
    """
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def slot(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text("💰 Сначала /start")
    if user.get('balance', 0) < 1000:
        return await update.message.reply_text("❌ Недостаточно денег! Нужно $1,000")
    user['balance'] -= 1000
    emojis = ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '💎', '7️⃣']
    result = [random.choice(emojis) for _ in range(3)]
    if result[0] == result[1] == result[2]:
        if result[0] == '7️⃣':
            win = 10000
        elif result[0] == '💎':
            win = 5000
        elif result[0] == '⭐':
            win = 3000
        else:
            win = 2000
        user['balance'] += win
        text = f"🎰 **ДЖЕКПОТ!**\n{result[0]} {result[1]} {result[2]}\n💰 +${win:,}"
    elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
        win = 500
        user['balance'] += win
        text = f"🎰 **ПОБЕДА!**\n{result[0]} {result[1]} {result[2]}\n💰 +${win}"
    else:
        text = f"🎰 **ПРОИГРЫШ**\n{result[0]} {result[1]} {result[2]}\n💸 -$1,000"
    await save_data()
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@block_check
async def guess(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text("💰 Сначала /start")
    if user.get('balance', 0) < 500:
        return await update.message.reply_text("❌ Недостаточно денег! Нужно $500")
    if 'guess_number' not in context.user_data:
        context.user_data['guess_number'] = random.randint(1, 100)
        context.user_data['guess_attempts'] = 0
    if not context.args:
        return await update.message.reply_text("📝 **/guess <число (1-100)>**")
    try:
        guess_num = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Введите число!")
    target = context.user_data['guess_number']
    context.user_data['guess_attempts'] += 1
    if guess_num == target:
        win = 500 * (10 - context.user_data['guess_attempts'])
        if win < 100:
            win = 100
        user['balance'] += win
        await save_data()
        await update.message.reply_text(f"🎯 **ПОБЕДА!**\nЧисло было {target}\n💰 +${win:,}\nПопыток: {context.user_data['guess_attempts']}")
        del context.user_data['guess_number']
        del context.user_data['guess_attempts']
    elif guess_num < target:
        await update.message.reply_text(f"📈 Больше! (попытка {context.user_data['guess_attempts']})")
    else:
        await update.message.reply_text(f"📉 Меньше! (попытка {context.user_data['guess_attempts']})")
    if context.user_data['guess_attempts'] >= 10:
        user['balance'] -= 500
        await save_data()
        await update.message.reply_text(f"💀 Ты проиграл! Число было {target}\n💸 -$500")
        del context.user_data['guess_number']
        del context.user_data['guess_attempts']

@block_check
async def roulette(update, context):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    if not user:
        return await update.message.reply_text("💰 Сначала /start")
    if user.get('balance', 0) < 5000:
        return await update.message.reply_text("❌ Недостаточно денег! Нужно $5,000")
    user['balance'] -= 5000
    chambers = [1, 2, 3, 4, 5, 6]
    bullet = random.choice(chambers)
    shot = random.choice(chambers)
    if shot == bullet:
        user['balance'] = max(0, user.get('balance', 0) - 10000)
        text = f"💀 **ВЫ УМЕРЛИ!**\nВыстрел попал в вас!\n💸 -$10,000"
    else:
        win = 10000
        user['balance'] += win
        text = f"🎉 **ВЫ ВЫЖИЛИ!**\nВыстрел мимо!\n💰 +${win:,}"
    await save_data()
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== ЗАПУСК ====================
async def run():
    global bot_instance
    load_data()
    logger.info(f'Загружено {len(user_data)} пользователей')
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0, pool_timeout=30.0)
    app = ApplicationBuilder().token(TOKEN).request(request).build()
    bot_instance = app

    asyncio.create_task(auto_save())
    asyncio.create_task(breakdown_loop())

    # Основные команды
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('profile', profile))
    app.add_handler(CommandHandler('balance', balance))
    app.add_handler(CommandHandler('level', level_command))
    app.add_handler(CommandHandler('stats', stats_command))
    app.add_handler(CommandHandler('top', top_command))
    app.add_handler(CommandHandler('daily', daily))
    app.add_handler(CommandHandler('rules', rules))
    app.add_handler(CommandHandler('staff', staff_command))

    # Магазины
    app.add_handler(CommandHandler('shop_cars', shop_cars))
    app.add_handler(CommandHandler('buy_car', buy_car))
    app.add_handler(CommandHandler('sell_car', sell_car))
    app.add_handler(CommandHandler('my_cars', my_cars))
    app.add_handler(CommandHandler('wear', wear_car))

    app.add_handler(CommandHandler('shop_radars', shop_radars))
    app.add_handler(CommandHandler('buy_radar', buy_radar))
    app.add_handler(CommandHandler('my_radars', my_radars))
    app.add_handler(CommandHandler('wear_radar', wear_radar))

    app.add_handler(CommandHandler('shop_probes', shop_probes))
    app.add_handler(CommandHandler('buy_probe', buy_probe))
    app.add_handler(CommandHandler('my_probes', my_probes))

    app.add_handler(CommandHandler('buy_vip', buy_vip))
    app.add_handler(CommandHandler('vip', vip_status))
    app.add_handler(CommandHandler('buy_money', buy_money_cmd))

    # Модерация
    app.add_handler(CommandHandler('mute', mute))
    app.add_handler(CommandHandler('unmute', unmute))
    app.add_handler(CommandHandler('ban', ban))
    app.add_handler(CommandHandler('banofdeath', banofdeath))
    app.add_handler(CommandHandler('unban', unban))
    app.add_handler(CommandHandler('warn', warn))
    app.add_handler(CommandHandler('unwarn', unwarn))
    app.add_handler(CommandHandler('resetwarns', resetwarns))
    app.add_handler(CommandHandler('warn_list', warn_list))
    app.add_handler(CommandHandler('ban_list', ban_list))
    app.add_handler(CommandHandler('mute_list', mute_list))
    app.add_handler(CommandHandler('kick', kick))
    app.add_handler(CommandHandler('mute_admin', mute_admin))
    app.add_handler(CommandHandler('unmute_admin', unmute_admin))

    # Админские
    app.add_handler(CommandHandler('approve_admin', approve_admin))
    app.add_handler(CommandHandler('unapprove_admin', unapprove_admin))
    app.add_handler(CommandHandler('promote', promote))
    app.add_handler(CommandHandler('demote', demote))
    app.add_handler(CommandHandler('block', block_user_cmd))
    app.add_handler(CommandHandler('unblock', unblock_user_cmd))
    app.add_handler(CommandHandler('block_list', block_list))
    app.add_handler(CommandHandler('add_greetings', add_greetings))
    app.add_handler(CommandHandler('off_chat', off_chat))
    app.add_handler(CommandHandler('on_chat', on_chat))
    app.add_handler(CommandHandler('say', say_command))
    app.add_handler(CommandHandler('say_all', say_all))
    app.add_handler(CommandHandler('chats', chats_command))
    app.add_handler(CommandHandler('check_chat', check_chat))
    app.add_handler(CommandHandler('check_chat_all', check_chat_all))
    app.add_handler(CommandHandler('add_interceptor', add_interceptor))
    app.add_handler(CommandHandler('remove_interceptor', remove_interceptor))
    app.add_handler(CommandHandler('join', join_command))
    app.add_handler(CommandHandler('clean', clean))

    # Перехват
    app.add_handler(CommandHandler('intercept', intercept))
    app.add_handler(CommandHandler('map', map_command))
    app.add_handler(CallbackQueryHandler(intercept_callback, pattern='^intercept_'))
    app.add_handler(CallbackQueryHandler(radar_callback, pattern='^radar_'))

    # Кланы
    app.add_handler(CommandHandler('clan_create', clan_create))
    app.add_handler(CommandHandler('clan_invite', clan_invite))
    app.add_handler(CommandHandler('clan', clan_info))

    # Достижения и игры
    app.add_handler(CommandHandler('achievements', achievements))
    app.add_handler(CommandHandler('casino', casino))
    app.add_handler(CommandHandler('slot', slot))
    app.add_handler(CommandHandler('guess', guess))
    app.add_handler(CommandHandler('roulette', roulette))

    # Репорты
    report_conv = ConversationHandler(
        entry_points=[CommandHandler('report', report_start)],
        states={REPORT_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_reason)]},
        fallbacks=[CommandHandler('cancel', lambda u, c: u.message.reply_text('❌ Отменено'))]
    )
    app.add_handler(report_conv)
    app.add_handler(CommandHandler('reports', reports_list))

    # Кнопки
    app.add_handler(CallbackQueryHandler(support_callback, pattern='^(support|confirm|deny|unmute|keep)'))

    # Обработчики
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))

    print("🌪️ ЗАПУСК STORM CHASER — MEGA EDITION...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print(f"✅ БОТ ЗАПУЩЕН!")
    print(f"👥 Пользователей: {len(user_data)}")
    print(f"🚫 Заблокировано: {len(blocked_users)}")
    print(f"💬 Чатов: {len(bot_chats)}")
    print(f"👑 Владелец: {OWNER_ID} | {OWNER_USERNAME}")
    print("🔄 Разрушение предметов КАЖДЫЕ 4 ДНЯ")
    print("⭐ VIP система активна")
    print("🚫 Автоматический мут для чатов-нарушителей")
    print("🗺️ Карта Keysota доступна (/map)")
    print("🏛️ Кланы активны (/clan_create)")
    print("🏆 Достижения активны (/achievements)")
    print("🎰 Казино активно (/casino)")

    stop = asyncio.Future()
    def handler():
        if not stop.done():
            stop.set_result(True)
    try:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, handler)
        loop.add_signal_handler(signal.SIGTERM, handler)
    except:
        pass

    try:
        await stop
    except:
        pass
    finally:
        await save_data()
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        print("👋 Бот остановлен")

if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"Ошибка: {e}")
