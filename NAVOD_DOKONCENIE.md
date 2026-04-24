# Návod: Ako dokončiť IoT zadanie — krok po kroku

> Určené pre začiatočníkov. Čítaj pomaly, rob každý krok po poriadku.

---

## Čo už máš hotové

Kód je kompletný. V tvojom projekte sú tieto súbory:

```
simple-iot-web-app/
├── app.py                  ← Flask backend (hotový)
├── requirements.txt        ← zoznam knižníc (hotový)
├── startup.sh              ← spúšťač pre Azure (hotový)
└── templates/
    ├── frontend_a.html     ← admin panel (hotový)
    └── frontend_b.html     ← IoT dashboard (hotový)
```

**Zostáva ti urobiť:**
1. Spustiť projekt lokálne a otestovať ho
2. Nahrať projekt na GitHub
3. Nasadiť na Azure
4. Skontrolovať, že všetko funguje online

---

## KROK 1 — Spusti projekt na svojom počítači

### 1.1 Otvor terminál v priečinku projektu

V prieskumníkovi (File Explorer) prejdi do priečinka `simple-iot-web-app`.
Klikni do adresného riadka, napíš `cmd` a stlač Enter.

Prípadne v VS Code: `Terminal → New Terminal`.

### 1.2 Vytvor virtuálne prostredie (robíš to raz)

```bash
python -m venv .venv
```

### 1.3 Aktivuj virtuálne prostredie

```bash
.venv\Scripts\activate
```

Po aktivácii uvidíš pred príkazovým riadkom `(.venv)`.

### 1.4 Nainštaluj knižnice

```bash
pip install -r requirements.txt
```

Stiahne sa Flask, flask-cors a gunicorn. Stačí počkať.

### 1.5 Spusti server

```bash
python app.py
```

Mali by si vidieť:

```
IoT Backend Server bezi!
Frontend A (Admin):  http://localhost:5000/
Frontend B (Klient): http://localhost:5000/klient
...
```

---

## KROK 2 — Otestuj, že všetko funguje

Otvor prehliadač a vyskúšaj tieto adresy jednu po druhej:

| Čo testuješ | URL |
|-------------|-----|
| Frontend A (admin panel) | http://localhost:5000/ |
| Frontend B (dashboard) | http://localhost:5000/klient |
| Kalkulačka (10+5) | http://localhost:5000/vypocet?cislo1=10&cislo2=5&operacia=plus |
| Prevod teploty | http://localhost:5000/api/prevod?hodnota=25&typ=c_to_f |
| Prevod tlaku | http://localhost:5000/api/prevod?hodnota=1013&typ=hpa_to_mmhg |
| Prevod vetra | http://localhost:5000/api/prevod?hodnota=10&typ=ms_to_kmh |
| História prevodov | http://localhost:5000/api/historia-prevodov |

**Čo očakávať:**
- Kalkulačka → `{"vysledok": 15, ...}`
- Prevod teploty → `{"popis": "25.0 C = 77.00 F", ...}`
- História prevodov → zoznam `[...]` (po niekoľkých testoch)

Ak vidíš JSON odpovede, všetko funguje správne. ✅

---

## KROK 3 — Nahraj projekt na GitHub

> Ak si už projekt na GitHube má (vidíš ho na github.com), tento krok preskočíš.

### 3.1 Inicializuj git (ak ešte nie je)

```bash
git init
git add .
git commit -m "IoT projekt - dokoncenie zadania"
```

### 3.2 Vytvor repozitár na GitHub.com

1. Choď na https://github.com → klikni **New repository**
2. Názov: `simple-iot-web-app`
3. Nechaj verejný (Public)
4. Neklikaj na "Initialize with README"
5. Klikni **Create repository**

### 3.3 Prepoj a nahraj

```bash
git remote add origin https://github.com/TVOJE_MENO/simple-iot-web-app.git
git branch -M main
git push -u origin main
```

*(zmeň `TVOJE_MENO` za svoje GitHub meno)*

---

## KROK 4 — Vytvor Azure Web App

> Potrebuješ Azure for Students účet (zadarmo, $100 kredit bez karty).
> Registrácia: https://azure.microsoft.com/free/students

### 4.1 Prihlás sa na Azure Portal

Choď na https://portal.azure.com a prihlás sa svojím školským emailom.

### 4.2 Vytvor novú Web App

1. Klikni na **Create a resource** (zelené plus hore vľavo)
2. Hľadaj `Web App` → klikni **Create**
3. Vyplň formulár:

| Pole | Hodnota |
|------|---------|
| Subscription | Azure for Students |
| Resource Group | Klikni **Create new** → napíš `iot-rg` |
| Name | `iot-backend-stefan` *(musí byť unikátne — pridaj svoje meno)* |
| Publish | **Code** |
| Runtime stack | **Python 3.11** |
| Operating System | **Linux** |
| Region | **West Europe** |
| Pricing plan | **Free F1** |

4. Klikni **Review + create** → **Create**
5. Počkaj ~1-2 minúty, kým sa vytvorí

---

## KROK 5 — Nastav spúšťač (Startup Command)

1. V Azure portáli nájdi svoju Web App (hľadaj podľa názvu)
2. V ľavom menu klikni na **Settings → Configuration**
3. Klikni na záložku **General settings**
4. Nájdi pole **Startup Command** a zadaj:

```
gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app
```

5. Pod tým nájdi **HTTPS Only** → prepni na **Off**
   *(nutné kvôli ESP32 senzoru)*
6. Klikni **Save** → potvrď **Continue**
7. Klikni **Overview** → **Restart**

---

## KROK 6 — Nasaď projekt na Azure (ZIP Deploy)

### 6.1 Priprav ZIP archív

Označ a skomprimuj tieto súbory/priečinky:
```
app.py
requirements.txt
startup.sh
templates/   (celý priečinok)
```

> ⚠️ **Dôležité:** Súbory musia byť priamo v ZIP archíve, NIE v podpriečinku!
> Teda vo vnútri ZIP vidíš `app.py`, nie `simple-iot-web-app/app.py`.

**Ako správne zazipovať vo Windows:**
- Otvor priečinok projektu
- Označ `app.py`, `requirements.txt`, `startup.sh` a priečinok `templates`
- Klikni pravým tlačidlom → **Compress to ZIP file**

### 6.2 Nahraj ZIP cez Kudu

1. V Azure portáli otvor svoju Web App
2. V ľavom menu hľadaj **Development Tools → Advanced Tools**
3. Klikni **Go →** (otvorí sa nová záložka — Kudu konzola)
4. V Kudu klikni hore na **Tools → Zip Push Deploy**
5. Pretiahni svoj ZIP súbor do okna (drag & drop)
6. Počkaj ~1-2 minúty — uvidíš hlásenie o úspešnom nasadení

---

## KROK 7 — Skontroluj, že Azure funguje

Otvor svoju Azure URL (napr. `  `) a otestuj:

| Čo testuješ | URL |
|-------------|-----|
| Frontend A | https://iot-backend-stefan.azurewebsites.net/ |
| Frontend B | https://iot-backend-stefan.azurewebsites.net/klient |
| Prevod teploty | https://iot-backend-stefan.azurewebsites.net/api/prevod?hodnota=25&typ=c_to_f |
| História prevodov | https://iot-backend-stefan.azurewebsites.net/api/historia-prevodov |

Ak všetko funguje — **zadanie je splnené!** 🎉

---

## Časté problémy

### „Application Error" po nasadení

**Príčina:** Chybný Startup Command alebo zlá štruktúra ZIP.

**Riešenie:**
1. Over, že Startup Command je presne: `gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app`
2. Over, že v ZIP je `app.py` priamo, nie v podpriečinku
3. Skontroluj logy: Azure Portal → Web App → **Monitoring → Log stream**

### Stránka sa načítava, ale bez dát / chyba CORS

**Príčina:** CORS nie je povolený alebo frontend_b.html sa nemôže pripojiť.

**Riešenie:**
- `app.py` má `CORS(app)` — to je správne
- `flask-cors==5.0.1` je v `requirements.txt` — to je správne
- Skús stránku znova načítať (Ctrl+F5)

### Prevody sa ukladajú, ale po reštarte zmiznú

**Príčina:** Azure Free tier má dočasný disk — `prevody.json` sa po reštarte stratí.

**Toto je normálne pre školský projekt.** Pre produkciu by sa použil Azure Blob Storage.

### „ModuleNotFoundError: No module named flask"

**Príčina:** `requirements.txt` nebol správne nahraný alebo nasadenie zlyhalo.

**Riešenie:** Znova nasaď ZIP, over že `requirements.txt` je v koreni archívu.

---

## Zhrnutie — kontrolný zoznam pred odovzdaním

- [ ] Lokálne: `python app.py` beží bez chýb
- [ ] Lokálne: `http://localhost:5000/api/prevod?hodnota=25&typ=c_to_f` vracia JSON
- [ ] Lokálne: Frontend B zobrazuje tabuľku prevodov
- [ ] Azure: Web App vytvorená s Python 3.11 a Free F1 plánom
- [ ] Azure: Startup Command nastavený
- [ ] Azure: HTTPS Only = Off
- [ ] Azure: ZIP Deploy úspešný
- [ ] Azure: `https://tvoj-backend.azurewebsites.net/` zobrazí Frontend A
- [ ] Azure: `https://tvoj-backend.azurewebsites.net/api/prevod?hodnota=10&typ=ms_to_kmh` vracia JSON
- [ ] Azure: Frontend B zobrazuje tabuľku prevodov

---

*Ak niečo nefunguje, pozri sekciu „Časté problémy" alebo skontroluj logy v Azure portáli.*
