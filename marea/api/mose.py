import logging
from statistics import mean

import requests

from telebot.models import BotData

log = logging.getLogger(__name__)

API_URL_MOSE = (
    "https://dati.venezia.it/sites/default/files/dataset/opendata/livello.json"
)

STAZIONI_LAGUNA = [
    "01025",
    "01030",
    "01033",
    "01036",
    "01037",
    "01028",
    "01032",
    "01045",
    "01029",
]
STAZIONI_MARE = ["01023", "01024", "01022", "01021"]


def get_api_mose() -> tuple[float, float]:
    r = requests.get(API_URL_MOSE)

    st_lag = []
    st_mare = []
    for stazione in r.json():
        if stazione["ID_stazione"] in STAZIONI_LAGUNA:
            st_lag.append(float(stazione["valore"].split(" ")[0]))
        else:
            st_mare.append(float(stazione["valore"].split(" ")[0]))
    lag = round(mean(st_lag), 4)
    mare = round(mean(st_mare), 4)
    log.info(f"La media lagunare é di {lag} e quella di mare é {mare}")
    return lag, mare


def is_mose_up(soglia=1.0) -> bool:
    lag, mare = get_api_mose()
    diff = round(abs(lag - mare), 4)
    log.info(f"La differenza é di {diff} con soglia a {soglia}")
    return diff > soglia


if __name__ == "__main__":
    is_mose_up()


def posting_mose(db_data: BotData):
    if is_mose_up():
        if db_data.data["message_mose"] is None:
            message, _ = db_data.channel.telegram_send(
                "❤️ Il mose é attualmente in funzione ❤️️"
            )
            db_data.data["message_mose"] = message
    else:
        if db_data.data.get("message_mose", None):
            db_data.channel.telegram_channel_delete_message(
                db_data.data["message_mose"]
            )
            db_data.data["message_mose"] = None
    db_data.save()
