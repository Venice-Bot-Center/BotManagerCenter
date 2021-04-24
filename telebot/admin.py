from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from telebot.models import TelegramBot, TelegramChannel


class TelegramBotAdmin(GuardedModelAdmin):
    list_display = ("name", "token")
    search_fields = ("name", "token")


admin.site.register(TelegramBot, TelegramBotAdmin)


class TelegramChannelAdmin(GuardedModelAdmin):
    list_display = ("name", "token", "bot")
    search_fields = ("name", "token")


admin.site.register(TelegramChannel, TelegramChannelAdmin)
