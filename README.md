# TODO API - Menadżer Zadań

**Autor:** Wiktor Stanisławski 82963
**Grupa:** ININ4 PR2

## Opis projektu
Proste REST API do zarządzania zadaniami.
Dane są zapisywane do pliku tasks.json.
API pozwala:
sprawdzić status serwera,
pobrać listę zadań,
dodać nowe zadanie,
edytować istniejące zadanie.

## Technologie
Python 3
FastAPI
Pydantic (walidacja danych)
JSON (do przechowywania danych)


## Instalacja i uruchomienie

### Wymagania
Python 3.10+
pip
curl

### Krok po kroku
# 1. Sklonuj repozytorium
git clone https://github.com/Wp-Stan/Programowanie_i_testowanie_BACKEND.git


# 3. Zainstaluj zależności
pip install fastapi uvicorn

# 4. Uruchom serwer
uvicorn main:app --reload

API działa pod adresem: http://127.0.0.1:8000
