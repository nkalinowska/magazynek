import streamlit as st

# --- Globalna lista magazynu (pamiętaj: resetowana przy każdej interakcji/odświeżeniu!) ---
# W realnej aplikacji Streamlit użyłbyś st.session_state, ale zgodnie z prośbą, pomijamy to.
# Do celów demonstracyjnych, inicjujemy ją z kilkoma elementami.
MAGAZYN = ["Laptop", "Monitor", "Klawiatura"]

def dodaj_towar(nazwa):
    """Dodaje towar do listy MAGAZYN."""
    if nazwa and nazwa not in MAGAZYN:
        MAGAZYN.append(nazwa)
        st.success(f"Dodano: **{nazwa}**")
    elif nazwa in MAGAZYN:
        st.warning(f"Towar **{nazwa}** jest już w magazynie!")
    else:
        st.error("Wprowadź nazwę towaru.")

def usun_towar(nazwa):
    """Usuwa towar z listy MAGAZYN."""
    try:
        MAGAZYN.remove(nazwa)
        st.success(f"Usunięto: **{nazwa}**")
    except ValueError:
        st.error(f"Towar **{nazwa}** nie został znaleziony w magazynie.")

# --- Interfejs użytkownika Streamlit ---

st.set_page_config(page_title="Prosty Magazyn (Streamlit)", layout="centered")

st.title("📦 Prosty Magazyn")
st.caption("Aplikacja demonstracyjna bez użycia st.session_state ani zapisu danych.")

# --- Sekcja Dodawania Towaru ---
st.header("➕ Dodaj Towar")
with st.form(key='dodawanie_form'):
    nowy_towar = st.text_input("Nazwa Towaru do dodania:", key="input_dodaj")
    submit_button_dodaj = st.form_submit_button("Dodaj do Magazynu")

    if submit_button_dodaj:
        # Streamlit wywołuje funkcję dodaj_towar
        dodaj_towar(nowy_towar)


# --- Sekcja Usuwania Towaru ---
st.header("➖ Usuń Towar")
if MAGAZYN:
    # Używamy selectbox do wyboru towaru do usunięcia
    towar_do_usunięcia = st.selectbox(
        "Wybierz Towar do usunięcia:",
        options=MAGAZYN,
        key="select_usun"
    )

    if st.button("Usuń z Magazynu", key="button_usun"):
        # Streamlit wywołuje funkcję usun_towar
        usun_towar(towar_do_usunięcia)
else:
    st.info("Magazyn jest pusty, nic do usunięcia.")


# --- Sekcja Aktualnego Stanu Magazynu ---
st.header("📊 Aktualny Stan Magazynu")

if MAGAZYN:
    st.write(f"Liczba pozycji: **{len(MAGAZYN)}**")
    # Wyświetlanie listy w formie listy punktowej
    st.markdown("#### Lista Towarów:")
    magazyn_list_markdown = "\n".join([f"* {towar}" for towar in MAGAZYN])
    st.markdown(magazyn_list_markdown)
else:
    st.info("Magazyn jest obecnie pusty.")

st.markdown("---")
st.info("💡 **Uwaga:** Ze względu na brak zapisu sesji/danych, lista jest resetowana przy każdym przeładowaniu strony lub interakcji powodującej ponowne uruchomienie skryptu.")
