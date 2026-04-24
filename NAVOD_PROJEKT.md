# NAVOD_PROJEKT.md — IoT Flask app + Azure

> Stručný referenčný návod pre mňa aj pre LLM, ktorý bude projekt ďalej upravovať.
> Cieľ: **(1) pochopiť čo projekt robí** a **(2) splniť všetky podmienky oboch zadaní** (`zadanie_na_doma.py` — 10 b., `zadanie_na_Azure.py` — 5 b.) vrátane nasadenia na Azure.

---

## 1. Čo projekt robí (30-sekundový prehľad)

Trojvrstvový IoT systém — jeden Flask backend, dve webové rozhrania, komunikácia cez HTTP GET + JSON.

```
Frontend A (admin)  ──GET /vypocet?cislo1=&cislo2=&operacia=──▶  Flask backend (app.py)
Frontend B (IoT)    ◀──fetch /api/historia, /api/statistiky──   + SQLite (databaza.db)
ESP32 / senzor      ──GET /iot/odosli?teplota=&vlhkost=─────▶   + (pridávané) prevody.json
```

- **`app.py`** — Flask + `flask-cors`. Endpointy: `/`, `/vypocet`, `/api/historia`, `/api/posledny`, `/api/statistiky`, `/klient`, `/iot/odosli`. SQLite tabuľka `vypocty(id, cislo1, cislo2, operacia, vysledok, cas)`.
- **`templates/frontend_a.html`** — admin kalkulačka. Má `BACKEND_URL = window.location.origin` → funguje lokálne aj na Azure bez zmeny.
- **`templates/frontend_b.html`** — read-only dashboard, pollovanie každých 5 s.
- **`requirements.txt`** — `Flask==3.1.1`, `flask-cors==5.0.1`, `gunicorn==23.0.0`.
- **`startup.sh`** — `gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app` (pre Azure).

---

## 2. Lokálne spustenie

```bash
git clone https://github.com/SamuelStefan01/simple-iot-web-app.git
cd simple-iot-web-app
python -m venv .venv && .venv\Scripts\activate    # Windows
pip install -r requirements.txt
python app.py
```

Otvor: `http://localhost:5000/` (Frontend A), `http://localhost:5000/klient` (Frontend B).
`databaza.db` vznikne automaticky.

---

## 3. Podmienky zadaní — kontrolný zoznam

### 3.1 `zadanie_na_doma.py` (10 bodov, všeobecnejšie)

| # | Podmienka | Kde to splniť |
|---|---|---|
| ✅ | Nový backend endpoint s min. **2 GET parametrami**, vracia JSON, výsledok sa ukladá | `app.py` → `@app.route("/api/prevod")` |
| ✅ | Frontend A: **`<input type="number">`** + **`<select>` alebo `<input type="radio">`** + **`<button type="submit">`** | `templates/frontend_a.html` |
| ✅ | Frontend B: načítanie cez `fetch()` a zobrazenie výsledkov z nového endpointu | `templates/frontend_b.html` |
| ✅ | GET parametre **viditeľné v URL** (nie POST) | Vo fetch URL: `?hodnota=...&typ=...` |
| ✅ | Okomentovaný kód | Všetky 3 súbory |

### 3.2 `zadanie_na_Azure.py` (5 bodov, konkrétne — prevodník jednotiek)

| # | Podmienka | Kde to splniť |
|---|---|---|
| ✅ | `/api/prevod` — prijme `hodnota` + `typ`, podporí min. **3 prevody** (`c_to_f`, `hpa_to_mmhg`, `ms_to_kmh`), uloží do **`prevody.json`** (zoznam) | `app.py` |
| ✅ | `/api/historia-prevodov` — prečíta `prevody.json`, vráti JSON (ak súbor chýba → `[]`) | `app.py` |
| ✅ | Frontend A formulár — input (number) + select + submit, zobrazí výsledok | `frontend_a.html` |
| ✅ | Frontend B — tabuľka (vstup, typ, výsledok, čas), dáta cez `fetch()` | `frontend_b.html` |
| ✅ | **Funkčné nasadenie na Azure App Service** | kapitola 5 |

> Obe zadania sa prekrývajú. Implementáciou **prevodníka z 3.2 splním aj všetkých 10 b. zo zadania 3.1** (jeden endpoint + jeden formulár + jedno zobrazenie pokryje obe).

---

## 4. Čo pridať do kódu (minimálna implementácia)

### 4.1 `app.py` — pridaj na koniec (pred `if __name__ == "__main__"`)

```python
import json, os
SUBOR_PREVODOV = "prevody.json"

def nacitaj_prevody():
    if not os.path.exists(SUBOR_PREVODOV):
        return []
    with open(SUBOR_PREVODOV, "r", encoding="utf-8") as f:
        return json.load(f)

def uloz_prevod(zaznam):
    prevody = nacitaj_prevody()
    prevody.append(zaznam)
    with open(SUBOR_PREVODOV, "w", encoding="utf-8") as f:
        json.dump(prevody, f, ensure_ascii=False, indent=2)

@app.route("/api/prevod")
def prevod():
    hodnota = request.args.get("hodnota", type=float)
    typ = request.args.get("typ", "c_to_f")
    if hodnota is None:
        return jsonify({"chyba": "Zadajte hodnotu!"}), 400

    if typ == "c_to_f":
        v = hodnota * 9/5 + 32;   popis = f"{hodnota} °C = {v:.2f} °F"
    elif typ == "hpa_to_mmhg":
        v = hodnota * 0.75006;    popis = f"{hodnota} hPa = {v:.2f} mmHg"
    elif typ == "ms_to_kmh":
        v = hodnota * 3.6;        popis = f"{hodnota} m/s = {v:.2f} km/h"
    else:
        return jsonify({"chyba": f"Neznámy typ: {typ}"}), 400

    zaznam = {
        "hodnota": hodnota, "typ": typ,
        "vysledok": round(v, 2), "popis": popis,
        "cas": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    uloz_prevod(zaznam)
    return jsonify(zaznam)

@app.route("/api/historia-prevodov")
def historia_prevodov():
    return jsonify(nacitaj_prevody())
```

### 4.2 `templates/frontend_a.html` — pridaj ďalšiu `.card` pod kalkulačku

```html
<div class="card">
  <h2>🌡️ Prevodník jednotiek</h2>
  <form onsubmit="return odosliPrevod(event)">
    <div class="form-group">
      <label>Hodnota:</label>
      <input type="number" id="pHodnota" step="any" required>
    </div>
    <div class="form-group">
      <label>Typ prevodu:</label>
      <select id="pTyp" style="width:100%;padding:12px;border-radius:8px;">
        <option value="c_to_f">°C → °F</option>
        <option value="hpa_to_mmhg">hPa → mmHg</option>
        <option value="ms_to_kmh">m/s → km/h</option>
      </select>
    </div>
    <button type="submit" class="submit-btn">Previesť</button>
  </form>
  <div id="pVystup" style="margin-top:15px;color:#00d4ff;"></div>
</div>

<script>
async function odosliPrevod(e) {
  e.preventDefault();
  const h = document.getElementById("pHodnota").value;
  const t = document.getElementById("pTyp").value;
  const r = await fetch(`${BACKEND_URL}/api/prevod?hodnota=${h}&typ=${t}`);
  const d = await r.json();
  document.getElementById("pVystup").innerText = d.popis || d.chyba;
  return false;
}
</script>
```

### 4.3 `templates/frontend_b.html` — pridaj ďalšiu `.card` pod Live Feed

```html
<div class="card">
  <h2>🌡️ História prevodov</h2>
  <table class="history-table" id="tabPrevody">
    <thead><tr><th>Vstup</th><th>Typ</th><th>Výsledok</th><th>Čas</th></tr></thead>
    <tbody></tbody>
  </table>
</div>

<script>
async function nacitajPrevody() {
  try {
    const r = await fetch(`${backendUrl || window.location.origin}/api/historia-prevodov`);
    const data = await r.json();
    const tbody = document.querySelector("#tabPrevody tbody");
    tbody.innerHTML = data.map(p =>
      `<tr><td>${p.hodnota}</td><td>${p.typ}</td>
       <td style="color:#e94560;">${p.vysledok}</td><td>${p.cas}</td></tr>`
    ).join("");
  } catch (err) { /* ignoruj, ak backend offline */ }
}
setInterval(nacitajPrevody, 5000);
nacitajPrevody();
</script>
```

> `BACKEND_URL` (frontend_a) a `backendUrl` (frontend_b) sú **už definované** v existujúcich HTML súboroch — netreba ich zavádzať znova.

---

## 5. Nasadenie na Azure (Free F1, ZIP Deploy)

### 5.1 Vytvor Web App

Portal → **Create → Web App**:
- *Name:* `iot-backend-stefan` (URL: `https://iot-backend-stefan.azurewebsites.net`)
- *Runtime:* **Python 3.11**, *OS:* **Linux**, *Region:* **West Europe**, *Plan:* **Free F1**

### 5.2 Konfigurácia (Settings → Configuration)

- **General settings → Startup Command:**
  `gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app`
- **General settings → HTTPS Only:** **Off** (kvôli ESP32 a pod.)
- Save → Restart.

### 5.3 Deploy

ZIP so súbormi **v koreni archívu** (nie v podpriečinku!):
```
app.py
requirements.txt
startup.sh
templates/frontend_a.html
templates/frontend_b.html
```
Kudu: **Advanced Tools → Go → Tools → Zip Push Deploy** → pretiahni ZIP. Počkaj ~2 min.

Alternatíva jedným príkazom:
```bash
az login
az webapp up --name iot-backend-stefan --resource-group iot-rg \
  --runtime "PYTHON:3.11" --sku F1 --location westeurope
```

Logy pri ladení: `az webapp log tail --name iot-backend-stefan --resource-group iot-rg`

---

## 6. Overenie (po nasadení)

- [ ] `/` zobrazí kalkulačku (Frontend A)
- [ ] `/vypocet?cislo1=10&cislo2=5&operacia=plus` → JSON s `"vysledok": 15`
- [ ] `/klient` sa obnovuje každých 5 s
- [ ] `/api/prevod?hodnota=25&typ=c_to_f` → `77.0 °F`
- [ ] `/api/prevod?hodnota=1013&typ=hpa_to_mmhg` → ~`759.81 mmHg`
- [ ] `/api/prevod?hodnota=10&typ=ms_to_kmh` → `36.0 km/h`
- [ ] `/api/historia-prevodov` vráti zoznam všetkých prevodov
- [ ] Frontend B zobrazí tabuľku prevodov
- [ ] GET parametre sú viditeľné v URL

---

## 7. Časté problémy

| Problém | Fix |
|---|---|
| `Application Error` po deploy | Over Startup Command a či je `app.py` v **koreni** ZIPu. Pozri `az webapp log tail`. |
| `ModuleNotFoundError` | Chýba závislosť v `requirements.txt` → doplň a redeployuj. |
| CORS chyba v konzole | Over `CORS(app)` v `app.py` (už tam je). Over, že `flask-cors` je v `requirements.txt`. |
| ESP32 nevie pripojiť cez HTTPS | HTTPS Only = Off. |
| `databaza.db` / `prevody.json` sa po reštarte stratia | Free tier má efemérny disk — pre školu to stačí. Pre produkciu: Azure Blob Storage / Azure SQL. |

---

## 8. Kľúčové URL

- Repo: <https://github.com/SamuelStefan01/simple-iot-web-app/>
- Azure portál: <https://portal.azure.com>
- Azure for Students ($100 bez karty): <https://azure.microsoft.com/free/students>

---

*Zdroje analýzy: `app.py`, `templates/frontend_a.html`, `templates/frontend_b.html`, `requirements.txt`, `startup.sh`, `zadanie_na_doma.py`, `zadanie_na_Azure.py`, `IoT_Materialy_Komplet.docx`, `Azure_Nasadenie_Detail.docx`.*
