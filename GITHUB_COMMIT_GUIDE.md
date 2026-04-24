# GitHub Commit Guide — IoT Meteorologická Stanica

> Praktický návod ako správne verzovať projekt pomocou Git a GitHub.

---

## 1. Prvé nastavenie (raz za počítač)

```bash
git config --global user.name "Tvoje Meno"
git config --global user.email "tvoj@email.com"
```

---

## 2. Inicializácia projektu (raz za projekt)

```bash
# Prejdi do priečinka projektu
cd "TUKE Programovanie/IoT/simple-iot-web-app"

# Inicializuj Git repozitár
git init

# Pridaj vzdialený repozitár (GitHub)
git remote add origin https://github.com/tvoje-meno/simple-iot-web-app.git

# Overenie
git remote -v
```

---

## 3. Základný workflow (každý deň)

```
Pracuješ na kóde
      ↓
git status        ← čo sa zmenilo?
      ↓
git add .         ← pridaj zmeny do "staging area"
      ↓
git commit -m "popis zmeny"   ← ulož snapshot
      ↓
git push          ← nahraj na GitHub
```

### Konkrétne príkazy:

```bash
# 1. Skontroluj stav — čo je zmenené
git status

# 2. Pridaj VŠETKY zmeny
git add .

# alebo len konkrétny súbor
git add templates/frontend_a.html

# 3. Vytvor commit
git commit -m "feat: pridany novy dizajn frontend A a B"

# 4. Nahraj na GitHub
git push origin main
```

---

## 4. Ako písať dobré commit správy

### Formát:
```
<typ>: <krátky popis>  (max ~72 znakov)
```

### Typy commitov:

| Typ | Použitie | Príklad |
|-----|----------|---------|
| `feat` | nová funkcia | `feat: pridany prevodnik jednotiek` |
| `fix` | oprava chyby | `fix: opravene delenie nulou` |
| `style` | zmena dizajnu/CSS | `style: prepísaný frontend na moderný dizajn` |
| `refactor` | preorganizovanie kódu | `refactor: rozdelenie logiky do funkcii` |
| `docs` | dokumentácia | `docs: pridany README a commit guide` |
| `chore` | konfigurácia, nastavenia | `chore: pridany requirements.txt` |
| `deploy` | nasadenie | `deploy: konfiguracia pre Azure` |

### Príklady pre tvoj projekt:
```bash
git commit -m "feat: pridana historia prevodov do frontend B"
git commit -m "fix: opravene CORS nastavenia pre Azure"
git commit -m "style: novy glassmorphism dizajn frontend A a B"
git commit -m "chore: aktualizovany requirements.txt"
git commit -m "deploy: pridany startup.sh pre gunicorn na Azure"
```

---

## 5. Zobrazenie histórie

```bash
# Zoznam commitov
git log

# Prehľadnejší výpis
git log --oneline

# Graficky (vetvy)
git log --oneline --graph --all
```

**Príklad výstupu `git log --oneline`:**
```
a3f2c1e style: novy dizajn frontend A a B
9b1d4f2 feat: pridany prevodnik meteorologickych jednotiek
3e8a7c0 feat: SQLite historia vypoctov
1f2b9d1 init: zakladna Flask aplikacia
```

---

## 6. Vrátenie zmien

```bash
# Zahodenie NEULOŽENÝCH zmien v súbore
git checkout -- app.py

# Vrátenie z "staging area" (po git add, pred commit)
git reset HEAD app.py

# Vrátenie posledného commitu (zachová zmeny v súboroch)
git reset --soft HEAD~1

# Zobrazenie rozdielu pred commitom
git diff
```

---

## 7. Vetvy (branches)

```bash
# Vytvor novú vetvu
git checkout -b feature/nove-senzory

# Prepni sa späť na main
git checkout main

# Zoznam vetiev
git branch

# Zlúč vetvu do main
git merge feature/nove-senzory

# Zmaž vetvu
git branch -d feature/nove-senzory
```

---

## 8. .gitignore — čo NEnahrávaš na GitHub

Vytvor súbor `.gitignore` v koreňovom priečinku:

```
# Python
__pycache__/
*.pyc
*.pyo
.env
venv/
.venv/

# Databáza (obsahuje dáta, nie kód)
databaza.db

# Lokálne nastavenia
*.log
.DS_Store

# Azure
*.zip
```

```bash
# Pridaj .gitignore a commit
git add .gitignore
git commit -m "chore: pridany .gitignore"
```

---

## 9. Prvý push na GitHub

```bash
# Nastav hlavnú vetvu a pushni
git push -u origin main

# Každý ďalší push stačí
git push
```

Ak GitHub vyžaduje token (od 2021 neakceptuje heslo):
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic) → zaškrtni `repo`
3. Token použi namiesto hesla pri `git push`

---

## 10. Stiahnutie zmien (keď pracuješ na viacerých počítačoch)

```bash
# Stiahni najnovšie zmeny z GitHubu
git pull

# alebo
git pull origin main
```

---

## 11. Rýchly cheatsheet

```bash
git status                    # čo sa zmenilo?
git add .                     # pridaj všetko
git add nazov_suboru.py       # pridaj konkrétny súbor
git commit -m "popis"         # ulož zmenu
git push                      # nahraj na GitHub
git pull                      # stiahni z GitHubu
git log --oneline             # história commitov
git diff                      # čo sa zmenilo v kóde
git checkout -- subor.py      # zahoď zmeny v súbore
```

---

## 12. Odporúčaný postup pre tvoj IoT projekt

```bash
# 1. Na začiatku práce
git pull

# 2. Pracuješ... upravuješ app.py, templates, atď.

# 3. Po dokončení funkcie/opravy
git status
git add .
git commit -m "feat: popis co si spravil"
git push

# Commit robíš minimálne:
#   - po každej novej funkčnosti
#   - po oprave chyby
#   - pred odchodom od počítača
#   - pred nasadením na Azure
```

---

*Tip: Commit správy sú ako komentáre — píš ich pre seba z budúcnosti 🙂*
