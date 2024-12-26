from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError

class TelegramUser(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    telegram_id = models.CharField(max_length=150, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profiles', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self) -> str:
        return self.username

class Role(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Country(models.Model):
    choise = (
        ("US 🇺🇸 AMERICA","US 🇺🇸 AMERICA"),
        ("ITA 🇮🇹 ITALY","ITA 🇮🇹 ITALY"),
        ("KSA 🇸🇦 SAUDI","KSA 🇸🇦 SAUDI"),
        ("TK 🇹🇷 TURKEY","TK 🇹🇷 TURKEY"),
        ("UK 🇬🇧 UNITED KINGDUM","UK 🇬🇧 UNITED KINGDUM"),
        ("UZ 🇺🇿 UZBEKISTAN","UZ 🇺🇿 UZBEKISTAN")
    )
    name = models.CharField(max_length=255, choices=choise)

    def __str__(self):
        return self.name

class Centers(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    country_1 = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="country_1")
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    centers = models.ForeignKey(Centers, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.category.name} - {self.date}"

    def get_telegram_message(self):
        """Generate the message content for Telegram."""
        return (
            f"New Order:\n"
            f"Role: {self.role.name}\n"
            f"Country: {self.country.name}\n"
            f"Center: {self.centers.name}\n"
            f"Category: {self.category.name}\n"
            f"Date: {self.date}\n"
            f"Description: {self.description}\n"
            f"Price: {self.price}\n"
        )