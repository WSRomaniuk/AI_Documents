import json
import ollama
import chromadb
from pydantic import BaseModel
from typing import List, Dict, Any

# --- MODELE Pydantic (Dynamiczne) ---
class Metadane(BaseModel):
    id_sprawy: str
    kategoria: str
    data_wplywu: str

class Sprawa(BaseModel):
    metadane: Metadane
    # Używamy Dict, żeby przyjmować DOWOLNE dane dla różnych spraw!
    stan_faktyczny: Dict[str, Any]  
    proces_rozumowania: Dict[str, Any]
    podstawy_prawne: List[str]

# --- FUNKCJE LOGICZNE ---
def waliduj_dane(surowe_dane: dict) -> Sprawa:
    return Sprawa(**surowe_dane)

def znajdz_przepisy(kategoria: str) -> str:
    klient = chromadb.PersistentClient(path="./moje_ustawy")
    kolekcja = klient.get_collection(name="przepisy_prawne")
    
    wyniki = kolekcja.query(
        query_texts=[kategoria.replace("_", " ")],
        n_results=1,
        where={"kategoria": kategoria} 
    )
    
    if wyniki['documents'] and wyniki['documents'][0]:
        return wyniki['documents'][0][0]
    
    return "Brak pasujących przepisów dla tej konkretnej kategorii."


def wytypuj_styl_llm(kategoria: str) -> str:
    """LLM Router: AI samo decyduje, jakiego szablonu użyć na podstawie nazwy kategorii."""
    prompt_routera = f"""
    Jesteś systemem kategoryzującym w urzędzie. Twoim zadaniem jest przypisać podaną sprawę do jednego z trzech działów.
    
    Dostępne działy:
    1. socjalne (zasiłki, stypendia, zapomogi, pomoc, opieka, trudna sytuacja)
    2. budowlane (pozwolenia, budowa, rozbiórka, nadzór, inwestycje, architektura)
    3. domyslne (wszystkie inne sprawy administracyjne, KPA, ogólne)
    
    Kategoria sprawy do oceny: "{kategoria}"
    
    ZWRÓĆ TYLKO I WYŁĄCZNIE JEDNO SŁOWO (socjalne, budowlane lub domyslne). Nie pisz żadnych innych znaków ani wyjaśnień.
    """
    
    odpowiedz = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt_routera}])
    wynik = odpowiedz['message']['content'].strip().lower()
    
    # Zabezpieczenie: jeśli AI zacznie halucynować i odpisze całym zdaniem, wymuszamy "domyslne"
    if "socjalne" in wynik: return "socjalne"
    elif "budowlane" in wynik: return "budowlane"
    else: return "domyslne"

def zaladuj_szablon(kategoria: str) -> str:
    """Pobiera szablon promptu używając decyzji podjętej przez LLM Router."""
    # 1. Pytamy sztuczną inteligencję o wybór stylu
    klucz_promptu = wytypuj_styl_llm(kategoria)
    print(f" Recepcjonista AI zdecydował: kategoria '{kategoria}' -> styl '{klucz_promptu}'")
    
    # 2. Ładujemy odpowiedni tekst z pliku
    try:
        with open("prompty.json", "r", encoding="utf-8") as plik:
            prompty = json.load(plik)
        return prompty.get(klucz_promptu, "Jesteś urzędnikiem. Napisz uzasadnienie.")
    except FileNotFoundError:
        return "Jesteś urzędnikiem. Napisz uzasadnienie."

def generuj_decyzje_llm_stream(sprawa: Sprawa, przepis: str, edytowany_prompt: str):
    # MAGIA DYNAMIKI: Zamieniamy słowniki na ładny tekst, niezależnie co tam jest!
    fakty_str = "\n".join([f"- {k.replace('_', ' ').capitalize()}: {v}" for k, v in sprawa.stan_faktyczny.items()])
    rozumowanie_str = "\n".join([f"- {k.replace('_', ' ').capitalize()}: {v}" for k, v in sprawa.proces_rozumowania.items()])

    prompt_koncowy = f"""
    {edytowany_prompt}
    
    FAKTY W SPRAWIE:
    {fakty_str}
    
    PROCES DECYZYJNY ALGORYTMU:
    {rozumowanie_str}
    
    PODSTAWA PRAWNA DO ZACYTOWANIA:
    "{przepis}"
    
    Pisz tylko na podstawie tych faktów!
    """
    
    strumien = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt_koncowy}], stream=True)
    for chunk in strumien:
        yield chunk['message']['content']