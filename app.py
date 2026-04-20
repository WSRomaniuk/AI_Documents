import streamlit as st
import json
import os
from datetime import datetime
import backend

st.set_page_config(page_title="Moduł XAI", layout="wide")

# --- BAZA HISTORII ---
PLIK_HISTORII = "historia_wersji.json"

def zaladuj_historie():
    if os.path.exists(PLIK_HISTORII):
        with open(PLIK_HISTORII, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def zapisz_wersje(tekst, uzytkownik, kategoria, id_sprawy):
    historia = zaladuj_historie()
    nowy_wpis = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uzytkownik": uzytkownik,
        "kategoria": kategoria,
        "id_sprawy": id_sprawy,
        "dokument": tekst
    }
    historia.append(nowy_wpis)
    with open(PLIK_HISTORII, "w", encoding="utf-8") as f:
        json.dump(historia, f, ensure_ascii=False, indent=4)
    st.success("✅ Wersja została pomyślnie zapisana!")

def przywroc_wersje(tekst):
    # Ta funkcja wykona się ZANIM strona się odświeży
    st.session_state['czy_wygenerowano'] = True
    st.session_state['klucz_edytora'] = tekst

# --- INTERFEJS GŁÓWNY ---
st.title("Moduł XAI - Generowanie Uzasadnień")

with st.sidebar:
    st.header("📂 Wgraj sprawę")
    plik_json = st.file_uploader("Wybierz plik JSON ze sprawą", type=["json"])

if plik_json is not None:
    # 1. ŁADOWANIE
    try:
        surowe_dane = json.load(plik_json)
        sprawa = backend.waliduj_dane(surowe_dane)
    except Exception as e:
        st.error(f"❌ Błąd w pliku JSON: {e}")
        st.stop()

    # 2. PRZYGOTOWANIE
    st.success(f"Rozpoznano sprawę: {sprawa.metadane.id_sprawy}")
    przepis = backend.znajdz_przepisy(sprawa.metadane.kategoria)
    domyslny_prompt = backend.zaladuj_szablon(sprawa.metadane.kategoria)

    # 3. KOLUMNY
    kolumna_lewa, kolumna_prawa = st.columns([1, 1])

    with kolumna_lewa:
        st.subheader("Podstawa Prawna")
        st.info(przepis)
        
        st.subheader("Szablon Promptu")
        edytowany_prompt = st.text_area("Instrukcja dla modelu:", value=domyslny_prompt, height=200)
        
        if st.button("Generuj Uzasadnienie", type="primary"):
            # Zamieniamy spinner na zwykłe info, bo tekst będzie leciał na żywo!
            st.info("Sztuczna Inteligencja generuje dokument na żywo...")
            
            # 1. Pobieramy "strumień" (generator) z naszego modelu
            strumien_slow = backend.generuj_decyzje_llm_stream(sprawa, przepis, edytowany_prompt)
            
            # 2. st.write_stream WYPISUJE tekst na żywo i zwraca połączony, ZWYKŁY TEKST (string)
            pelen_tekst_string = st.write_stream(strumien_slow)
            
            # 3. Zapisujemy do pamięci bezpieczny string, a nie generator!
            st.session_state['czy_wygenerowano'] = True
            st.session_state['klucz_edytora'] = pelen_tekst_string
            
            # 4. Odświeżamy stronę, żeby tekst sam wskoczył do prawego okienka
            st.rerun()

    with kolumna_prawa:
        st.subheader("Edytor Dokumentu")
        
        if st.session_state.get('czy_wygenerowano', False):
            # MAGIA: Używamy tylko parametru 'key'. Edytor jest teraz twardo podpięty pod pamięć!
            tekst_do_edycji = st.text_area("Popraw błędy przed zapisaniem:", height=350, key="klucz_edytora")
            
            st.divider()
            urzednik = st.text_input("Identyfikator urzędnika:", "Urzednik_Jan")
            if st.button("Zapisz wersję do bazy"):
                zapisz_wersje(tekst_do_edycji, urzednik, sprawa.metadane.kategoria, sprawa.metadane.id_sprawy)
        else:
            st.warning("Kliknij 'Generuj', aby zobaczyć tekst.")

else:
    st.info("Wgraj plik JSON ze sprawą w menu bocznym.")

# --- 4. HISTORIA WERSJI ---
st.divider()
st.header("Historia zapisanych wersji")
historia = zaladuj_historie()

if historia:
    for i, wpis in enumerate(reversed(historia)):
        with st.expander(f"Sprawa: {wpis['id_sprawy']} | {wpis['data']} | {wpis['uzytkownik']}"):
            st.info(wpis['dokument'])
            
            # NAPRAWA COFANIA WERSJI
            # Używamy on_click (Callback), żeby ominąć błąd Streamlita
            st.button(
                "⏪ Wczytaj tę wersję do edytora", 
                key=f"btn_przywroc_{i}",
                on_click=przywroc_wersje,
                args=(wpis['dokument'],) # Przekazujemy tekst do funkcji
            )
else:
    st.write("Brak zapisów w historii.")