from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from telebot.models import TelegramBot, TelegramChannel, BotData


class TelegramBotAdmin(GuardedModelAdmin):
    list_display = ("name", "token")
    search_fields = ("name", "token")


class TelegramChannelAdmin(GuardedModelAdmin):
    list_display = ("name", "token", "bot")
    search_fields = ("name", "token")


class BotDataAdmin(GuardedModelAdmin):
    list_display = ("name", "channel", "data")
    search_fields = ["name"]


admin.site.register(BotData, BotDataAdmin)
admin.site.register(TelegramBot, TelegramBotAdmin)
admin.site.register(TelegramChannel, TelegramChannelAdmin)
