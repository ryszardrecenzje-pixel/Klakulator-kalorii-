"""Talerz — dziennik kalorii. Uruchom: streamlit run app.py"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

from foods import FOODS, from_per_100, search_foods, suggest_targets

DATA = Path(__file__).parent / "data" / "dziennik.json"
MEALS = ["Śniadanie", "II śniadanie", "Obiad", "Podwieczorek", "Kolacja"]


def load() -> dict:
    if DATA.exists():
        return json.loads(DATA.read_text(encoding="utf-8"))
    return {
        "entries": [],
        "customs": [],
        "goals": {"kcal": 2000, "protein": 120, "carbs": 220, "fat": 65},
    }


def save(state: dict) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def api_key() -> str:
    key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY") or ""
    try:
        key = key or st.secrets.get("XAI_API_KEY", "")
    except Exception:
        pass
    return key


def recognize(image_bytes: bytes, mime: str) -> dict:
    import base64
    import urllib.request

    key = api_key()
    if not key:
        return {"ok": False, "error": "Ustaw XAI_API_KEY, żeby rozpoznawać zdjęcia."}
    b64 = base64.b64encode(image_bytes).decode("ascii")
    prompt = (
        "Wskaż jedzenie na zdjęciu. Zwróć wyłącznie JSON "
        '{"summary":"...","items":[{"name":"...","grams":100,"kcalPer100":0,'
        '"proteinPer100":0,"carbsPer100":0,"fatPer100":0}]} '
        "Nazwy po polsku, maksymalnie 8 pozycji, wartości na 100 g."
    )
    body = json.dumps(
        {
            "model": "grok-4.5",
            "temperature": 0.2,
            "max_tokens": 900,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    ],
                }
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=45) as res:
        payload = json.loads(res.read().decode("utf-8"))
    text = payload["choices"][0]["message"]["content"]
    start, end = text.find("{"), text.rfind("}")
    return {"ok": True, **json.loads(text[start : end + 1])}


def main() -> None:
    st.set_page_config(page_title="Talerz", page_icon="🥗", layout="centered")
    st.title("Talerz")
    st.caption("Dziennik kalorii i makroskładników. Wartości są orientacyjne.")

    state = load()
    goals = state["goals"]
    day = st.date_input("Dzień", value=date.today())
    iso = day.isoformat()
    meal = st.selectbox("Posiłek", MEALS)

    tab_dziennik, tab_dodaj, tab_foto, tab_cele = st.tabs(["Dziennik", "Dodaj", "Zdjęcie", "Cele"])

    with tab_dodaj:
        query = st.text_input("Szukaj", placeholder="kurczak, ryż, jabłko")
        catalog = state["customs"] + FOODS
        hits = search_foods(query, catalog)[:12]
        names = [item["name"] for item in hits]
        if names:
            choice = st.selectbox("Produkt", names)
            food = next(item for item in hits if item["name"] == choice)
            grams = st.slider("Gramy", 10, 500, 100, 5)
            macros = from_per_100(food, grams)
            st.write(
                f"**{macros['kcal']} kcal** · białko {macros['protein']} g · "
                f"węgle {macros['carbs']} g · tłuszcz {macros['fat']} g"
            )
            if st.button("Dodaj do dziennika", type="primary"):
                state["entries"].insert(
                    0,
                    {"date": iso, "meal": meal, "name": food["name"], "grams": grams, **macros},
                )
                save(state)
                st.success(f"Dodano {food['name']}")
                st.rerun()
        with st.expander("Własny produkt (na 100 g)"):
            name = st.text_input("Nazwa")
            c1, c2, c3, c4 = st.columns(4)
            kcal = c1.number_input("kcal", 0, 900, 100)
            protein = c2.number_input("białko", 0.0, 100.0, 5.0)
            carbs = c3.number_input("węgle", 0.0, 100.0, 10.0)
            fat = c4.number_input("tłuszcz", 0.0, 100.0, 3.0)
            if st.button("Zapamiętaj") and name.strip():
                state["customs"].insert(
                    0,
                    {
                        "name": name.strip(),
                        "group": "Moje",
                        "kcal": kcal,
                        "protein": protein,
                        "carbs": carbs,
                        "fat": fat,
                    },
                )
                save(state)
                st.rerun()

    with tab_foto:
        photo = st.camera_input("Zrób zdjęcie") or st.file_uploader("albo wgraj plik", type=["jpg", "jpeg", "png", "webp"])
        if photo is not None and st.button("Rozpoznaj produkty"):
            try:
                result = recognize(photo.getvalue(), photo.type or "image/jpeg")
            except Exception as exc:
                st.error(f"Nie udało się rozpoznać zdjęcia: {exc}")
                result = None
            if result and not result.get("ok", True):
                st.error(result["error"])
            elif result:
                st.session_state["scan"] = result
        scan = st.session_state.get("scan")
        if scan:
            st.write(scan.get("summary", ""))
            picked = []
            for index, item in enumerate(scan.get("items") or []):
                grams = st.number_input(f"{item.get('name', 'Produkt')} — gramy", 5, 1500, int(item.get("grams") or 100), key=f"g{index}")
                macros = from_per_100(
                    {
                        "kcal": item.get("kcalPer100") or 0,
                        "protein": item.get("proteinPer100") or 0,
                        "carbs": item.get("carbsPer100") or 0,
                        "fat": item.get("fatPer100") or 0,
                    },
                    grams,
                )
                keep = st.checkbox(f"Dodaj: {macros['kcal']} kcal", value=True, key=f"k{index}")
                if keep:
                    picked.append({"date": iso, "meal": meal, "name": item.get("name") or "Produkt", "grams": grams, **macros})
            if picked and st.button("Zapisz rozpoznane"):
                state["entries"] = picked + state["entries"]
                save(state)
                st.session_state["scan"] = None
                st.success("Zapisano w dzienniku")
                st.rerun()

    with tab_cele:
        kcal = st.number_input("Cel kcal", 800, 6000, int(goals["kcal"]))
        protein = st.number_input("Białko g", 0, 400, int(goals["protein"]))
        carbs = st.number_input("Węglowodany g", 0, 800, int(goals["carbs"]))
        fat = st.number_input("Tłuszcz g", 0, 300, int(goals["fat"]))
        if st.button("Zapisz cele"):
            state["goals"] = {"kcal": kcal, "protein": protein, "carbs": carbs, "fat": fat}
            save(state)
            st.success("Zapisane")
        st.divider()
        st.caption("Szacunek startowy, nie porada medyczna.")
        sex = st.radio("Płeć do wzoru", ["k", "m"], format_func=lambda v: "Kobieta" if v == "k" else "Mężczyzna", horizontal=True)
        age = st.number_input("Wiek", 15, 90, 30)
        cm = st.number_input("Wzrost cm", 120, 230, 168)
        kg = st.number_input("Masa kg", 35, 250, 70)
        activity = st.selectbox("Aktywność", ["niska", "umiarkowana", "wysoka"])
        aim = st.selectbox("Kierunek", ["schudnac", "utrzymac", "przytyc"], format_func=lambda v: {"schudnac": "Jeść lżej", "utrzymac": "Utrzymać", "przytyc": "Jeść więcej"}[v])
        if st.button("Policz propozycję"):
            proposal = suggest_targets(sex, age, cm, kg, activity, aim)
            state["goals"] = proposal
            save(state)
            st.success(f"Propozycja: {proposal['kcal']} kcal")
            st.rerun()

    with tab_dziennik:
        rows = [row for row in state["entries"] if row["date"] == iso]
        eaten = {
            "kcal": sum(row["kcal"] for row in rows),
            "protein": round(sum(row["protein"] for row in rows), 1),
            "carbs": round(sum(row["carbs"] for row in rows), 1),
            "fat": round(sum(row["fat"] for row in rows), 1),
        }
        a, b, c, d = st.columns(4)
        a.metric("kcal", eaten["kcal"], f"cel {goals['kcal']}")
        b.metric("białko", eaten["protein"])
        c.metric("węgle", eaten["carbs"])
        d.metric("tłuszcz", eaten["fat"])
        if not rows:
            st.info("Ten dzień jest pusty. Dodaj produkt albo zrób zdjęcie.")
        for index, row in enumerate(rows):
            cols = st.columns([4, 1])
            cols[0].write(f"**{row['meal']}** · {row['name']} · {row['grams']} g · {row['kcal']} kcal")
            if cols[1].button("Usuń", key=f"del-{iso}-{index}-{row['name']}"):
                state["entries"].remove(row)
                save(state)
                st.rerun()

        st.subheader("Tydzień")
        labels, values = [], []
        for offset in range(6, -1, -1):
            current = date.today() - timedelta(days=offset)
            labels.append(current.strftime("%d.%m"))
            values.append(sum(row["kcal"] for row in state["entries"] if row["date"] == current.isoformat()))
        st.bar_chart({"kcal": values})
        st.caption(" · ".join(f"{label}: {value}" for label, value in zip(labels, values)))


if __name__ == "__main__":
    main()
