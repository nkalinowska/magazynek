import streamlit as st
from typing import Dict, Tuple, List, Any
import time
import math

# --- Konfiguracja Wygasania Sesji ---
CZAS_WYGASANIA_SEKCJI_SEKUNDY = 120
KLUCZ_MAGAZYNU = 'magazyn'
KLUCZ_LAST_ACTIVITY = 'last_activity'

# --- Inicjalizacja Stanu Sesji ---

def inicjalizuj_stan_sesji():
    """Inicjalizuje magazyn, czas aktywności oraz domyślne stany minimalne."""
    if KLUCZ_MAGAZYNU not in st.session_state:
        # Struktura: Klucz: (Nazwa, Lokalizacja), Wartość: Lista Partii
        st.session_state[KLUCZ_MAGAZYNU]: Dict[Tuple[str, str], List[Dict[str, float]]] = {
            ("Laptop", "Regał A01"): [
                {'ilosc': 10, 'cena': 2500.00, 'min_stock': 20}, # Min stock = 20
                {'ilosc': 5, 'cena': 2700.00, 'min_stock': 20}
            ],
            ("Monitor", "Regał A01"): [
                {'ilosc': 20, 'cena': 850.50, 'min_stock': 25} # Min stock = 25
            ],
            ("Klawiatura", "Sektor B05"): [
                {'ilosc': 50, 'cena': 150.00, 'min_stock': 40} # Min stock = 40
            ]
        }
    
    if KLUCZ_LAST_ACTIVITY not in st.session_state:
        st.session_state[KLUCZ_LAST_ACTIVITY] = time.time()

def sprawdz_wygasanie_sesji():
    """Sprawdza, czy sesja wygasła z powodu braku aktywności."""
    
    czas_teraz = time.time()
    czas_ostatniej_aktywnosci = st.session_state.get(KLUCZ_LAST_ACTIVITY, czas_teraz)
    roznica_czasu = czas_teraz - czas_ostatniej_aktywnosci
    
    if roznica_czasu > CZAS_WYGASANIA_SEKCJI_SEKUNDY:
        st.session_state[KLUCZ_MAGAZYNU] = {}
        st.session_state[KLUCZ_LAST_ACTIVITY] = czas_teraz
        st.error(f"⚠️ **Sesja Wygasła!** Brak aktywności przez ponad {CZAS_WYGASANIA_SEKCJI_SEKUNDY} sekund. Magazyn został zresetowany.")
    else:
        st.session_state[KLUCZ_LAST_ACTIVITY] = time.time() 
        czas_pozostaly = int(CZAS_WYGASANIA_SEKCJI_SEKUNDY - roznica_czasu)
        st.sidebar.info(f"Sesja wygaśnie za: **{max(0, czas_pozostaly)}** sekund.")

# --- NOWA FUNKCJA GENEROWANIA ZAPOTRZEBOWANIA (POPRWIONA) ---

def generuj_zapotrzebowanie():
    """Analizuje magazyn i generuje listę towarów wymagających domówienia (Poniżej Min Stock)."""
    
    magazyn = st.session_state[KLUCZ_MAGAZYNU]
    
    # Krok 1: Agregacja danych (suma ilości i min_stock dla unikalnych nazw)
    agregacja: Dict[str, Dict[str, Any]] = {}

    for (nazwa, _), partie in magazyn.items():
        if not partie:
            continue
            
        # Sumaryczna ilość z wszystkich partii w tej lokalizacji
        dostepna_ilosc = sum(p['ilosc'] for p in partie)
        
        # Min stock (zakładamy, że jest taki sam dla wszystkich partii/lokalizacji danego produktu)
        min_stock_partii = partie[0].get('min_stock', 0)
        
        if nazwa not in agregacja:
            agregacja[nazwa] = {'dostepna': 0, 'min_stock': min_stock_partii}
        
        # Agregacja ilości
        agregacja[nazwa]['dostepna'] += dostepna_ilosc
        
        # Jeśli znajdziemy wyższy min_stock (w przypadku błędu użytkownika), użyjemy wyższego
        if min_stock_partii > agregacja[nazwa]['min_stock']:
             agregacja[nazwa]['min_stock'] = min_stock_partii
            

    # Krok 2: Generowanie listy braków
    lista_brakow = []
    for nazwa, dane in agregacja.items():
        if dane['dostepna'] < dane['min_stock']:
            brak = dane['min_stock'] - dane['dostepna']
            lista_brakow.append({
                "Towar": nazwa,
                "Stan Obecny": dane['dostepna'],
                "Stan Minimalny": dane['min_stock'],
                "Zapotrzebowanie (Braki)": brak
            })
    
    return lista_brakow


# --- Funkcje Magazynowe (pozostały bez zmian, ale operują na min_stock) ---

def dodaj_towar_z_partia(nazwa: str, ilosc: int, lokalizacja: str, cena: float, min_stock: int):
    """Dodaje nową partię towaru z min_stock."""
    
    nazwa = nazwa.strip()
    lokalizacja = lokalizacja.strip().upper() 
    
    if not nazwa or not lokalizacja:
        st.error("Wprowadź nazwę towaru i lokalizację.")
        return

    if ilosc <= 0 or cena <= 0 or min_stock < 0:
        st.error("Ilość, cena i min stock muszą być poprawnymi wartościami.")
        return

    klucz = (nazwa, lokalizacja)
    magazyn = st.session_state[KLUCZ_MAGAZYNU]
    
    # Dodanie min_stock do partii
    nowa_partia = {'ilosc': ilosc, 'cena': round(cena, 2), 'min_stock': min_stock}
    
    if klucz not in magazyn:
        magazyn[klucz] = []
    
    magazyn[klucz].append(nowa_partia)
    
    st.success(f"Przyjęto nową partię: **{nazwa}** ({ilosc} szt. @ {cena:.2f} PLN) na pozycji **{lokalizacja}**. Min Stock ustawiono na: {min_stock}.")


def usun_towar_z_lokalizacja(klucz: Tuple[str, str], ilosc_do_usuniecia: int):
    """Usuwa podaną ilość towaru z danej lokalizacji (FIFO)."""
    
    nazwa, lokalizacja = klucz
    magazyn = st.session_state[KLUCZ_MAGAZYNU]
    
    if ilosc_do_usuniecia <= 0:
        st.error("Ilość do usunięcia musi być większa niż zero.")
        return

    if klucz not in magazyn or not magazyn[klucz]:
        st.error(f"Towar **{nazwa}** na pozycji **{lokalizacja}** nie został znaleziony w magazynie.")
        return

    dostepna_ilosc = sum(partia['ilosc'] for partia in magazyn[klucz])
    
    if ilosc_do_usuniecia > dostepna_ilosc:
        st.error(f"Nie można wydać **{ilosc_do_usuniecia}** sztuk. Dostępnych jest tylko **{dostepna_ilosc}**.")
        return

    pozostala_ilosc = ilosc_do_usuniecia
    wydane_partie_info = []

    while pozostala_ilosc > 0 and magazyn[klucz]:
        partia = magazyn[klucz][0]
        ilosc_partii = partia['ilosc']
        cena_partii = partia['cena']
        
        if ilosc_partii <= pozostala_ilosc:
            magazyn[klucz].pop(0) 
            wydane_partie_info.append(f"{ilosc_partii} szt. @ {cena_partii:.2f} PLN")
            pozostala_ilosc -= ilosc_partii
        else:
            partia['ilosc'] -= pozostala_ilosc
            wydane_partie_info.append(f"{pozostala_ilosc} szt. @ {cena_partii:.2f} PLN")
            pozostala_ilosc = 0

    st.success(f"Wydano **{ilosc_do_usuniecia}** sztuk towaru **{nazwa}** z **{lokalizacja}** na podstawie partii: " + ", ".join(wydane_partie_info))
    
    if not magazyn[klucz]:
        del magazyn[klucz]


# --- Główny Interfejs Użytkownika Streamlit ---

st.set_page_config(page_title="Magazyn: Kontrola Zapasów", layout="wide")

inicjalizuj_stan_sesji()
sprawdz_wygasanie_sesji() 

MAGAZYN = st.session_state[KLUCZ_MAGAZYNU]

st.title("🏭 Kontrola Zapasów Magazynowych (Stock Replenishment)")
st.caption(f"Dane są utrzymywane, ale resetują się po {CZAS_WYGASANIA_SEKCJI_SEKUNDY} sekundach bezczynności.")

# --- KOLUMNY DLA OSZCZĘDNOŚCI MIEJSCA PIONOWEGO ---
col_replenish, col_add_remove = st.columns([1, 1])

# ==============================================================================
# LEWA KOLUMNA: Generowanie Zapotrzebowania (Zamówienie Stockowe)
# ==============================================================================
with col_replenish:
    st.header("📈 Automatyczna Analiza Zapasów")
    st.info("Generuje listę towarów poniżej Stanu Minimalnego (Min Stock). To jest Twoja lista zakupów/domówień.")

    lista_brakow = generuj_zapotrzebowanie()

    if lista_brakow:
        st.subheader("⚠️ Wymagane Domy (Zapotrzebowanie):")
        
        # Znalezienie maksymalnej wartości Min Stock dla poprawnej wizualizacji paska
        max_min_stock = max(item['Stan Minimalny'] for item in lista_brakow) if lista_brakow else 1
        
        df_braki = st.dataframe(
            lista_brakow, 
            hide_index=True,
            use_container_width=True,
            column_config={
                "Stan Obecny": st.column_config.ProgressColumn(
                    "Stan Obecny",
                    format="%f szt.",
                    min_value=0,
                    # Używamy max_min_stock, aby pasek wypełniał się do poziomu minimalnego
                    max_value=max_min_stock 
                )
            }
        )
        st.error(f"Znaleziono **{len(lista_brakow)}** pozycje poniżej minimum!")
    else:
        st.success("Wszystkie towary utrzymują stan minimalny lub powyżej. Brak zapotrzebowania na ten moment.")

# ==============================================================================
# PRAWA KOLUMNA: Operacje Magazynowe (Dodaj / Usuń)
# ==============================================================================
with col_add_remove:
    
    st.header("➕ Przyjęcie Towaru i Definicja Min Stock")
    with st.form(key='dodawanie_form'):
        
        # Wiersz 1
        c1, c2 = st.columns(2)
        with c1:
            nowy_towar = st.text_input("Nazwa Towaru:", key="input_dodaj")
        with c2:
            lokalizacja_dodaj = st.text_input("Lokalizacja:", key="lokalizacja_dodaj")

        # Wiersz 2
        c3, c4, c5 = st.columns(3)
        with c3:
            ilosc_dodaj = st.number_input("Ilość sztuk:", min_value=1, value=1, step=1, key="ilosc_dodaj")
        with c4:
            cena_dodaj = st.number_input("Cena jedn. (PLN):", min_value=0.01, value=100.00, step=0.01, key="cena_dodaj", format="%.2f")
        with c5:
            min_stock_dodaj = st.number_input("Stan Minimalny (Min Stock):", min_value=0, value=10, step=1, key="min_stock_dodaj")


        submit_button_dodaj = st.form_submit_button("Przyjmij Nową Partię do Magazynu")

        if submit_button_dodaj:
            dodaj_towar_z_partia(nowy_towar, ilosc_dodaj, lokalizacja_dodaj, cena_dodaj, min_stock_dodaj)

    st.markdown("---") 
    
    st.header("➖ Wydanie Towaru (FIFO)")

    if MAGAZYN:
        with st.form(key='usuwanie_form'):
            
            dostepne_klucze = sorted(MAGAZYN.keys())
            opcje_do_wyboru = []
            nazwa_do_klucza_map = {}
            suma_ilosci = {} 
            
            for (nazwa, lokalizacja), partie in MAGAZYN.items():
                ilosc_sumaryczna = sum(p['ilosc'] for p in partie)
                if ilosc_sumaryczna > 0:
                    czytelna_opcja = f"{nazwa} | {lokalizacja} (SUMA: {ilosc_sumaryczna} szt.)"
                    opcje_do_wyboru.append(czytelna_opcja)
                    nazwa_do_klucza_map[czytelna_opcja] = (nazwa, lokalizacja)
                    suma_ilosci[(nazwa, lokalizacja)] = ilosc_sumaryczna

            if not opcje_do_wyboru:
                st.info("Brak towaru do wydania.")
                st.stop()
            
            c6, c7 = st.columns(2)
            with c6:
                wybrana_opcja = st.selectbox(
                    "Wybierz pozycję do wydania (Lokalizacja):",
                    options=opcje_do_wyboru, 
                    key="select_usun"
                )
            
            klucz_do_usunięcia = nazwa_do_klucza_map[wybrana_opcja]
            max_ilosc = suma_ilosci.get(klucz_do_usunięcia, 1)

            with c7:
                ilosc_usun = st.number_input(
                    f"Ilość sztuk do wydania (Max: {max_ilosc}):",
                    min_value=1,
                    max_value=max_ilosc,
                    value=1, 
                    step=1, 
                    key="ilosc_usun"
                )

            submit_button_usun = st.form_submit_button("Usuń / Wydaj z Magazynu")

            if submit_button_usun:
                usun_towar_z_lokalizacja(klucz_do_usunięcia, ilosc_usun)
    else:
        st.info("Magazyn jest pusty, operacja wydania niemożliwa.")


st.markdown("---")

# --- Pełna Tabela Stanu Magazynu (Dół ekranu) ---
st.header("📊 Szczegółowy Stan Magazynu (Partie)")
st.info("Pełna lista wszystkich partii towarów z cenami i lokalizacjami.")

if MAGAZYN:
    wszystkie_dane_tabela = []
    
    for (nazwa, lokalizacja), partie in sorted(MAGAZYN.items()):
        for partia in partie:
            wszystkie_dane_tabela.append({
                "Nazwa Towaru": nazwa,
                "Lokalizacja": lokalizacja,
                "Ilość Sztuk": partia['ilosc'],
                "Cena Jednostkowa (PLN)": f"{partia['cena']:.2f}",
                "Wartość Partii (PLN)": f"{partia['ilosc'] * partia['cena']:.2f}",
                "Stan Minimalny": partia['min_stock']
            })

    st.dataframe(wszystkie_dane_tabela, hide_index=True, use_container_width=True)
else:
    st.info("Magazyn jest obecnie pusty.")

st.markdown("---")
st.caption("Wydawanie towaru odbywa się metodą FIFO (First-In, First-Out).")
