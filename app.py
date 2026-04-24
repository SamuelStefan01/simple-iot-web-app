# -*- coding: utf-8 -*-
"""
=============================================================================
IoT Meteorologicka Stanica - Flask Backend
=============================================================================
Tema projektu: IoT meteorologicka stanica
  - Prijima namerané hodnoty zo senzorov (teplota, tlak, rychlost vetra)
  - Prevadza fyzikalne jednotky medzi rozlichnymi sustavami
  - Uklada historiu prevodov do suboru prevody.json
  - Poskytuje REST API pre klientsky dashboard (Frontend B)

Autor: Samuel Stefan
Predmet: Internet veci
=============================================================================
"""

# Importy knizhnic
# Flask       = webovy framework (zaklad servera)
# request     = objekt na citanie dat z URL parametrov (?cislo1=10&...)
# jsonify     = pomocnik na odosielanie JSON odpovedi (pre API)
# render_template = nacitanie HTML sablon z priecinka "templates/"
# flask_cors  = riesenie CORS politiky (povolenie komunikacie medzi domenami)
# sqlite3     = vstavana Python knizhnica na pracu s databazou
# datetime    = praca s datumom a casom
# json, os    = praca s JSON suborom prevody.json

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import datetime
import json
import os

# Vytvorenie aplikacie
# Flask(__name__) = vytvori instanciu Flask aplikacie
# CORS(app)       = povoli komunikaciu z INYCH domien (Frontend B ma inu URL!)
app = Flask(__name__)
CORS(app)  # Bez tohto by Frontend B nemohol komunikovat s backendom!

# ============================================================================
# DATABAZA - SQLite
# ============================================================================
# SQLite je jednoduchá databaza ulozena v jednom subore (databaza.db).
# Tabulka "vypocty": id, cislo1, cislo2, operacia, vysledok, cas

DATABASE = "databaza.db"


def inicializuj_databazu():
    """
    Vytvori tabulku 'vypocty', ak este neexistuje.
    Vola sa raz pri starte servera.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vypocty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cislo1 REAL NOT NULL,
            cislo2 REAL NOT NULL,
            operacia TEXT NOT NULL,
            vysledok REAL NOT NULL,
            cas TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Databaza inicializovana.")


def uloz_do_databazy(cislo1, cislo2, operacia, vysledok):
    """
    Ulozi jeden zaznam o vypocte do databazy.
    Vracia int: ID noveho zaznamu.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cas = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO vypocty (cislo1, cislo2, operacia, vysledok, cas) VALUES (?, ?, ?, ?, ?)",
        (cislo1, cislo2, operacia, vysledok, cas)
    )
    conn.commit()
    nove_id = cursor.lastrowid
    conn.close()
    return nove_id


def nacitaj_vsetky_vypocty():
    """
    Nacita VSETKY zaznamy z tabulky 'vypocty'.
    Vracia list slovnikov (dict).
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vypocty ORDER BY id DESC")
    riadky = cursor.fetchall()
    conn.close()
    return [dict(riadok) for riadok in riadky]


# ============================================================================
# ROUTE 1: Hlavna stranka (Frontend A - Administracny)
# URL: /
# ============================================================================

@app.route("/")
def hlavna_stranka():
    """Zobrazí hlavnu stranku - Frontend A."""
    return render_template("frontend_a.html")


# ============================================================================
# ROUTE 2: Vypocet (spracovanie formulara)
# URL: /vypocet?cislo1=10&cislo2=5&operacia=plus
# GET parametre su VIDITELNE v URL - podmienka zadania
# ============================================================================

@app.route("/vypocet")
def vypocet():
    """
    Prijme cisla a operaciu cez GET parametre, vykona vypocet,
    ulozi do databazy a vrati vysledok ako JSON.

    Priklad URL: /vypocet?cislo1=10&cislo2=5&operacia=plus
    """
    # Krok 1: Citanie parametrov z URL
    cislo1_str = request.args.get("cislo1", "0")
    cislo2_str = request.args.get("cislo2", "0")
    operacia = request.args.get("operacia", "plus")

    # Krok 2: Validacia vstupov
    try:
        cislo1 = float(cislo1_str)
        cislo2 = float(cislo2_str)
    except ValueError:
        return jsonify({"chyba": "Neplatne cisla! Zadajte ciselne hodnoty."}), 400

    # Krok 3: Vypocet podla zvolenej operacie
    if operacia == "plus":
        vysledok = cislo1 + cislo2
    elif operacia == "minus":
        vysledok = cislo1 - cislo2
    elif operacia == "krat":
        vysledok = cislo1 * cislo2
    elif operacia == "deleno":
        if cislo2 == 0:
            return jsonify({"chyba": "Delenie nulou nie je mozne!"}), 400
        vysledok = cislo1 / cislo2
    else:
        return jsonify({"chyba": "Neznama operacia: " + operacia}), 400

    # Krok 4: Ulozenie do databazy
    nove_id = uloz_do_databazy(cislo1, cislo2, operacia, vysledok)

    # Krok 5: Vratie vysledku ako JSON
    return jsonify({
        "id": nove_id,
        "cislo1": cislo1,
        "cislo2": cislo2,
        "operacia": operacia,
        "vysledok": round(vysledok, 4),
        "cas": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# ============================================================================
# ROUTE 3: API - Ziskanie historie vypoctov
# URL: /api/historia
# ============================================================================

@app.route("/api/historia")
def historia():
    """
    API endpoint - vrati celu historiu vypoctov ako JSON pole.
    Pouziva Frontend B na zobrazenie live feedu.
    """
    vypocty = nacitaj_vsetky_vypocty()
    return jsonify(vypocty)


# ============================================================================
# ROUTE 4: API - Posledny vypocet
# URL: /api/posledny
# ============================================================================

@app.route("/api/posledny")
def posledny_vypocet():
    """API endpoint - vrati iba posledny vykonany vypocet."""
    vypocty = nacitaj_vsetky_vypocty()
    if vypocty:
        return jsonify(vypocty[0])
    else:
        return jsonify({"info": "Zatial neboli vykonane ziadne vypocty."}), 404


# ============================================================================
# ROUTE 5: API - Statistiky
# URL: /api/statistiky
# ============================================================================

@app.route("/api/statistiky")
def statistiky():
    """API endpoint - vrati zakladne statistiky o vypoctoch."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM vypocty")
    pocet = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(vysledok) FROM vypocty")
    priemer = cursor.fetchone()[0]

    cursor.execute("SELECT operacia, COUNT(*) as pocet FROM vypocty GROUP BY operacia")
    podla_operacie = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    return jsonify({
        "celkovy_pocet": pocet,
        "priemerny_vysledok": round(priemer, 4) if priemer else 0,
        "podla_operacie": podla_operacie
    })


# ============================================================================
# ROUTE 6: Frontend B (Klientsky/IoT pohlad)
# URL: /klient
# ============================================================================

@app.route("/klient")
def klientsky_pohlad():
    """Zobrazi Frontend B - klientsky/IoT pohlad."""
    return render_template("frontend_b.html")


# ============================================================================
# ROUTE 7: IoT Simulacia (ESP32 / senzor)
# URL: /iot/odosli?teplota=22.5&vlhkost=60
# ============================================================================

@app.route("/iot/odosli")
def iot_odosli():
    """
    Simulacia IoT endpointu - prijima data zo senzora.
    V realnom svete by ESP32 posielal HTTP GET request na tento endpoint.
    """
    teplota = request.args.get("teplota", type=float)
    vlhkost = request.args.get("vlhkost", type=float)

    if teplota is None or vlhkost is None:
        return jsonify({"chyba": "Chybaju parametre teplota a vlhkost!"}), 400

    return jsonify({
        "status": "ok",
        "prijate_data": {
            "teplota": teplota,
            "vlhkost": vlhkost,
            "cas": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "sprava": "Data zo senzora boli uspesne prijate."
    })


# ============================================================================
# PREVODNIK METEOROLOGICKYCH JEDNOTIEK
# ============================================================================
# Tema projektu: IoT meteorologicka stanica prevadza namerané fyzikalne veliciny
# Podporene prevody (podmienka zadania: min. 3):
#   c_to_f     : stupne Celzia -> Fahrenheit    (teplota zo senzora)
#   hpa_to_mmhg: hektopascaly -> milimetre rtuti (atmosfericky tlak)
#   ms_to_kmh  : metre/sekunda -> km/hodinu      (rychlost vetra)
#
# Data sa ukladaju do suboru prevody.json (zoznam JSON objektov).

SUBOR_PREVODOV = "prevody.json"


def nacitaj_prevody():
    """
    Nacita historiu prevodov zo suboru prevody.json.

    Vracia:
        list: Zoznam slovnikov, kazdy predstavuje jeden prevod.
              Ak subor neexistuje, vrati prazdny zoznam.
    """
    if not os.path.exists(SUBOR_PREVODOV):
        return []
    with open(SUBOR_PREVODOV, "r", encoding="utf-8") as f:
        return json.load(f)


def uloz_prevod(zaznam):
    """
    Prida novy zaznam prevodu do suboru prevody.json.

    Parametre:
        zaznam (dict): Slovnik s klucmi hodnota, typ, vysledok, popis, cas.
    """
    prevody = nacitaj_prevody()
    prevody.append(zaznam)
    with open(SUBOR_PREVODOV, "w", encoding="utf-8") as f:
        json.dump(prevody, f, ensure_ascii=False, indent=2)


# ============================================================================
# ROUTE 8: API - Prevodnik jednotiek
# URL: /api/prevod?hodnota=25&typ=c_to_f
# GET parametre (viditelne v URL - podmienka zadania):
#   hodnota : ciselna hodnota na prevod (float)
#   typ     : druh prevodu (c_to_f | hpa_to_mmhg | ms_to_kmh)
# ============================================================================

@app.route("/api/prevod")
def prevod():
    """
    Prijme meteorologicku hodnotu a typ prevodu cez 2 GET parametre,
    vykona konverziu jednotiek a ulozi zaznam do prevody.json.

    Priklady URL:
        /api/prevod?hodnota=25&typ=c_to_f         -> 25 C = 77.00 F
        /api/prevod?hodnota=1013&typ=hpa_to_mmhg  -> 1013 hPa = 759.81 mmHg
        /api/prevod?hodnota=10&typ=ms_to_kmh      -> 10 m/s = 36.00 km/h
    """
    # Krok 1: Citanie 2 GET parametrov z URL (?hodnota=...&typ=...)
    hodnota = request.args.get("hodnota", type=float)
    typ = request.args.get("typ", "c_to_f")

    # Krok 2: Validacia vstupnej hodnoty
    if hodnota is None:
        return jsonify({"chyba": "Zadajte ciselnu hodnotu parametrom 'hodnota'!"}), 400

    # Krok 3: Vypocet podla zvoleného druhu prevodu
    if typ == "c_to_f":
        # Teplota: Celzius -> Fahrenheit (vzorec: F = C * 9/5 + 32)
        v = hodnota * 9 / 5 + 32
        popis = "{} C = {:.2f} F".format(hodnota, v)
    elif typ == "hpa_to_mmhg":
        # Tlak: hektopascaly -> milimetre rtuti (1 hPa = 0.75006 mmHg)
        v = hodnota * 0.75006
        popis = "{} hPa = {:.2f} mmHg".format(hodnota, v)
    elif typ == "ms_to_kmh":
        # Rychlost vetra: metre/sekunda -> kilometre/hodina (1 m/s = 3.6 km/h)
        v = hodnota * 3.6
        popis = "{} m/s = {:.2f} km/h".format(hodnota, v)
    else:
        return jsonify({"chyba": "Neznamy typ prevodu: {}. Povolene: c_to_f, hpa_to_mmhg, ms_to_kmh".format(typ)}), 400

    # Krok 4: Zostavenie zaznamu a ulozenie do prevody.json
    zaznam = {
        "hodnota": hodnota,
        "typ": typ,
        "vysledok": round(v, 2),
        "popis": popis,
        "cas": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    uloz_prevod(zaznam)

    # Krok 5: Vratie JSON odpovede
    return jsonify(zaznam)


# ============================================================================
# ROUTE 9: API - Historia prevodov
# URL: /api/historia-prevodov
# Cita prevody.json a vracia cely zoznam ako JSON pole.
# Ak subor este neexistuje, vracia prazdne pole [].
# ============================================================================

@app.route("/api/historia-prevodov")
def historia_prevodov():
    """
    API endpoint - vrati historiu vsetkych prevodov jednotiek.
    Frontend B pravidelne vola tento endpoint a zobrazuje tabulku.

    Vystup (JSON pole):
        [
          {"hodnota": 25, "typ": "c_to_f", "vysledok": 77.0,
           "popis": "25 C = 77.00 F", "cas": "2026-04-24 10:00:00"},
          ...
        ]
    """
    return jsonify(nacitaj_prevody())


# ============================================================================
# START SERVERA
# ============================================================================
# Tento blok sa spusti len ak spustime subor priamo (python app.py)
# host="0.0.0.0" = server pocuva na vsetkych sietovych rozhraniach
# port=5000      = standardny Flask port
# debug=True     = automaticky restartuje server pri zmene kodu (len pre vyvoj!)

if __name__ == "__main__":
    inicializuj_databazu()
    print("=" * 60)
    print("IoT Backend Server bezi!")
    print("=" * 60)
    print("   Frontend A (Admin):       http://localhost:5000/")
    print("   Frontend B (Klient):      http://localhost:5000/klient")
    print("   API Historia:             http://localhost:5000/api/historia")
    print("   API Statistiky:           http://localhost:5000/api/statistiky")
    print("   IoT Endpoint:             http://localhost:5000/iot/odosli?teplota=22&vlhkost=60")
    print("   Prevodnik (c_to_f):       http://localhost:5000/api/prevod?hodnota=25&typ=c_to_f")
    print("   Prevodnik (hpa_to_mmhg):  http://localhost:5000/api/prevod?hodnota=1013&typ=hpa_to_mmhg")
    print("   Prevodnik (ms_to_kmh):    http://localhost:5000/api/prevod?hodnota=10&typ=ms_to_kmh")
    print("   Historia prevodov:        http://localhost:5000/api/historia-prevodov")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
