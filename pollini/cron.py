import logging
from functools import cmp_to_key

from botmanager.utility import letter_cmp
from pollini.api import get_dati_continui, get_pollini, get_level
from telebot.exception import BotDataNotExist
from telebot.models import BotData

log = logging.getLogger(__name__)


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
