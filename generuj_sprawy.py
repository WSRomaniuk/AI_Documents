import json
import os

sprawy = [
    # --- BLOK SOCJALNY ---
    {"id_sprawy": "SOC/01", "kategoria": "zasilek_celowy", "stan": {"wnioskodawca": "Jan Kowalski", "cel": "zakup opału na zimę", "sytuacja": "pozar domu", "dochod": 1200}, "rozumowanie": {"kwalifikacja": True, "kwota_przyznana": 1500, "decyzja": "pozytywna"}},
    {"id_sprawy": "SOC/02", "kategoria": "zasilek_staly", "stan": {"wnioskodawca": "Anna Nowak", "wiek": 68, "zdolnosc_do_pracy": "calkowita niezdolnosc", "dochod": 400}, "rozumowanie": {"kryterium_wiekowe": True, "kryterium_dochodowe": True, "decyzja": "pozytywna"}},
    {"id_sprawy": "SOC/03", "kategoria": "stypendium_socjalne", "stan": {"wnioskodawca": "Piotr Wisniewski", "uczelnia": "Politechnika", "dochod_na_osobe": 1800}, "rozumowanie": {"prog_dochodowy": 1300, "przekroczenie": True, "decyzja": "negatywna"}},
    {"id_sprawy": "SOC/04", "kategoria": "stypendium_niepelnosprawni", "stan": {"wnioskodawca": "Ewa Lis", "stopien_niepelnosprawnosci": "umiarkowany", "dochod": 5000}, "rozumowanie": {"waznosc_orzeczenia": True, "zaleznosc_od_dochodu": False, "decyzja": "pozytywna"}},
    {"id_sprawy": "SOC/05", "kategoria": "zasilek_okresowy", "stan": {"wnioskodawca": "Krzysztof Maj", "powod": "dlugotrwale bezrobocie", "czas_bez_pracy": "14 miesiecy"}, "rozumowanie": {"wymogi_ustawowe": True, "okres_wyplaty": "6 miesiecy", "decyzja": "pozytywna"}},
    # --- BLOK BUDOWLANY ---
    {"id_sprawy": "BUD/01", "kategoria": "pozwolenie_na_budowe", "stan": {"inwestor": "Developer S.A.", "obiekt": "biurowiec", "mpzp": "zgodne"}, "rozumowanie": {"kompletnosc_wniosku": True, "ocena_techniczna": "pozytywna", "decyzja": "pozytywna"}},
    {"id_sprawy": "BUD/02", "kategoria": "rozbiorka_obiektu", "stan": {"inwestor": "Gmina Miejska", "obiekt": "stara stodola", "wysokosc": "6 metrow", "zabytek": False}, "rozumowanie": {"wymog_pozwolenia": False, "wystarczy_zgloszenie": True, "decyzja": "umorzenie_postepowania"}},
    {"id_sprawy": "BUD/03", "kategoria": "zmiana_uzytkowania", "stan": {"inwestor": "Janina Kowalczyk", "stan_obecny": "mieszkanie", "stan_planowany": "przedszkole", "warunki_pozarowe": "brak dostosowania"}, "rozumowanie": {"zgodnosc_BHP": False, "ryzyko": "wysokie", "decyzja": "negatywna"}},
    {"id_sprawy": "BUD/04", "kategoria": "samowola_budowlana", "stan": {"wlasciciel": "Michal Kot", "obiekt": "garaz murowany", "pozwolenie": "brak"}, "rozumowanie": {"stan_faktyczny": "potwierdzony", "mozliwosc_legalizacji": False, "decyzja": "nakaz_rozbiorki"}},
    # --- BLOK DOMYSLNY ---
    {"id_sprawy": "ADM/01", "kategoria": "wymeldowanie", "stan": {"strona": "Tomasz Lis", "przebywanie_pod_adresem": False, "okres_nieobecnosci": "powyzej 3 lat"}, "rozumowanie": {"przeslanki_ustawowe": True, "decyzja": "wymeldowanie_z_urzedu"}}
]

for i, s in enumerate(sprawy, 1):
    dane = {
        "metadane": {"id_sprawy": s["id_sprawy"], "kategoria": s["kategoria"], "data_wplywu": "2026-05-15"},
        "stan_faktyczny": s["stan"],
        "proces_rozumowania": s["rozumowanie"],
        "podstawy_prawne": []
    }
    with open(f"testowa_{i:02d}_{s['kategoria']}.json", "w", encoding="utf-8") as f:
        json.dump(dane, f, indent=4)

print("✅ Utworzono 10 nowych, różnorodnych plików ze sprawami!")