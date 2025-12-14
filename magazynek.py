import streamlit as st
from typing import Dict, Tuple
import time
import datetime

# --- Konfiguracja Wygasania Sesji ---
# 120 sekund = 2 minuty
CZAS_WYGASANIA_SEKCJI_SEKUNDY = 120
KLUCZ_MAGAZYNU = 'magazyn'
KLUCZ_LAST_ACTIVITY = 'last_activity'

# --- Inicjalizacja Stanu Sesji ---

def inicjalizuj_stan_sesji():
    """Inicjalizuje magazyn i czas aktywności w st.session_state."""
    if KLUCZ_MAGAZYNU not in st.session_state:
        # Początkowe dane (tworzone tylko raz)
        st.session_state[KLUCZ_MAGAZYNU]: Dict[Tuple[str, str], int] = {
            ("Laptop", "Regał A01"): 10,
            ("Monitor", "Regał A01"): 5,
            ("Klawiatura", "Sektor B05"): 25
        }
    
    if KLUCZ_LAST_ACTIVITY not in st.session_state:
        # Zapisz obecny czas jako czas ostatniej aktywności
        st.session_state[KLUCZ_LAST_ACTIVITY] = time.time()

def sprawdz_wygasanie_sesji():
    """Sprawdza, czy sesja wygasła z powodu braku aktywności."""
    
    czas_teraz = time.time()
    czas_ostatniej_aktywnosci = st.session_state.get(KLUCZ_LAST_ACTIVITY, czas_teraz)
    
    # Obliczanie różnicy w sekundach
    roznica_czasu = czas_teraz - czas_ostatniej_aktywnosci
    
    if roznica_czasu > CZAS_WYGASANIA_SEKCJI_SEKUNDY:
        # Sesja wygasła! Resetujemy magazyn i czas
        st.session_state[KLUCZ_MAGAZYNU] = {}
        st.session_state[KLUCZ_LAST_ACTIVITY] = czas_teraz
        st.error(f"⚠️ **Sesja Wygasła!** Brak aktywności przez ponad {CZAS_WYGASANIA_SEKCJI_SEKUNDY} sekund. Magazyn został zresetowany.")
    else:
        # Aktualizujemy czas ostatniej aktywności przy każdym przebiegu skryptu Streamlit
        st.session_state[KLUCZ_LAST_ACTIVITY] = czas_teraz
        
        # Wyświetlanie pozostałego czasu (dla dewelopera)
        czas_pozostaly = int(CZAS_WYGASANIA_SEKCJI_SEKUNDY - roznica_czasu)
        st.sidebar.info(f"Sesja wygaśnie za: **{max(0, czas_pozostaly)}** sekund.")


# --- Funkcje Magazynowe (Operujące na st.session_state) ---

def dodaj_towar_z_ilosc_i_lokalizacja(nazwa: str, ilosc: int, lokalizacja: str):
    """Dodaje lub aktualizuje towar wraz z podaną ilością i lokalizacją."""
    
    nazwa = nazwa.strip()
    lokalizacja = lokalizacja.strip().upper() 
    
    if not nazwa or not lokalizacja:
        st.error("Wprowadź zarówno nazwę towaru, jak i lokalizację.")
        return

    if ilosc <= 0:
        st.error("Ilość musi być większa niż zero.")
        return

    klucz = (nazwa, lokalizacja)
    
    magazyn = st.session_state[KLUCZ_MAGAZYNU]

    if klucz in magazyn:
        magazyn[klucz] += ilosc
        st.success(f"Zaktualizowano: Dodano **{ilosc}** sztuk towaru **{nazwa}** w **{lokalizacja}**. Nowa ilość: **{magazyn[klucz]}**.")
    else:
        magazyn[klucz] = ilosc
        st.success(f"Nowy towar dodany: **{nazwa}** w ilości **{ilosc}** sztuk, na pozycji **{lokalizacja}**.")

def usun_towar_z_ilosc_i_lokalizacja(klucz: Tuple[str, str], ilosc: int):
    """Usuwa podaną ilość towaru z danej lokalizacji."""
    
    nazwa, lokalizacja = klucz
    magazyn = st.session_state[KLUCZ_MAGAZYNU]
    
    if ilosc <= 0:
        st.error("Ilość do usunięcia musi być większa niż zero.")
        return

    if klucz not in magazyn:
        st.error(f"Towar **{nazwa}** na pozycji **{lokalizacja}** nie został znaleziony w magazynie.")
        return

    obecna_ilosc = magazyn[klucz]

    if ilosc >= obecna_ilosc:
        del magazyn[klucz]
        st.success(f"Usunięto cały zapas towaru **{nazwa}** z **{lokalizacja}** (usunięto **{obecna_ilosc}** sztuk).")
    else:
        magazyn[klucz] -= ilosc
        st.success(f"Usunięto **{ilosc}** sztuk towaru **{nazwa}** z **{lokalizacja}**. Pozostało: **{magazyn[klucz]}**.")


# --- Główny Interfejs Użytkownika Streamlit ---

st.set_page_config(page_title="Magazyn z Wygasającą Sesją", layout="centered")

# KROK 1: Inicjalizacja i Sprawdzenie Wygasania
inicjalizuj_stan_sesji()
sprawdz_wygasanie_sesji() 

MAGAZYN = st.session_state[KLUCZ_MAGAZYNU]

st.title("⏱️ Magazyn z Symulacją Wygasania Sesji")
st.caption(f"Dane są utrzymywane dzięki `st.session_state`, ale resetują się po {CZAS_WYGASANIA_SEKCJI_SEKUNDY} sekundach bezczynności.")

# --- Sekcja Dodawania Towaru ---
st.header("➕ Dodaj / Przyjmij Towar")
with st.form(key='dodawanie_form'):
    col1, col2 = st.columns(2)
    with col1:
        nowy_towar = st.text_input("Nazwa Towaru:", key="input_dodaj")
    with col2:
        lokalizacja_dodaj = st.text_input("Lokalizacja (np. Regał A01):", key="lokalizacja_dodaj")

    ilosc_dodaj = st.number_input("Ilość sztuk:", min_value=1, value=1, step=1, key="ilosc_dodaj")

    submit_button_dodaj = st.form_submit_button("Dodaj / Przyjmij do Magazynu")

    if submit_button_dodaj:
        dodaj_towar_z_ilosc_i_lokalizacja(nowy_towar, ilosc_dodaj, lokalizacja_dodaj)


# --- Sekcja Usuwania Towaru ---
st.header("➖ Usuń / Wydaj Towar")
if MAGAZYN:
    with st.form(key='usuwanie_form'):
        
        dostepne_klucze_sorted = sorted(MAGAZYN.keys())
        opcje_do_wyboru = [
            f"{nazwa} | {lokalizacja} ({ilosc} szt.)"
            for (nazwa, lokalizacja), ilosc in MAGAZYN.items()
        ]
        
        indeks_wyboru = st.selectbox(
            "Wybierz pozycję do wydania:",
            options=range(len(opcje_do_wyboru)),
            format_func=lambda i: opcje_do_wyboru[i], 
            key="select_usun"
        )
        
        klucz_do_usunięcia = dostepne_klucze_sorted[indeks_wyboru]
        max_ilosc = MAGAZYN.get(klucz_do_usunięcia, 1)

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
            usun_towar_z_ilosc_i_lokalizacja(klucz_do_usunięcia, ilosc_usun)
else:
    st.info("Magazyn jest pusty, nic do usunięcia.")


# --- Sekcja Aktualnego Stanu Magazynu ---
st.header("📊 Aktualny Stan Magazynu")

if MAGAZYN:
    st.write(f"Liczba unikalnych pozycji: **{len(MAGAZYN)}**")
    
    dane_tabela = [
        {"Nazwa Towaru": nazwa, "Lokalizacja": lokalizacja, "Ilość Sztuk": ilosc} 
        for (nazwa, lokalizacja), ilosc in sorted(MAGAZYN.items())
    ]
    
    st.dataframe(dane_tabela, hide_index=True)
else:
    st.info("Magazyn jest obecnie pusty.")

st.markdown("---")
st.info("💡 **Działanie:** Każda interakcja z aplikacją (np. naciśnięcie przycisku, zmiana pola) resetuje licznik braku aktywności. Jeśli upłynie 120 sekund bez interakcji, dane zostaną usunięte.")
