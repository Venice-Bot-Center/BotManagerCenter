import logging

import requests
from django.db import models

log = logging.getLogger(__name__)


class TelegramBot(models.Model):
    name = models.CharField(max_length=50)
    token = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class TelegramChannel(models.Model):
    name = models.CharField(max_length=50)
    token = models.CharField(max_length=50, null=True, blank=True)
    bot = models.ForeignKey(
        TelegramBot, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["bot", "token"]

    def telegram_send(self, text: str) -> tuple[str, bool]:
        url = f"https://api.telegram.org/bot{self.bot.token}/sendMessage"
        message = {
            "chat_id": self.token,
            "text": text,
            "parse_mode": "Markdown",
        }
        r = requests.post(url=url, json=message)
        log.info(r.json())
        if r.json()["ok"]:
            return r.json()["result"]["message_id"], True
        return r.json()["result"]["message_id"], False

    def telegram_channel_delete_message(self, message_id: str = None) -> bool:
        log.info(message_id)
        if message_id is None:
            return False
        url = f"https://api.telegram.org/bot{self.bot.token}/deleteMessage"
        message = {"chat_id": self.token, "message_id": int(message_id)}
        r = requests.get(url=url, json=message)
        log.info(r.json())
        if r.json()["ok"]:
            return True
        else:
            return False


class BotData(models.Model):
    name = models.CharField(max_length=50, unique=True)
    data = models.JSONField(default=dict, null=True, blank=True)
    channel = models.ForeignKey(
        TelegramChannel, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name
