"""Baza produktów na 100 g i proste liczenie porcji."""

FOODS = [
    {"name": "Mleko 2%", "group": "Nabiał", "kcal": 50, "protein": 3.4, "carbs": 4.8, "fat": 2},
    {"name": "Jogurt naturalny", "group": "Nabiał", "kcal": 61, "protein": 4.3, "carbs": 4.7, "fat": 2},
    {"name": "Skyr naturalny", "group": "Nabiał", "kcal": 63, "protein": 11, "carbs": 4, "fat": 0.2},
    {"name": "Twaróg półtłusty", "group": "Nabiał", "kcal": 133, "protein": 19, "carbs": 3.5, "fat": 5},
    {"name": "Ser gouda", "group": "Nabiał", "kcal": 356, "protein": 25, "carbs": 2, "fat": 27},
    {"name": "Jajko kurze", "group": "Nabiał", "kcal": 143, "protein": 13, "carbs": 1, "fat": 10},
    {"name": "Jajecznica na maśle", "group": "Dania", "kcal": 196, "protein": 12, "carbs": 1.5, "fat": 16},
    {"name": "Pierś z kurczaka, grill", "group": "Mięso", "kcal": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    {"name": "Indyk pieczony", "group": "Mięso", "kcal": 135, "protein": 29, "carbs": 0, "fat": 2},
    {"name": "Schab pieczony", "group": "Mięso", "kcal": 198, "protein": 27, "carbs": 0, "fat": 10},
    {"name": "Kotlet schabowy", "group": "Dania", "kcal": 280, "protein": 16, "carbs": 12, "fat": 18},
    {"name": "Polędwica wołowa", "group": "Mięso", "kcal": 187, "protein": 26, "carbs": 0, "fat": 9},
    {"name": "Szynka z piersi kurczaka", "group": "Mięso", "kcal": 105, "protein": 18, "carbs": 1, "fat": 3},
    {"name": "Łosoś pieczony", "group": "Ryby", "kcal": 208, "protein": 20, "carbs": 0, "fat": 13},
    {"name": "Dorsz pieczony", "group": "Ryby", "kcal": 105, "protein": 23, "carbs": 0, "fat": 1},
    {"name": "Tuńczyk w sosie własnym", "group": "Ryby", "kcal": 116, "protein": 26, "carbs": 0, "fat": 1},
    {"name": "Ryż biały gotowany", "group": "Zboża", "kcal": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
    {"name": "Kasza gryczana gotowana", "group": "Zboża", "kcal": 110, "protein": 3.4, "carbs": 21, "fat": 1},
    {"name": "Makaron gotowany", "group": "Zboża", "kcal": 131, "protein": 5, "carbs": 25, "fat": 1.1},
    {"name": "Płatki owsiane", "group": "Zboża", "kcal": 379, "protein": 13, "carbs": 67, "fat": 7},
    {"name": "Owsianka na mleku 2%", "group": "Dania", "kcal": 95, "protein": 4, "carbs": 14, "fat": 2.5},
    {"name": "Chleb żytni", "group": "Zboża", "kcal": 215, "protein": 6.5, "carbs": 42, "fat": 1.5},
    {"name": "Bułka kajzerka", "group": "Zboża", "kcal": 280, "protein": 9, "carbs": 54, "fat": 3},
    {"name": "Pomidor", "group": "Warzywa", "kcal": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    {"name": "Ogórek", "group": "Warzywa", "kcal": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1},
    {"name": "Brokuł", "group": "Warzywa", "kcal": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
    {"name": "Ziemniak gotowany", "group": "Warzywa", "kcal": 86, "protein": 1.7, "carbs": 20, "fat": 0.1},
    {"name": "Jabłko", "group": "Owoce", "kcal": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
    {"name": "Banan", "group": "Owoce", "kcal": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
    {"name": "Oliwa z oliwek", "group": "Tłuszcze", "kcal": 884, "protein": 0, "carbs": 0, "fat": 100},
    {"name": "Masło", "group": "Tłuszcze", "kcal": 740, "protein": 0.7, "carbs": 0.6, "fat": 82},
    {"name": "Awokado", "group": "Tłuszcze", "kcal": 160, "protein": 2, "carbs": 9, "fat": 15},
    {"name": "Pierogi ruskie", "group": "Dania", "kcal": 200, "protein": 6, "carbs": 30, "fat": 6},
    {"name": "Pizza margherita", "group": "Dania", "kcal": 266, "protein": 11, "carbs": 33, "fat": 10},
    {"name": "Bigos", "group": "Dania", "kcal": 95, "protein": 4, "carbs": 6, "fat": 6},
    {"name": "Kawa czarna", "group": "Napoje", "kcal": 2, "protein": 0.1, "carbs": 0, "fat": 0},
    {"name": "Czekolada mleczna", "group": "Słodycze", "kcal": 535, "protein": 7, "carbs": 59, "fat": 30},
    {"name": "Miód", "group": "Słodycze", "kcal": 304, "protein": 0.3, "carbs": 82, "fat": 0},
]


def fold(value: str) -> str:
    table = str.maketrans("ąćęłńóśźż", "acelnoszz")
    return value.lower().translate(table)


def search_foods(query: str, foods: list[dict]) -> list[dict]:
    q = fold(query.strip())
    if not q:
        return foods[:8]
    return [food for food in foods if q in fold(food["name"]) or q in fold(food.get("group", ""))]


def from_per_100(food: dict, grams: float) -> dict:
    factor = grams / 100

    def scale(key: str) -> float:
        return round(float(food[key]) * factor, 1)

    return {
        "kcal": int(round(scale("kcal"))),
        "protein": scale("protein"),
        "carbs": scale("carbs"),
        "fat": scale("fat"),
    }


def suggest_targets(sex: str, age: float, cm: float, kg: float, activity: str, aim: str) -> dict:
    bmr = 10 * kg + 6.25 * cm - 5 * age + (5 if sex == "m" else -161)
    factor = {"niska": 1.3, "wysoka": 1.7}.get(activity, 1.5)
    tdee = bmr * factor
    if aim == "schudnac":
        tdee *= 0.85
    if aim == "przytyc":
        tdee *= 1.1
    kcal = max(1200, int(round(tdee / 10) * 10))
    protein = round(kg * (1.8 if aim == "schudnac" else 1.6))
    fat = round(kg * 0.8)
    carbs = max(0, round((kcal - protein * 4 - fat * 9) / 4))
    return {"kcal": kcal, "protein": protein, "carbs": carbs, "fat": fat}
