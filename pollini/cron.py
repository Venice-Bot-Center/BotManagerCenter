import datetime
import logging
from functools import cmp_to_key

import requests

from telebot.exception import BotDataNotExist
from telebot.models import BotData

log = logging.getLogger(__name__)


def letter_cmp(a, b):
    if a[2] > b[2]:
        return -1
    if a[2] == b[2]:
        if a[0] > b[0]:
            return 1
        return -1
    else:
        return 1


def get_monday() -> datetime.date:
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday() + 8)


def get_dati_continui() -> dict:
    url = "http://dati.retecivica.bz.it/services/POLLNET_REMARKS"
    payload = {"format": "json", "STAT_ID": "55", "from": str(get_monday())}
    response = requests.request("GET", url, params=payload)
    out = {}
    for e in response.json():
        out[e["PART_ID"]] = e["REMA_CONCENTRATION"]
    return out


def get_pollini() -> dict:
    url = "http://dati.retecivica.bz.it/services/POLLNET_PARTICLES"
    payload = {"format": "json"}
    response = requests.request("GET", url, params=payload)
    out = {}
    for e in response.json():
        if e["PART_NAME_I"] and e["PART_HIGH"] and e["PART_HIGH"] > 0:
            out[e["PART_ID"]] = {
                "name": e["PART_NAME_I"],
                "levels": [e["PART_LOW"], e["PART_MIDDLE"], e["PART_HIGH"]],
            }
    return out


def get_level(limits: list, number: float = 0.0) -> tuple[str, str]:
    if number is None:
        number = 0.0
    if number < limits[0]:
        return "⚪", "None"
    if number < limits[1]:
        return "🟢", "Low"
    if number < limits[2]:
        return "🟠", "Medium"
    return "🔴", "High"


def get_data_from_source() -> list[tuple[str, str, str]]:
    dati = get_dati_continui()
    pollini = get_pollini()
    out = []
    for e in dati:
        try:
            pollin_data = pollini[e]
            pollin_level = dati[e]
            circle, str_level = get_level(
                number=pollin_level, limits=pollin_data["levels"]
            )
            name = pollin_data["name"]
            out.append((circle, str_level, name))
        except KeyError:
            pass
    letter_cmp_key = cmp_to_key(letter_cmp)
    out.sort(key=letter_cmp_key, reverse=True)
    log.debug(out)
    return out


def sender_message(data: dict) -> str:
    message = ""
    for a, b, c in data:
        if b != "None":
            message += f"{a} {c}\n"
    return message


def run():
    db_data, flag = BotData.objects.get_or_create(name="Pollini a Venezia")
    if flag:
        raise BotDataNotExist
    new_hash = data = get_data_from_source()
    if new_hash != db_data.data.get("pollini_hash", None):
        db_data.data["pollini_hash"] = new_hash
        if not db_data.channel.telegram_channel_delete_message(
            message_id=db_data.data.get("pollini_mex", None)
        ):
            log.error("Problemi con la cancellazione")
        db_data.data["pollini_mex"] = db_data.channel.telegram_send(
            sender_message(data)
        )[0]
    db_data.save()
