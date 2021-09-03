import logging

import requests

from marea.api import posting_instant, posting_previsione, adding_data
from marea.api.actv import posting_actv
from marea.api.mose import posting_mose
from telebot.models import BotData

log = logging.getLogger(__name__)

MAREA_API_URL = "http://dati.venezia.it/sites/default/files/dataset/opendata/previsione.json"


def run():
    db_data, flag = BotData.objects.get_or_create(name="Marea a Venezia")
    if not flag:
        r = requests.get(MAREA_API_URL)
        if 200 <= r.status_code < 400:
            datas = r.json()
            max = adding_data(datas, db_data)
            posting_actv(db_data)
            posting_previsione(db_data=db_data, max=max)
            posting_instant(db_data)
            posting_mose(db_data)
        else:
            log.error(f"The marea api return {r.status_code}")
    else:
        log.error("You need to setup the BotData")
