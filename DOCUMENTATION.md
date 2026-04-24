# DOCUMENTATION.md — IoT Meteorologická Stanica

## Téma projektu

**IoT Meteorologická Stanica** — trojvrstvový IoT systém simulujúci backend meteorologickej stanice.  
Systém prijíma namerané fyzikálne veličiny zo senzorov (teplota, atmosferický tlak, rýchlosť vetra),
prevádza ich medzi mernými sústavami a zobrazuje výsledky na klientskom dashboarde v reálnom čase.

Príklad použitia: ESP32 so senzorom BME280 odošle teplotu (napr. 24 °C) a tlak (napr. 1013 hPa)
na backend, kde sa dáta prevedú do požadovaných jednotiek a uložia do histórie.

---

## Architektúra

```
Frontend A (admin panel)  ──GET /vypocet?...──────▶  Flask backend (app.py)
                          ──GET /api/prevod?...───▶   + SQLite (databaza.db)
Frontend B (IoT dashboard)◀──fetch /api/historia──   + JSON  (prevody.json)
ESP32 / senzor            ──GET /iot/odosli?...───▶
```

---

## Splnené podmienky zadaní

### zadanie_na_doma.py — 10 bodov

| # | Podmienka | Stav | Kde |
|---|-----------|------|-----|
| 1 | Nový endpoint `/api/prevod` s min. **2 GET parametrami** (`hodnota`, `typ`), vracia JSON, výsledok sa ukladá | ✅ | `app.py` — route `/api/prevod` |
| 2 | Frontend A: **`<input type="number">`** | ✅ | `templates/frontend_a.html` — karta Prevodník |
| 3 | Frontend A: **`<select>`** (výber typu prevodu) | ✅ | `templates/frontend_a.html` — element `#pTyp` |
| 4 | Frontend A: **`<button type="submit">`** | ✅ | `templates/frontend_a.html` — tlačidlo „Previesť jednotky" |
| 5 | Frontend B: načítanie cez **`fetch()`** a zobrazenie výsledkov z nového endpointu | ✅ | `templates/frontend_b.html` — funkcia `nacitajPrevody()` |
| 6 | GET parametre **viditeľné v URL** | ✅ | URL: `/api/prevod?hodnota=25&typ=c_to_f` |
| 7 | Okomentovaný kód (všetky 3 súbory) | ✅ | `app.py`, `frontend_a.html`, `frontend_b.html` |

### zadanie_na_Azure.py — 5 bodov

| # | Podmienka | Stav | Kde |
|---|-----------|------|-----|
| 1 | `/api/prevod` — prijme `hodnota` + `typ`, podporuje **3 prevody** (`c_to_f`, `hpa_to_mmhg`, `ms_to_kmh`), uloží do **`prevody.json`** | ✅ | `app.py` — funkcie `uloz_prevod()`, `prevod()` |
| 2 | `/api/historia-prevodov` — prečíta `prevody.json`, vráti JSON (ak súbor chýba → `[]`) | ✅ | `app.py` — funkcie `nacitaj_prevody()`, `historia_prevodov()` |
| 3 | Frontend A formulár — input (number) + select + submit + zobrazenie výsledku | ✅ | `templates/frontend_a.html` — karta Prevodník |
| 4 | Frontend B — tabuľka (vstup, typ, výsledok, čas) cez `fetch()` | ✅ | `templates/frontend_b.html` — tabuľka `#tabPrevody` |
| 5 | Funkčné nasadenie na **Azure App Service** | ⬜ | Pozri postup v `NAVOD_PROJEKT.md` kapitola 5 |

---

## Popis implementovaných súborov

### `app.py`

Flask backend s 9 routami:

- `/` — Frontend A (administračný panel)
- `/klient` — Frontend B (klientský dashboard)
- `/vypocet?cislo1=&cislo2=&operacia=` — kalkulačka, ukladá do SQLite
- `/api/historia` — celá história výpočtov z SQLite
- `/api/posledny` — posledný výpočet
- `/api/statistiky` — štatistiky (počet, priemer, podľa operácie)
- `/iot/odosli?teplota=&vlhkost=` — simulácia IoT senzora
- `/api/prevod?hodnota=&typ=` — **prevodník jednotiek** (ukladá do `prevody.json`)
- `/api/historia-prevodov` — historia prevodov z `prevody.json`

Podporované prevody:

| Kód | Konverzia | Vzorec |
|-----|-----------|--------|
| `c_to_f` | °C → °F (teplota) | `F = C × 9/5 + 32` |
| `hpa_to_mmhg` | hPa → mmHg (atmosferický tlak) | `mmHg = hPa × 0.75006` |
| `ms_to_kmh` | m/s → km/h (rýchlosť vetra) | `km/h = m/s × 3.6` |

### `templates/frontend_a.html`

Administračný panel s dvoma kartami:
1. **Kalkulačka** — 2× `<input type="number">` + 4× `<input type="radio">` + `<button type="submit">`
2. **Prevodník meteorologických jednotiek** — `<input type="number">` + `<select>` + `<button type="submit">`

Obe sekcie zobrazujú ukážku URL requestu v reálnom čase (viditeľné GET parametre).

### `templates/frontend_b.html`

Klientský dashboard so 4 kartami:
1. **Posledný výpočet** — veľký číselný display
2. **Štatistiky** — grid (počet, priemer, sčítania, odčítania)
3. **Live Feed** — zoznam všetkých výpočtov, obnova každých 5 s
4. **História prevodov meteorologických jednotiek** — tabuľka (vstup, typ, výsledok, čas), `fetch()` každých 5 s

### `requirements.txt`

```
Flask==3.1.1
flask-cors==5.0.1
gunicorn==23.0.0
```

### `startup.sh`

```bash
gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app
```

---

## Overenie funkčnosti (manuálne testy)

```
GET /                                              → zobrazí kalkulačku (Frontend A)
GET /klient                                        → zobrazí dashboard (Frontend B)
GET /vypocet?cislo1=10&cislo2=5&operacia=plus      → {"vysledok": 15}
GET /api/prevod?hodnota=25&typ=c_to_f              → {"popis": "25.0 C = 77.00 F"}
GET /api/prevod?hodnota=1013&typ=hpa_to_mmhg       → {"popis": "1013.0 hPa = 759.81 mmHg"}
GET /api/prevod?hodnota=10&typ=ms_to_kmh           → {"popis": "10.0 m/s = 36.00 km/h"}
GET /api/historia-prevodov                         → JSON pole všetkých prevodov (alebo [])
GET /iot/odosli?teplota=22.5&vlhkost=60            → {"status": "ok", ...}
```

---

## Lokálne spustenie

```bash
cd simple-iot-web-app
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
python app.py
```

Otvor `http://localhost:5000/` (Frontend A) a `http://localhost:5000/klient` (Frontend B).

---

## Nasadenie na Azure

Postup viz `NAVOD_PROJEKT.md` kapitola 5. Skrátene:

1. Azure Portal → Create Web App (Python 3.11, Linux, Free F1, West Europe)
2. Startup Command: `gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app`
3. HTTPS Only: **Off**
4. ZIP Deploy cez Kudu (Advanced Tools) — súbory musia byť v **koreni** archívu
5. Počkať ~2 min, overiť URL `https://<meno>.azurewebsites.net/`

---

## Autor

Samuel Štefan | Predmet: Internet vecí | TUKE | 2026
