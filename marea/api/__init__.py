from marea.api.marea import get_istantanea_marea, get_percentuale_allagamento
from marea.api.wind import get_vento
from telebot.models import BotData

UP = "🔺"
DOWN = "🔻"
TIMEWATCH = "⌚"
CALENDAR = "📆"
STAR = "🌟"


class Previsione:
    def __init__(self, previsione, estremale, tipo, valore):
        self.data_previsione = previsione
        self.data_estremale = estremale
        self.date, self.time = self.data_estremale.split(" ")
        self.tipo = tipo
        self.valore = valore

    def min_max(self, hight=98) -> str:
        arrow = DOWN if self.tipo == "min" else UP
        star = STAR if int(self.valore) >= int(hight) else ""
        return f"{arrow}{self.valore}{star}"

    def hour(self):
        return TIMEWATCH + str(self.time)

    def long_string(self, hight=94):
        min_max = self.min_max(hight)
        return f"{CALENDAR}{self.date}{TIMEWATCH}{self.time}{min_max}\n"

    def __str__(self):
        return self.long_string()


def adding_data(input_dict: dict, db_data: BotData):
    maximum = -400
    db_data.data["lastest"] = db_data.data.get("last", None)
    prevision = []
    for data in input_dict:
        d = Previsione(
            data["DATA_PREVISIONE"],
            data["DATA_ESTREMALE"],
            data["TIPO_ESTREMALE"],
            data["VALORE"],
        )
        maximum = max(int(maximum), int(data["VALORE"]))
        prevision.append(str(d))
        db_data.data["last"] = input_dict[0]["DATA_PREVISIONE"]
    db_data.data["prevision"] = prevision
    db_data.save()
    return maximum


def posting_previsione(db_data: BotData):
    if db_data.data["lastest"] == db_data.data["last"]:
        return
    if db_data.data.get("message_id", None) is not None:
        db_data.channel.telegram_channel_delete_message(
            db_data.data["message_id"]
        )
    estended = ""
    for s in db_data.data["prevision"]:
        estended += s
    message, flag = db_data.channel.telegram_send(estended)
    if flag:
        db_data.data["message_id"] = message
    db_data.save()


def posting_instant(db_data: BotData):

    hight = get_istantanea_marea()
    allagamento = get_percentuale_allagamento(hight)
    vento, vento_max = get_vento()
    last_hight_db = db_data.data.get("instante", 0)

    if int(hight) == int(last_hight_db):
        return

    db_data.data["instante"] = hight

    db_data.channel.telegram_channel_delete_message(
        db_data.data.get("message_hight", None)
    )

    if allagamento > 0:
        estended = f"⚠️ Ultima misurazione è cm {hight}⚠️\n🥾La percentuale di Venezia allagata é di {allagamento}%🥾\n🎏Il vento è {vento:.2f} km/h e al massimo il vento è {vento_max:.2f} km/h🎏/n"
        message, flag = db_data.channel.telegram_send(estended)
        if flag:
            db_data.data["message_hight"] = message
    db_data.save()
