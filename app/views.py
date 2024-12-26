from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Category, TelegramUser,Role, Order,Centers,Country
import urllib.parse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import requests
from django.utils.safestring import mark_safe
import aiohttp
import asyncio

TELEGRAM_BOT_TOKEN = '7828651431:AAELpI8DuJFcq-M3B6nhPQv_xhJ41QnkeQI'  

TELEGRAM_CHAT_ID_UK = -1002231892574  
TELEGRAM_CHAT_ID_US = -1002440391832
TELEGRAM_CHAT_ID_KSA = -1002316531885
TELEGRAM_CHAT_ID_ITA = -1002340445857
TELEGRAM_CHAT_ID_TK = -1002463421519

def index(request):
    tg_id = request.GET.get('tg_id') or request.session.get('tg_id')
    username = request.GET.get('username') or request.session.get('username')
    first_name = request.GET.get('first_name') or request.session.get('first_name')
    last_name = request.GET.get('last_name') or request.session.get('last_name')
    profile_photo = request.GET.get('profile_photo') or request.session.get('profile_photo')

    if not tg_id:
        return render(request, 'home.html', context={'message': 'Telegram maʼlumotlari yetishmayapti'})

    user = authenticate(request, username=tg_id, password=tg_id)

    if user is None:
        user = User.objects.create_user(username=tg_id, password=tg_id)

    tg_user, created = TelegramUser.objects.get_or_create(user=user)
    tg_user.username = username if username else None
    tg_user.first_name = first_name if first_name else None
    tg_user.last_name = last_name if last_name else None
    tg_user.telegram_id = tg_id

    if profile_photo:
        tg_user.profile_photo = urllib.parse.unquote(profile_photo)
    tg_user.save()

    request.session['tg_id'] = tg_id
    request.session['username'] = username
    request.session['first_name'] = first_name
    request.session['last_name'] = last_name
    request.session['profile_photo'] = profile_photo

    login(request, user)

    if request.method == "POST":
        country_id = request.POST.get("country")
        country_1_id = request.POST.get("country_1")

        if country_id and country_1_id:
            country = Country.objects.get(id=country_id)
            country_1 = Country.objects.get(id=country_1_id)
            if country_id == country_1_id:
                messages.error(
                request,
                mark_safe("Ikki mamlakat bir xil bo'lishi mumkin emas❗<br>Turli mamlakat tanlang")
                )
            elif "UZ 🇺🇿 UZBEKISTAN" not in (country.name, country_1.name):
                messages.error(request, "Biz faqat O'zbekiston bilan boshqa davlatlar o'rtasida jo'natmalarni amalga oshira olamiz❗")
            else:
                request.session['country'] = country_id
                request.session['country_1'] = country_1_id
                return redirect('create')
        else:
            messages.error(request, "Iltimos, har ikkala mamlakatni tanlang.")

    countries = Country.objects.all()
    telegram_user = TelegramUser.objects.get(user=request.user)
    context = {
        'message': 'Tizimga kirdi' if not created else 'Yangi foydalanuvchi yaratildi',
        'telegram_user': tg_user,  # Shablon uchun foydalanuvchini yuborish
        'roles': Role.objects.all(),
        'countries': countries,
    }
    return render(request, "home.html", {"context": context, 'countries': countries, 'telegram_user': telegram_user})


def order_create(request):
    country_id = request.session.get('country')
    country_1_id = request.session.get('country_1')

    if not country_id or not country_1_id:
        return redirect('home_page')

    countries = Country.objects.filter(id__in=[country_id, country_1_id])

    if request.method == "POST":
        try:
            telegram_user = get_object_or_404(TelegramUser, user=request.user)
        except TelegramUser.DoesNotExist:
            messages.error(request, "Foydalanuvchi ma'lumotlari topilmadi.")
            return redirect('home_page')

        role_id = request.POST.get("role")
        center_id = request.POST.get("center")
        category_id = request.POST.get("category")
        date = request.POST.get("date")
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        phone = request.POST.get("phone")

        role = Role.objects.get(id=role_id)
        center = Centers.objects.get(id=center_id)
        category = Category.objects.get(id=category_id)

        order = Order.objects.create(
            user=telegram_user,  # Request foydalanuvchisiga tegishli TelegramUser
            role=role,
            country_1=countries[0],
            country=countries[1],
            centers=center,
            category=category,
            date=date,
            name=name,
            description=description,
            price=price,
            phone=phone
        )
        country_chat_ids = {
                "UK 🇬🇧 UNITED KINGDUM": "https://t.me/ukuzbpochta/1",
                "ITA 🇮🇹 ITALY": "https://t.me/itauzbpochta/1",
                "KSA 🇸🇦 SAUDI": "https://t.me/ksauzbpochta/1",
                "TK 🇹🇷 TURKEY": "https://t.me/tkuzbpochta/1",
                "US 🇺🇸 AMERICA": "https://t.me/usuzbpochta/1",
            }

        group_url = country_chat_ids.get(order.country.name) or country_chat_ids.get(order.country_1.name)

        if not group_url:
            messages.error(request, "Tegishli chat ID topilmadi. Iltimos, ma'lumotlaringizni tekshiring.")
        else:
            messages.success(
                request, 
                mark_safe(f"E'lon muvaffaqiyatli yaratildi! <br><a href='{group_url}' target='_blank'>Guruhni ochish</a>")
            )
        asyncio.run(send_to_telegram_async(order)) 
        return redirect('home')

    roles = Role.objects.all()
    centers = Centers.objects.filter(country_id=country_id)
    categories = Category.objects.all()
    telegram_user = TelegramUser.objects.get(user=request.user)

    return render(request, "create_order.html", {
        "countries": countries,
        "roles": roles,
        "centers": centers,
        "categories": categories,
        "telegram_user": telegram_user,
    })

async def send_to_telegram_async(order):
    """Telegramga asinxron xabar yuborish funksiyasi."""
    message = (
        f"📢 Yangi e'lon\n\n"
        f"📌 E'lon turi: {order.role.name}\n"
        f"🌍 Jo'natish: {order.country.name}\n"
        f"🛫 Qabul qilish: {order.country_1.name}\n"
        f"🎒 Bagaj: {order.category.name}\n"
        f"🏢 Markaz: {order.centers.name}\n"
        f"🕒 Vaqt: {order.date}\n"
        f"👥 Ismi:{order.name}\n"
        f"👤 T.me: @{order.user.username}\n"
        f"📝 Izoh: {order.description}\n"
        f"📞 Kontakt: {order.phone}\n"
        f"💵 Narx: {order.price}\n\n\n"
        f"📲 E'lon joylash uchun: https://t.me/pochta_elon_bot"
    )

    country_chat_ids = {
        "UK 🇬🇧 UNITED KINGDUM": TELEGRAM_CHAT_ID_UK,
        "ITA 🇮🇹 ITALY": TELEGRAM_CHAT_ID_ITA,
        "KSA 🇸🇦 SAUDI": TELEGRAM_CHAT_ID_KSA,
        "TK 🇹🇷 TURKEY": TELEGRAM_CHAT_ID_TK,
        "US 🇺🇸 AMERICA": TELEGRAM_CHAT_ID_US,
    }

    chat_id = country_chat_ids.get(order.country.name) or country_chat_ids.get(order.country_1.name)

    if not chat_id:
        print("Tegishli chat ID topilmadi. Xabar yuborilmaydi.")
        return

    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
    }
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                print("Xabar muvaffaqiyatli yuborildi!")
            else:
                error_text = await response.text()
                print(f"Xatolik: {response.status}, {error_text}")

def my_posts(request):
    telegram_user = TelegramUser.objects.get(user=request.user)
    orders = Order.objects.filter(user=telegram_user)
    return render(request, 'my_posts.html', {'orders': orders,'telegram_user': telegram_user})

def my_profile(request):
    telegram_user = TelegramUser.objects.get(user=request.user)
    return render(request, 'my_profile.html', {'telegram_user': telegram_user})

from rest_framework.viewsets import ModelViewSet
from .models import TelegramUser, Role, Country, Centers, Category, Order
from .serializers import TelegramUserSerializer, RoleSerializer, CountrySerializer, CentersSerializer, CategorySerializer, OrderSerializer

class TelegramUserViewSet(ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer

class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class CentersViewSet(ModelViewSet):
    queryset = Centers.objects.all()
    serializer_class = CentersSerializer

    def get_queryset(self):
        """
        Agar `country` parametri kelsa, querysetni filtrlaydi.
        """
        country_id = self.request.query_params.get('country')
        if country_id:
            return self.queryset.filter(country_id=country_id)
        return self.queryset
    
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
