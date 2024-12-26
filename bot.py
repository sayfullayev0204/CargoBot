import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton,WebAppInfo
import requests
import urllib

API_BASE_URL = "https://cargobot-production.up.railway.app/api/"  # Django API URL
TOKEN = "6804578580:AAHJhUTXbOaajQjzURNnT_xXuQQV3smwKC8"
web_url = "https://34c4-37-110-210-71.ngrok-free.app"

TELEGRAM_CHAT_ID_UK = -1002231892574  
TELEGRAM_CHAT_ID_US = -1002440391832
TELEGRAM_CHAT_ID_KSA = -1002316531885
TELEGRAM_CHAT_ID_ITA = -1002340445857
TELEGRAM_CHAT_ID_TK = -1002463421519

country_chat_ids = {
        "UK 🇬🇧 UNITED KINGDUM": TELEGRAM_CHAT_ID_UK,
        "ITA 🇮🇹 ITALY": TELEGRAM_CHAT_ID_ITA,
        "KSA 🇸🇦 SAUDI": TELEGRAM_CHAT_ID_KSA,
        "TK 🇹🇷 TURKEY": TELEGRAM_CHAT_ID_TK,
        "US 🇺🇸 AMERICA": TELEGRAM_CHAT_ID_US,
}
country_chat_link = {
                "UK 🇬🇧 UNITED KINGDUM": "https://t.me/ukuzbpochta/1",
                "ITA 🇮🇹 ITALY": "https://t.me/itauzbpochta/1",
                "KSA 🇸🇦 SAUDI": "https://t.me/ksauzbpochta/1",
                "TK 🇹🇷 TURKEY": "https://t.me/tkuzbpochta/1",
                "US 🇺🇸 AMERICA": "https://t.me/usuzbpochta/1",
            }

bot = telebot.TeleBot(TOKEN)

# Global dictionary to track orders
current_order = {}

def get_user_profile_photo_url(user_id):
    try:
        photos = bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id
            file = bot.get_file(file_id)
            photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
            return photo_url
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    tg_id = message.from_user.id
    username = message.from_user.username or ''
    first_name = message.from_user.first_name or ''
    last_name = message.from_user.last_name or ''

    profile_photo = get_user_profile_photo_url(tg_id)
    profile_photo_encoded = urllib.parse.quote(profile_photo or '')

    web_app_url = f"{web_url}/?tg_id={tg_id}&username={username}&first_name={first_name}&last_name={last_name}&profile_photo={profile_photo_encoded}"

    web_app_button = InlineKeyboardButton(
        text="Web App ni ochish",
        web_app=WebAppInfo(url=web_app_url)  # Web App URL
    )
    bot_button = InlineKeyboardButton(
        text="Botda davom etish",
        callback_data="create_order"  
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(web_app_button)
    keyboard.add(bot_button)

    bot.send_message(
        message.chat.id,
        f"Assalomu alaykum, {first_name}! Botga xush kelibsiz.\n"
        f"Web App yoki bot orqali e'lon berish uchun tugmalardan birini tanlang:",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("create_order"))
def create_order(call):
    current_order[call.message.chat.id] = {}  # Ensure the order dictionary is initialized
    try:
        response = requests.get(f"{API_BASE_URL}roles/")
        response.raise_for_status()
        roles = response.json()
    except requests.RequestException:
        bot.send_message(call.message.chat.id, "Rol ma'lumotlarini olishda xatolik yuz berdi.")
        return

    markup = InlineKeyboardMarkup()
    for role in roles:
        markup.add(InlineKeyboardButton(role['name'], callback_data=f"role_{role['id']}"))

    bot.send_message(call.message.chat.id, "Rolni tanlang:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def select_role(call):
    role_id = call.data.split("_")[1]
    try:
        response = requests.get(f"{API_BASE_URL}roles/")
        response.raise_for_status()
        roles = response.json()
        role_name = next(role['name'] for role in roles if str(role['id']) == role_id)
    except requests.RequestException:
        bot.send_message(call.message.chat.id, "Rol ma'lumotlarini olishda xatolik yuz berdi.")
        return

    current_order[call.message.chat.id]['role'] = {'id': role_id, 'name': role_name}

    # Proceed to the next step
    try:
        response = requests.get(f"{API_BASE_URL}countries/")
        response.raise_for_status()
        countries = response.json()
    except requests.RequestException:
        bot.send_message(call.message.chat.id, "Mamlakatlar ma'lumotlarini olishda xatolik yuz berdi.")
        return

    markup = InlineKeyboardMarkup()
    for country in countries:
        markup.add(InlineKeyboardButton(country['name'], callback_data=f"country1_{country['id']}"))

    bot.send_message(call.message.chat.id, "Qayerdan:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("country1_"))
def select_country1(call):
    country1_id = call.data.split("_")[1]
    try:
        response = requests.get(f"{API_BASE_URL}countries/")
        response.raise_for_status()
        countries = response.json()
        country1_name = next(country['name'] for country in countries if str(country['id']) == country1_id)
    except requests.RequestException:
        bot.send_message(call.message.chat.id, "Mamlakatlar ma'lumotlarini olishda xatolik yuz berdi.")
        return

    current_order[call.message.chat.id]['country_1'] = {'id': country1_id, 'name': country1_name}

    # Fetch the list of countries again for the second selection
    markup = InlineKeyboardMarkup()
    for country in countries:
        markup.add(InlineKeyboardButton(country['name'], callback_data=f"country_{country['id']}"))

    bot.edit_message_text("Qayerga:", call.message.chat.id, call.message.id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def select_country(call):
    country_id = call.data.split("_")[1]
    try:
        response = requests.get(f"{API_BASE_URL}countries/")
        response.raise_for_status()
        countries = response.json()
        country_name = next(country['name'] for country in countries if str(country['id']) == country_id)
    except requests.RequestException:
        bot.send_message(call.message.chat.id, "Mamlakat ma'lumotlarini olishda xatolik yuz berdi.")
        return

    current_order[call.message.chat.id]['country'] = {'id': country_id, 'name': country_name}

    # Markazlar ro'yxatini olish
    response = requests.get(f"{API_BASE_URL}centers/", params={"country": country_id})
    if response.status_code == 200:
        centers = response.json()
        markup = InlineKeyboardMarkup()
        for center in centers:
            markup.add(InlineKeyboardButton(center['name'], callback_data=f"center_{center['id']}"))

        bot.edit_message_text(
            "Airoportni tanlang:", call.message.chat.id, call.message.id, reply_markup=markup
        )
    else:
        bot.edit_message_text(
            "Markazlarni olishda xatolik yuz berdi.", call.message.chat.id, call.message.id
        )
        
@bot.callback_query_handler(func=lambda call: call.data.startswith("center_"))
def select_center(call):
    center_id = call.data.split("_")[1]
    country1_id = current_order[call.message.chat.id]['country_1']['id']

    response = requests.get(f"{API_BASE_URL}centers/", params={"country": country1_id})
    if response.status_code == 200:
        centers = response.json()
        center_name = next(center['name'] for center in centers if str(center['id']) == center_id)
        current_order[call.message.chat.id]['centers'] = {'id': center_id, 'name': center_name}

        # Fetch categories
        response = requests.get(f"{API_BASE_URL}categories/")
        if response.status_code == 200:
            categories = response.json()
            markup = InlineKeyboardMarkup()
            for category in categories:
                markup.add(InlineKeyboardButton(category['name'], callback_data=f"category_{category['id']}"))

            bot.edit_message_text("Bagajni tanlang:", call.message.chat.id, call.message.id, reply_markup=markup)
        else:
            bot.edit_message_text("Kategoriyalarni olishda xatolik yuz berdi.", call.message.chat.id, call.message.id)
    else:
        bot.edit_message_text("Markazlarni olishda xatolik yuz berdi.", call.message.chat.id, call.message.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def select_category(call):
    category_id = call.data.split("_")[1]
    try:
        response = requests.get(f"{API_BASE_URL}categories/")
        response.raise_for_status()
        categories = response.json()
        category_name = next(category['name'] for category in categories if str(category['id']) == category_id)
    except requests.RequestException:
        bot.send_message(call.message.chat.id, "Kategoriyani olishda xatolik yuz berdi.")
        return

    current_order[call.message.chat.id]['category'] = {'id': category_id, 'name': category_name}

    bot.send_message(call.message.chat.id, "Buyurtma sanasini kiriting (YYYY-MM-DD):")
    bot.register_next_step_handler(call.message, get_date)

def get_date(message):
    current_order[message.chat.id]['date'] = message.text
    bot.send_message(message.chat.id, "Ismni kiriting:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    current_order[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "Tavsifni kiriting:")
    bot.register_next_step_handler(message, get_description)

def get_description(message):
    current_order[message.chat.id]['description'] = message.text
    bot.send_message(message.chat.id, "Narxni kiriting:")
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    current_order[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "Telefon raqamini kiriting:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    current_order[message.chat.id]['phone'] = message.text

    order_data = current_order[message.chat.id]
    order_preview = f"""
Buyurtma ma'lumotlari:
Rol: {order_data.get('role', {}).get('name')}
Birinchi Mamlakat: {order_data.get('country_1', {}).get('name')}
Ikkinchi Mamlakat: {order_data.get('country', {}).get('name')}
Markaz: {order_data.get('centers', {}).get('name')}
Kategoriya: {order_data.get('category', {}).get('name')}
Sana: {order_data.get('date')}
Ism: {order_data.get('name')}
Tavsif: {order_data.get('description')}
Narx: {order_data.get('price')}
Telefon: {order_data.get('phone')}
    """

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm"))
    markup.add(InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))

    bot.send_message(message.chat.id, order_preview, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["confirm", "cancel"])
def confirm_order(call):
    if call.data == "confirm":
        order_data = current_order.pop(call.message.chat.id, None)

        if not order_data:
            bot.edit_message_text("Buyurtma ma'lumotlari topilmadi.", call.message.chat.id, call.message.id)
            return
        chat_id_country_1 = country_chat_link.get(order_data.get('country_1', {}).get('name'))
        chat_id_country = country_chat_link.get(order_data.get('country', {}).get('name'))
        group_link = chat_id_country_1 or chat_id_country
        # Prepare the order details message
        order_message = (
        "📢 Yangi e'lon\n\n"
        f"📌 E'lon turi: {order_data.get('role', {}).get('name')}\n"
        f"🌍 Jo'natish: {order_data.get('country_1', {}).get('name')}\n"
        f"🛫 Qabul qilish: {order_data.get('country', {}).get('name')}\n"
        f"🏢 Markaz: {order_data.get('centers', {}).get('name')}\n"
        f"🎒 Bagaj: {order_data.get('category', {}).get('name')}\n"
        f"🕒 Vaqt: {order_data.get('date')}\n"
        f"👤 Ism: {order_data.get('name')}\n"
        f"📝 Izoh: {order_data.get('description')}\n"
        f"💵 Narx: {order_data.get('price')}\n"
        f"📞 Kontakt: {order_data.get('phone')} \n\n\n\n"
        f"👥 Guruhga qo'shilish: {group_link}\n"
        "📲 E'lon joylash uchun: https://t.me/pochta_elon_bot"
        )

        # Send the order message to the specific Telegram ID
        chat_id_country_1 = country_chat_ids.get(order_data.get('country_1', {}).get('name'))
        chat_id_country = country_chat_ids.get(order_data.get('country', {}).get('name'))
        chat_id = chat_id_country_1 or chat_id_country

        if not chat_id:
            bot.edit_message_text("Mamlakatga mos chat ID topilmadi.", call.message.chat.id, call.message.id)
            return

        # Send the order message to the specific Telegram ID
        try:
            bot.send_message(chat_id, order_message)
            bot.edit_message_text(f"✅ Buyurtma tasdiqlandi va guruhga yuborildi yuborildi\n\n👥 Guhuh: {group_link}!", call.message.chat.id, call.message.id)
        except Exception as e:
            bot.edit_message_text(f"Xabarni yuborishda xatolik: {e}", call.message.chat.id, call.message.id)
    else:
        current_order.pop(call.message.chat.id, None)
        bot.edit_message_text("❌ Buyurtma bekor qilindi.", call.message.chat.id, call.message.id)


bot.polling(none_stop=True)
