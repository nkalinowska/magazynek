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
    """Inicjalizuje magazyn i czas aktywności w st.session_state."""
    if KLUCZ_MAGAZYNU not in st.session_state:
        # Początkowe dane (Klucz: (Nazwa, Lokalizacja), Wartość: Lista Partii)
        st.session_state[KLUCZ_MAGAZYNU]: Dict[Tuple[str, str], List[Dict[str, float]]] = {
            ("Laptop", "Regał A01"): [
                {'ilosc': 10, 'cena': 2500.00},
                {'ilosc': 5, 'cena': 2700.00}
            ],
            ("Monitor", "Regał A01"): [
                {'ilosc': 20, 'cena': 850.50}
            ],
            ("Klawiatura", "Sektor B05"): [
                {'ilosc': 50, 'cena': 150.00}
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
        st.session_state[KLUCZ_LAST_ACTIVITY] = czas_teraz
        czas_pozostaly = int(CZAS_WYGASANIA_SEKCJI_SEKUNDY - roznica_czasu)
        st.sidebar.info(f"Sesja wygaśnie za: **{max(0, czas_pozostaly)}** sekund.")

# --- Funkcje Magazynowe (Operujące na st.session_state) ---

def zloz_zamowienie(nazwa: str, ilosc: int):
    """Symuluje składanie zamówienia, sprawdzając dostępność w magazynie."""
    
    nazwa = nazwa.strip()

    if not nazwa:
        st.error("Wprowadź nazwę towaru, który chcesz zamówić.")
        return

    if ilosc <= 0:
        st.error("Ilość musi być większa niż zero.")
        return

    magazyn = st.session_state[KLUCZ_MAGAZYNU]
    
    # Oblicz sumę dostępnej ilości dla danej nazwy towaru, niezależnie od lokalizacji i partii
    dostepna_ilosc = 0
    # Iterujemy po kluczach (nazwa, lokalizacja)
    for (item_name, _), partie in magazyn.items():
        if item_name.lower() == nazwa.lower():
            dostepna_ilosc += sum(p['ilosc'] for p in partie)

    st.subheader("Wynik Sprawdzenia Dostępności")
    st.markdown("---")
    st.metric(label=f"Całkowita Dostępna Ilość dla {nazwa}", value=f"{dostepna_ilosc} szt.")

    if dostepna_ilosc >= ilosc:
        # Sukces: Towar dostępny
        st.success(f"✅ Zamówienie na **{ilosc}** sztuk towaru **{nazwa}** jest **dostępne w magazynie** i może zostać zrealizowane natychmiast.")
        st.info("Aby sfinalizować wydanie, przejdź do sekcji 'Usuń / Wydaj Towar (FIFO)'.")
    else:
        # Częściowa/Brak dostępności
        brakujaca_ilosc = ilosc - dostepna_ilosc
        st.warning(f"❌ Towar **{nazwa}** jest **niedostępny** w wystarczającej ilości.")
        st.error(f"Wymagana ilość: {ilosc} szt. Dostępna ilość: {dostepna_ilosc} szt. **Wymagane domówienie: {brakujaca_ilosc} szt.**")
        
    st.markdown("---")
    
# Pozostałe funkcje (dodaj i usun) pozostają bez zmian:

def dodaj_towar_z_partia(nazwa: str, ilosc: int, lokalizacja: str, cena: float):
    # ... (kod pozostaje bez zmian) ...
    nazwa = nazwa.strip()
    lokalizacja = lokalizacja.strip().upper() 
    
    if not nazwa or not lokalizacja:
        st.error("Wprowadź nazwę towaru i lokalizację.")
        return

    if ilosc <= 0:
        st.error("Ilość musi być większa niż zero.")
        return
    
    if cena <= 0:
        st.error("Cena musi być większa niż zero.")
        return

    klucz = (nazwa, lokalizacja)
    magazyn = st.session_state[KLUCZ_MAGAZYNU]
    
    nowa_partia = {'ilosc': ilosc, 'cena': round(cena, 2)}
    
    if klucz not in magazyn:
        magazyn[klucz] = []
    
    magazyn[klucz].append(nowa_partia)
    
    st.success(f"Przyjęto nową partię: **{nazwa}** ({ilosc} szt. @ {cena:.2f} PLN) na pozycji **{lokalizacja}**.")


def usun_towar_z_lokalizacja(klucz: Tuple[str, str], ilosc_do_usuniecia: int):
    # ... (kod pozostaje bez zmian) ...
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

st.set_page_config(page_title="Magazyn z Zamówieniami i Wygasającą Sesją", layout="centered")

inicjalizuj_stan_sesji()
sprawdz_wygasanie_sesji() 

MAGAZYN = st.session_state[KLUCZ_MAGAZYNU]

st.title("🛒 System Zarządzania Magazynem (z Zamówieniami)")
st.caption(f"Dane są utrzymywane dzięki `st.session_state`, ale resetują się po {CZAS_WYGASANIA_SEKCJI_SEKUNDY} sekundach bezczynności.")

# --- Sekcja Dodawania Towaru ---
st.header("➕ Dodaj / Przyjmij Nową Partię")
with st.form(key='dodawanie_form'):
    col1, col2 = st.columns(2)
    with col1:
        nowy_towar = st.text_input("Nazwa Towaru:", key="input_dodaj")
    with col2:
        lokalizacja_dodaj = st.text_input("Lokalizacja (np. Regał A01):", key="lokalizacja_dodaj")

    col3, col4 = st.columns(2)
    with col3:
        ilosc_dodaj = st.number_input("Ilość sztuk:", min_value=1, value=1, step=1, key="ilosc_dodaj")
    with col4:
        cena_dodaj = st.number_input("Cena jednostkowa (PLN):", min_value=0.01, value=100.00, step=0.01, key="cena_dodaj", format="%.2f")

    submit_button_dodaj = st.form_submit_button("Przyjmij Nową Partię do Magazynu")

    if submit_button_dodaj:
        dodaj_towar_z_partia(nowy_towar, ilosc_dodaj, lokalizacja_dodaj, cena_dodaj)

st.markdown("---")

# --- NOWA SEKCJA: Składanie Zamówień ---
st.header("🛒 Złóż Zamówienie Klienta")
st.info("Ta sekcja sprawdza sumaryczną dostępność towaru w całym magazynie. Nie modyfikuje stanów magazynowych.")

with st.form(key='zamowienie_form'):
    
    # 1. Lista unikalnych nazw (do wyboru)
    unikalne_nazwy = sorted(list(set(nazwa for (nazwa, _), _ in MAGAZYN.items())))
    opcje_zamowienia = ["--- Wpisz własną nazwę ---"] + unikalne_nazwy
    
    col_order_1, col_order_2 = st.columns(2)
    
    with col_order_1:
        wybor_nazwy = st.selectbox(
            "Wybierz towar z magazynu:",
            options=opcje_zamowienia,
            key="select_zamow"
        )
    
    # 2. Obsługa wyboru własnej nazwy
    if wybor_nazwy == "--- Wpisz własną nazwę ---":
        nazwa_zamowienia = st.text_input("Nazwa Towaru do zamówienia:", key="input_zamow_custom")
    else:
        nazwa_zamowienia = wybor_nazwy
    
    with col_order_2:
        ilosc_zamowienia = st.number_input(
            "Ilość sztuk do zamówienia:", 
            min_value=1, 
            value=1, 
            step=1, 
            key="ilosc_zamow"
        )

    submit_button_zamow = st.form_submit_button("Sprawdź Dostępność i Złóż Zamówienie")

    if submit_button_zamow:
        # Przekazujemy finalną nazwę i ilość do funkcji sprawdzającej
        zloz_zamowienie(nazwa_zamowienia, ilosc_zamowienia)

st.markdown("---")

# --- Sekcja Usuwania Towaru ---
st.header("➖ Usuń / Wydaj Towar (FIFO)")
if MAGAZYN:
    
    # 1. Przygotowanie kluczy i opcji do wyboru
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
        st.info("Brak towaru w magazynie.")
        st.stop()

    with st.form(key='usuwanie_form'):
        
        col_remove_1, col_remove_2 = st.columns(2)

        with col_remove_1:
            wybrana_opcja = st.selectbox(
                "Wybierz pozycję do wydania (Nazwa i Lokalizacja):",
                options=opcje_do_wyboru, 
                key="select_usun"
            )
        
        klucz_do_usunięcia = nazwa_do_klucza_map[wybrana_opcja]
        max_ilosc = suma_ilosci.get(klucz_do_usunięcia, 1)

        with col_remove_2:
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
    st.info("Magazyn jest pusty, nic do usunięcia.")


# --- Sekcja Aktualnego Stanu Magazynu (Szczegółowo) ---
st.header("📊 Szczegółowy Stan Magazynu (Partie)")

if MAGAZYN:
    wszystkie_dane_tabela = []
    
    for (nazwa, lokalizacja), partie in sorted(MAGAZYN.items()):
        for partia in partie:
            wszystkie_dane_tabela.append({
                "Nazwa Towaru": nazwa,
                "Lokalizacja": lokalizacja,
                "Ilość Sztuk": partia['ilosc'],
                "Cena Jednostkowa (PLN)": f"{partia['cena']:.2f}",
                "Wartość Partii (PLN)": f"{partia['ilosc'] * partia['cena']:.2f}"
            })

    st.dataframe(wszystkie_dane_tabela, hide_index=True)
else:
    st.info("Magazyn jest obecnie pusty.")
