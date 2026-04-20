import json
import chromadb

def synchronizuj_baze():
    print("🔌 Łączenie z bazą wektorową ChromaDB...")
    klient = chromadb.PersistentClient(path="./moje_ustawy")
    kolekcja = klient.get_or_create_collection(name="przepisy_prawne")
    
    print("📖 Czytanie bazy prawnej z pliku ustawy.json...")
    with open("ustawy.json", "r", encoding="utf-8") as plik:
        ustawy_z_pliku = json.load(plik)
        
    # 1. Przygotowujemy listy z JSONa
    id_w_pliku = [ustawa["id"] for ustawa in ustawy_z_pliku]
    teksty_w_pliku = [ustawa["tekst"] for ustawa in ustawy_z_pliku]
    
    # 2. Pobieramy to, co aktualnie siedzi w bazie wektorowej
    dane_w_bazie = kolekcja.get()
    id_w_bazie = dane_w_bazie['ids']

    metadane_w_pliku = [{"kategoria": u.get("kategoria", "ogolne")} for u in ustawy_z_pliku]  # Dodajemy kategorię do metadanych!
    
    # 3. KROK CZYSZCZENIA (Szukamy "duchów")
    # Zbieramy te ID, które są w bazie, ale nie ma ich już w naszym pliku JSON
    do_usuniecia = [id_baza for id_baza in id_w_bazie if id_baza not in id_w_pliku]
    
    if do_usuniecia:
        print(f"🗑️ Wykryto usunięte przepisy. Usuwam z bazy wektorowej: {do_usuniecia}")
        kolekcja.delete(ids=do_usuniecia)
    
    # 4. AKTUALIZACJA I DODAWANIE (Upsert)
    print("📥 Aktualizuję bazę (tekst + kategorie)...")
    kolekcja.upsert(
        documents=teksty_w_pliku,
        ids=id_w_pliku,
        metadatas=metadane_w_pliku  # Tu dodajemy kategorie do bazy!
    )
    
    print(f"✅ Baza zsynchronizowana idealnie! Obecna liczba przepisów: {kolekcja.count()}")

if __name__ == "__main__":
    synchronizuj_baze()