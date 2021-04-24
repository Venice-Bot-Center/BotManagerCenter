import requests

from botmanager.utility import get_monday


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
