# Talerz — kalkulator kalorii

Dziennik jedzenia: kalorie, białko, węglowodany i tłuszcz. Można wpisać produkt albo zrobić zdjęcie talerza.

## Uruchomienie (Streamlit)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Dziennik zapisuje się lokalnie w `data/dziennik.json`.

## Zdjęcia

Rozpoznawanie produktów wymaga klucza xAI. Ustaw zmienną środowiskową `XAI_API_KEY` albo plik `.streamlit/secrets.toml`:

```toml
XAI_API_KEY = "twój_klucz"
```

Bez klucza działa wyszukiwarka i ręczne dodawanie.

Wartości odżywcze są orientacyjne i nie zastępują porady dietetyka.
