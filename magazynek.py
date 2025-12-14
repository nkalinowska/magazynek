import streamlit as st
from typing import Dict, Tuple

# --- Globalny Słownik Magazynu (Klucz: (Nazwa Towaru, Lokalizacja), Wartość: Ilość) ---
# Uwaga: Nadal resetowany przy każdej interakcji/odświeżeniu.
MAGAZYN: Dict[Tuple[str, str], int] = {
    ("Laptop", "Regał A01"): 10,
    ("Monitor", "Regał A01"): 5,
    ("Klawiatura", "Sektor B05"): 25,
    ("Myszka", "Regał A01"): 15 # Dwa różne towary w tej samej lokalizacji
}

def dodaj_towar_z_ilosc_i_lokalizacja(nazwa: str, ilosc: int, lokalizacja: str):
    """Dodaje lub aktualizuje towar wraz z podaną ilością i lokalizacją."""
    
    # Normalizacja danych wejściowych
    nazwa = nazwa.strip()
    lokalizacja = lokalizacja.strip().upper() # Lokalizacje zapisujemy dużymi literami
    
    if not nazwa or not lokalizacja:
        st.error("Wprowadź zarówno nazwę towaru, jak i lokalizację.")
        return

    if ilosc <= 0:
        st.error("Ilość musi być większa niż zero.")
        return

    klucz = (nazwa, lokalizacja)
    
    if klucz in MAGAZYN:
        MAGAZYN[klucz] += ilosc
        st.success(f"Zaktualizowano: Dodano **{ilosc}** sztuk towaru **{nazwa}** w **{lokalizacja}**. Nowa ilość: **{MAGAZYN[klucz]}**.")
    else:
        MAGAZYN[klucz] = ilosc
        st.success(f"Nowy towar dodany: **{nazwa}** w ilości **{ilosc}** sztuk, na pozycji **{lokalizacja}**.")

def usun_towar_z_ilosc_i_lokalizacja(klucz: Tuple[str, str], ilosc: int):
    """Usuwa podaną ilość towaru z danej lokalizacji."""
    
    nazwa, lokalizacja = klucz
    
    if ilosc <= 0:
        st.error("Ilość do usunięcia musi być większa niż zero.")
        return

    if klucz not in MAGAZYN:
        st.error(f"Towar **{nazwa}** na pozycji **{lokalizacja}** nie został znaleziony w magazynie.")
        return

    obecna_ilosc = MAGAZYN[klucz]

    if ilosc >= obecna_ilosc:
        # Usuń cały wpis
        del MAGAZYN[klucz]
        st.success(f"Usunięto cały zapas towaru **{nazwa}** z **{lokalizacja}** (usunięto **{obecna_ilosc}** sztuk).")
    else:
        # Zmniejsz ilość
        MAGAZYN[klucz] -= ilosc
        st.success(f"Usunięto **{ilosc}** sztuk towaru **{nazwa}** z **{lokalizacja}**. Pozostało: **{MAGAZYN[klucz]}**.")

# --- Interfejs użytkownika Streamlit ---

st.set_page_config(page_title="Magazyn z Lokalizacją (Streamlit)", layout="centered")

st.title("🗺️ Magazyn z Lokalizacją i Ilościami")
st.caption("Klucz Magazynu: (Nazwa Towaru, Lokalizacja). Aplikacja demonstracyjna bez użycia st.session_state.")

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
        # Tworzymy czytelną listę opcji do wyboru w selectbox: "Nazwa Towaru | Lokalizacja (Ilość)"
        dostepne_klucze_sorted = sorted(MAGAZYN.keys())
        opcje_do_wyboru = [
            f"{nazwa} | {lokalizacja} ({ilosc} szt.)"
            for (nazwa, lokalizacja), ilosc in MAGAZYN.items()
        ]
        
        # Streamlit potrzebuje listy kluczy do wewnętrznego mapowania, ale wyświetla opcje_do_wyboru
        indeks_wyboru = st.selectbox(
            "Wybierz pozycję do wydania (Nazwa i Lokalizacja):",
            options=range(len(opcje_do_wyboru)),
            format_func=lambda i: opcje_do_wyboru[i], # Użycie format_func do wyświetlenia czytelnej opcji
            key="select_usun"
        )
        
        # Pobieramy faktyczny klucz (nazwa, lokalizacja) na podstawie wybranego indeksu
        klucz_do_usunięcia = dostepne_klucze_sorted[indeks_wyboru]
        
        # Obliczenie maksymalnej ilości do usunięcia dla wybranego klucza
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
    st.write(f"Liczba unikalnych pozycji (towar + lokalizacja): **{len(MAGAZYN)}**")
    
    # Przygotowanie danych do wyświetlenia w tabeli
    dane_tabela = [
        {"Nazwa Towaru": nazwa, "Lokalizacja": lokalizacja, "Ilość Sztuk": ilosc} 
        for (nazwa, lokalizacja), ilosc in sorted(MAGAZYN.items())
    ]
    
    st.dataframe(dane_tabela, hide_index=True)
else:
    st.info("Magazyn jest obecnie pusty.")

st.markdown("---")
st.warning("💡 **Kluczowa Uwaga:** Magazyn wciąż nie zapisuje stanu (bez `st.session_state`). Wszelkie zmiany zostaną zresetowane po przeładowaniu strony lub interakcji.")
