import streamlit as st

# Lista towarów
towary = []

# Funkcja do dodawania towaru
def dodaj_towar(nazwa):
    if nazwa not in towary:
        towary.append(nazwa)
        st.success(f'Towar "{nazwa}" został dodany.')
    else:
        st.warning(f'Towar "{nazwa}" już znajduje się na liście.')

# Funkcja do usuwania towaru
def usun_towar(nazwa):
    if nazwa in towary:
        towary.remove(nazwa)
        st.success(f'Towar "{nazwa}" został usunięty.')
    else:
        st.warning(f'Towar "{nazwa}" nie znajduje się na liście.')

# Strona aplikacji
st.title('Prosty Magazyn')

# Wyświetlanie dostępnych towarów
st.subheader('Lista towarów:')
if towary:
    st.write(', '.join(towary))
else:
    st.write('Brak towarów w magazynie.')

# Dodawanie towaru
nowy_towar = st.text_input('Podaj nazwę towaru do dodania:')
if st.button('Dodaj towar') and nowy_towar:
    dodaj_towar(nowy_towar)

# Usuwanie towaru
towar_do_usuniecia = st.text_input('Podaj nazwę towaru do usunięcia:')
if st.button('Usuń towar') and towar_do_usuniecia:
    usun_towar(towar_do_usuniecia)

# Dodanie instrukcji
st.info('Użyj pola tekstowego, aby dodać lub usunąć towar z listy magazynu.')
