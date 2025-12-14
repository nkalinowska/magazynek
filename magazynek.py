import streamlit as st
from typing import Dict, Union

# --- Globalny Słownik Magazynu (Nazwa Towaru: Ilość) ---
# Uwaga: Nadal resetowany przy każdej interakcji/odświeżeniu, ponieważ nie używamy st.session_state.
MAGAZYN: Dict[str, int] = {
    "Laptop": 10,
    "Monitor": 5,
    "Klawiatura": 25
}

def dodaj_towar_z_ilosc(nazwa: str, ilosc: int):
    """Dodaje lub aktualizuje towar wraz z podaną ilością."""
    if not nazwa:
        st.error("Wprowadź nazwę towaru.")
        return

    if ilosc <= 0:
        st.error("Ilość musi być większa niż zero.")
        return

    if nazwa in MAGAZYN:
        MAGAZYN[nazwa] += ilosc
        st.success(f"Zaktualizowano: Dodano **{ilosc}** sztuk towaru **{nazwa}**. Nowa ilość: **{MAGAZYN[nazwa]}**.")
    else:
        MAGAZYN[nazwa] = ilosc
        st.success(f"Nowy towar dodany: **{nazwa}** w ilości **{ilosc}** sztuk.")

def usun_towar_z_ilosc(nazwa: str, ilosc: int):
    """Usuwa podaną ilość towaru lub usuwa cały towar, jeśli ilość jest zbyt duża."""
    if not nazwa:
        st.error("Wybierz nazwę towaru do usunięcia.")
        return

    if ilosc <= 0:
        st.error("Ilość do usunięcia musi być większa niż zero.")
        return

    if nazwa not in MAGAZYN:
        st.error(f"Towar **{nazwa}** nie został znaleziony w magazynie.")
        return

    obecna_ilosc = MAGAZYN[nazwa]

    if ilosc >= obecna_ilosc:
        # Usuń cały wpis, jeśli usuwana ilość jest większa lub równa obecnej
        del MAGAZYN[nazwa]
        st.success(f"Usunięto cały zapas towaru **{nazwa}** (usunięto **{obecna_ilosc}** sztuk).")
    else:
        # Zmniejsz ilość
        MAGAZYN[nazwa] -= ilosc
        st.success(f"Usunięto **{ilosc}** sztuk towaru **{nazwa}**. Pozostało: **{MAGAZYN[nazwa]}**.")

# --- Interfejs użytkownika Streamlit ---

st.set_page_config(page_title="Prosty Magazyn z Ilościami (Streamlit)", layout="centered")

st.title("📦 Prosty Magazyn (z Ilościami)")
st.caption("Aplikacja demonstracyjna bez użycia st.session_state.")

# --- Sekcja Dodawania Towaru ---
st.header("➕ Dodaj / Przyjmij Towar")
with st.form(key='dodawanie_form'):
    col1, col2 = st.columns(2)
    with col1:
        nowy_towar = st.text_input("Nazwa Towaru:", key="input_dodaj")
    with col2:
        ilosc_dodaj = st.number_input("Ilość sztuk:", min_value=1, value=1, step=1, key="ilosc_dodaj")

    submit_button_dodaj = st.form_submit_button("Dodaj / Przyjmij do Magazynu")

    if submit_button_dodaj:
        dodaj_towar_z_ilosc(nowy_towar, ilosc_dodaj)


# --- Sekcja Usuwania Towaru ---
st.header("➖ Usuń / Wydaj Towar")
if MAGAZYN:
    with st.form(key='usuwanie_form'):
        # Sortujemy klucze (nazwy towarów) dla przejrzystości
        dostepne_towary = sorted(MAGAZYN.keys())
        
        col3, col4 = st.columns(2)
        with col3:
            # Używamy selectbox do wyboru towaru do usunięcia
            towar_do_usunięcia = st.selectbox(
                "Wybierz Towar do wydania:",
                options=dostepne_towary,
                key="select_usun"
            )
        
        # Obliczenie maksymalnej ilości do usunięcia dla wybranego towaru
        max_ilosc = MAGAZYN.get(towar_do_usunięcia, 1)

        with col4:
            ilosc_usun = st.number_input(
                "Ilość sztuk do wydania:",
                min_value=1,
                max_value=max_ilosc, # Ograniczenie do faktycznej ilości
                value=1, 
                step=1, 
                key="ilosc_usun"
            )

        submit_button_usun = st.form_submit_button("Usuń / Wydaj z Magazynu")

        if submit_button_usun:
            # Wywołujemy funkcję usuwającą
            usun_towar_z_ilosc(towar_do_usunięcia, ilosc_usun)
else:
    st.info("Magazyn jest pusty, nic do usunięcia.")


# --- Sekcja Aktualnego Stanu Magazynu ---
st.header("📊 Aktualny Stan Magazynu")

if MAGAZYN:
    st.write(f"Liczba unikalnych pozycji: **{len(MAGAZYN)}**")
    
    # Przygotowanie danych do wyświetlenia w tabeli
    dane_tabela = [
        {"Nazwa Towaru": nazwa, "Ilość Sztuk": ilosc} 
        for nazwa, ilosc in sorted(MAGAZYN.items())
    ]
    
    # Wyświetlanie słownika jako przejrzystej tabeli
    st.dataframe(dane_tabela, hide_index=True)
else:
    st.info("Magazyn jest obecnie pusty.")

st.markdown("---")
st.warning("💡 **Kluczowa Uwaga:** Zgodnie z prośbą, ten magazyn jest implementowany bez zapisywania stanu (bez `st.session_state`). Oznacza to, że **wszelkie zmiany (dodanie/usunięcie) zostaną zresetowane**, gdy tylko aplikacja przeładuje się po interakcji lub odświeżeniu strony.")
