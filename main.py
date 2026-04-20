import json
import ollama
import chromadb
from pydantic import BaseModel
from typing import List

# --- 1. MODELE DANYCH (Nasz Strażnik) ---
class Metadane(BaseModel):
    id_sprawy: str
    kategoria: str
    data_wplywu: str

class StanFaktyczny(BaseModel):
    wnioskodawca: str
    dochod_miesieczny_rodziny: float
    liczba_czlonkow_rodziny: int
    dochod_na_osobe: float

class ProcesRozumowania(BaseModel):
    prog_dochodowy_ustawowy: float
    przekroczenie_progu: bool
    kwota_przekroczenia: float
    decyzja_algorytmu: str

class Sprawa(BaseModel):
    metadane: Metadane
    stan_faktyczny: StanFaktyczny
    proces_rozumowania: ProcesRozumowania
    podstawy_prawne: List[str]


# --- 2. FUNKCJE POMOCNICZE ---
def zaladuj_dane(sciezka: str) -> Sprawa:
    with open(sciezka, "r", encoding="utf-8") as plik:
        return Sprawa(**json.load(plik))

def znajdz_przepisy(kategoria: str) -> str:
    print("📚 Przeszukuję bazę prawną (ChromaDB)...")
    # Łączymy się z naszą wczorajszą bazą
    klient = chromadb.PersistentClient(path="./moje_ustawy")
    kolekcja = klient.get_collection(name="przepisy_prawne")
    
    # Szukamy przepisu pasującego do kategorii (np. "stypendium socjalne")
    wyniki = kolekcja.query(
        query_texts=[kategoria.replace("_", " ")],
        n_results=1 # Chcemy tylko 1 najbardziej trafny przepis
    )
    
    znaleziony_przepis = wyniki['documents'][0][0]
    print(f"⚖️ Znaleziono pasujący przepis: {znaleziony_przepis[:60]}...")
    return znaleziony_przepis


# --- 3. INŻYNIERIA PROMPTU (RAG + LLM) ---
def zaladuj_szablon(kategoria: str) -> str:
    # Pobieramy szablony promptów z pliku
    with open("prompty.json", "r", encoding="utf-8") as plik:
        prompty = json.load(plik)
    
    # Jeśli mamy specjalny prompt dla tej kategorii, używamy go.
    # W przeciwnym razie bierzemy styl "domyslny".
    return prompty.get(kategoria, prompty["domyslny"])

def generuj_decyzje(sprawa: Sprawa, przepis: str):
    print("⏳ AI dobiera styl i generuje uzasadnienie...")
    
    # 1. Pobieramy styl ("osobowość" modelu) dla tej konkretnej sprawy
    styl_systemowy = zaladuj_szablon(sprawa.metadane.kategoria)
    
    # 2. Składamy to z naszymi twardymi faktami (RAG)
    prompt_koncowy = f"""
    {styl_systemowy}
    
    SPRAWA: {sprawa.metadane.kategoria.replace('_', ' ')}.
    
    FAKTY:
    - Wnioskodawca: {sprawa.stan_faktyczny.wnioskodawca}
    - Dochód rodziny: {sprawa.stan_faktyczny.dochod_miesieczny_rodziny} zł
    - Liczba osób: {sprawa.stan_faktyczny.liczba_czlonkow_rodziny}
    - Dochód na osobę: {sprawa.stan_faktyczny.dochod_na_osobe} zł
    - Ustawowy próg: {sprawa.proces_rozumowania.prog_dochodowy_ustawowy} zł
    - Decyzja: {sprawa.proces_rozumowania.decyzja_algorytmu.upper()}
    
    PODSTAWA PRAWNA:
    "{przepis}"
    
    Napisz uzasadnienie teraz, opierając się TYLKO na powyższych danych:
    """

    odpowiedz = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt_koncowy}])
    return odpowiedz['message']['content']

# --- 4. GŁÓWNA LOGIKA ---
if __name__ == "__main__":
    try:
        # KROK A: Pobieramy i walidujemy JSON
        sprawa = zaladuj_dane("sprawa_01_stypendium.json")
        
        # KROK B: System RAG sam szuka prawa dla tej konkretnej sprawy!
        przepis_prawny = znajdz_przepisy(sprawa.metadane.kategoria)
        
        # KROK C: Wysyłamy fakty + prawo do AI
        gotowy_dokument = generuj_decyzje(sprawa, przepis_prawny)
        
        print("\n================ DOKUMENT URZĘDOWY ================\n")
        print(gotowy_dokument)
        print("\n===================================================\n")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")