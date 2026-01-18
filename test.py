import os
import json
import requests

BASE_URL = "http://127.0.0.1:8000"

# Liczniki wyników
tests_passed = 0
tests_failed = 0
failed_tests = []


def record_result(name: str, response: requests.Response, expected_status: int):
    """Zapisuje wynik testu i wypisuje szczegóły."""
    global tests_passed, tests_failed, failed_tests

    print(f"=== {name} ===")
    print(f"Status code: {response.status_code}")

    try:
        body = response.json()
        print(json.dumps(body, indent=2, ensure_ascii=False))
    except ValueError:
        print("RAW BODY:")
        print(response.text)

    print()

    # Zliczanie testów
    if response.status_code == expected_status:
        tests_passed += 1
    else:
        tests_failed += 1
        failed_tests.append((name, response.status_code, expected_status))


def main():
    global tests_passed, tests_failed, failed_tests

    # Usuwamy tasks.json – czyste środowisko testowe
    if os.path.exists("tasks.json"):
        os.remove("tasks.json")
        print("[info] Usunięto tasks.json przed testami.\n")

    # 1) GET /health
    r = requests.get(f"{BASE_URL}/health")
    record_result("GET /health", r, expected_status=200)

    # 2) GET /tasks – pusto
    r = requests.get(f"{BASE_URL}/tasks")
    record_result("GET /tasks (pusto)", r, expected_status=200)

    # 3) POST /tasks – poprawny
    valid_task = {
        "title": "Zrobic zadanie",
        "description": "Task z poprawnymi danymi",
    }
    r = requests.post(f"{BASE_URL}/tasks", json=valid_task)
    record_result("POST /tasks (poprawny)", r, expected_status=201)

    if r.status_code == 201:
        task_id = r.json()["id"]
    else:
        task_id = None

    # 4) POST /tasks – za długi tytuł
    too_long_title = {"title": "X" * 60, "description": "za długi tytuł"}
    r = requests.post(f"{BASE_URL}/tasks", json=too_long_title)
    record_result("POST /tasks (za długi tytuł)", r, expected_status=422)

    # 5) POST /tasks – za długi opis
    too_long_desc = {"title": "Poprawny", "description": "Y" * 300}
    r = requests.post(f"{BASE_URL}/tasks", json=too_long_desc)
    record_result("POST /tasks (za długi opis)", r, expected_status=422)

    # 6) POST /tasks – brak tytułu
    no_title = {"description": "brak tytułu"}
    r = requests.post(f"{BASE_URL}/tasks", json=no_title)
    record_result("POST /tasks (brak tytułu)", r, expected_status=422)

    # 7) PUT /tasks/{id} – poprawna aktualizacja
    if task_id is not None:
        update_data = {"completed": True, "description": "done!"}
        r = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data)
        record_result("PUT /tasks/{id} (poprawny)", r, expected_status=200)

    # 8) PUT /tasks/{id} – za długi tytuł
    if task_id is not None:
        bad_update = {"title": "Z" * 100}
        r = requests.put(f"{BASE_URL}/tasks/{task_id}", json=bad_update)
        record_result("PUT /tasks/{id} (za długi tytuł)", r, expected_status=422)

    # 9) PUT /tasks/9999 – nie istnieje
    r = requests.put(f"{BASE_URL}/tasks/9999", json={"completed": True})
    record_result("PUT /tasks/9999 (nie istnieje)", r, expected_status=404)

    # 10) GET /tasks – końcówka
    r = requests.get(f"{BASE_URL}/tasks")
    record_result("GET /tasks (końcowy)", r, expected_status=200)

    # ============================
    # PODSUMOWANIE TESTÓW
    # ============================

    print("\n==============================")
    print("       PODSUMOWANIE TESTÓW")
    print("==============================")
    print(f"Zaliczonych testów: {tests_passed}")
    print(f"Nieudanych testów:  {tests_failed}")

    if failed_tests:
        print("\nBłędy:")
        for name, got, expected in failed_tests:
            print(f"- {name}: zwrócono {got}, oczekiwano {expected}")
    else:
        print("\nWszystko przeszło")

    print("==============================\n")


if __name__ == "__main__":
    main()
