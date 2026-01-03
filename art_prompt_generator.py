from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional


APP_NAME = "Draw Idea Generator (CLI)"
FAV_FILE = "favorites.json"


THEMES = ["любой", "фэнтези", "sci-fi", "бытовое", "хоррор"]


# Наборы по темам: где нет явной тематической привязки, кладём в "любой".
POOLS: Dict[str, Dict[str, List[str]]] = {
    "любой": {
        "персонаж": [
            "уставший маг", "хитрая лиса-алхимик", "космический курьер", "робот-няня",
            "странствующий музыкант", "детектив", "техномонах", "кулинар-экспериментатор",
            "художник-иллюзионист", "пилот дирижабля", "школьница с секретом", "потерявшийся турист",
        ],
        "действие": [
            "ищет потерянный артефакт", "чинит странный механизм", "впервые использует новую силу",
            "прячется от преследователей", "готовит зелье", "пишет письмо, которое нельзя отправить",
            "спорит с отражением", "спасает маленькое существо", "делает выбор между долгом и мечтой",
            "пытается не засмеяться в серьёзной ситуации", "обнаруживает тайную комнату",
        ],
        "окружение": [
            "на крыше высокого здания", "в заброшенной библиотеке", "в шумном ночном рынке",
            "в туманном лесу", "в маленькой мастерской", "на вокзале под дождём",
            "в пустыне у одинокой вышки", "в подземном метро", "в старом театре",
            "у моря на рассвете", "в комнате, где время остановилось",
        ],
        "стиль": [
            "аниме", "реализм", "полуреализм", "комикс", "пиксель-арт", "акварель",
            "тушь/лайн", "минимализм", "low-poly", "ч/б графика", "скетч карандашом",
        ],
        "настроение": [
            "спокойное", "меланхоличное", "напряжённое", "уютное", "праздничное",
            "таинственное", "комедийное", "мечтательное", "тревожное", "торжественное",
        ],
        "ограничение": [
            "только 3 цвета", "без линий (только пятна)", "10 минут на скетч",
            "один источник света", "без лица (показать эмоцию позой)", "только силуэты",
            "вид сверху", "одна деталь должна быть красной", "максимум 30 штрихов",
        ],
        "деталь": [
            "у персонажа необычные перчатки", "рядом странная табличка", "на фоне заметен символ",
            "есть питомец-компаньон", "в кадре зеркало/отражение", "на одежде нашивка",
            "в воздухе летят бумажки", "на столе загадочный чертёж", "в углу прячется кот",
        ],
    },

    "фэнтези": {
        "персонаж": ["ведьма", "рыцарь", "эльф-разведчик", "дракончик-воришка", "алхимик"],
        "окружение": ["в руинах храма", "в таверне у камина", "на мосту над пропастью", "у древнего дерева"],
        "деталь": ["магические руны светятся", "меч треснул, но держится", "фляга с зельем кипит"],
    },

    "sci-fi": {
        "персонаж": ["кибер-ниндзя", "инженер станции", "андроид", "навигатор корабля", "охотник за дронами"],
        "окружение": ["в коридоре космостанции", "на пыльной луне", "в неоновом переулке", "в кабине меха"],
        "деталь": ["на шлеме трещина", "провода торчат наружу", "голограмма мерцает"],
    },

    "бытовое": {
        "персонаж": ["бариста", "студент", "доставщик еды", "музыкант на улице", "девушка с блокнотом"],
        "окружение": ["в маленьком кафе", "на остановке", "в библиотеке", "на кухне ночью", "в парке"],
        "деталь": ["на столе недопитый чай", "кот залез на сумку", "на стене смешной плакат"],
    },

    "хоррор": {
        "персонаж": ["ночной сторож", "исследователь", "человек в плаще", "кукла", "пациент"],
        "окружение": ["в пустой больнице", "в коридоре с мигающей лампой", "в доме на окраине", "в тоннеле"],
        "настроение": ["тревожное", "пугающе-тихое", "паранойяльное", "гнетущее"],
        "деталь": ["вдалеке слышны шаги", "на стене царапины", "дверь приоткрыта"],
    },
}


@dataclass
class Options:
    theme: str = "любой"
    mode: str = "стандарт"  # быстрый скетч / стандарт / челлендж
    include_style: bool = True
    include_mood: bool = True
    include_constraint: bool = False
    include_detail: bool = True


def load_favorites(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return []


def save_favorites(path: str, favorites: List[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)


def merged_pool(theme: str) -> Dict[str, List[str]]:
    """Склеиваем 'любой' + выбранная тема (если не 'любой')."""
    base = POOLS["любой"]
    if theme == "любой":
        return base

    themed = POOLS.get(theme, {})
    out: Dict[str, List[str]] = {}
    keys = set(base.keys()) | set(themed.keys())
    for k in keys:
        out[k] = list(base.get(k, [])) + list(themed.get(k, []))
    return out


def pick(pool: Dict[str, List[str]], key: str) -> Optional[str]:
    items = pool.get(key, [])
    return random.choice(items) if items else None


def generate_prompt(opt: Options) -> str:
    pool = merged_pool(opt.theme)

    character = pick(pool, "персонаж") or "кто-то"
    action = pick(pool, "действие") or "делает что-то странное"
    place = pick(pool, "окружение") or "в неизвестном месте"

    parts = [f"{character} {action} {place}"]

    if opt.include_style:
        style = pick(pool, "стиль")
        if style:
            parts.append(f"стиль: {style}")

    if opt.include_mood:
        mood = pick(pool, "настроение")
        if mood:
            parts.append(f"настроение: {mood}")

    if opt.include_detail:
        detail = pick(pool, "деталь")
        if detail:
            parts.append(f"деталь: {detail}")

    if opt.include_constraint:
        constraint = pick(pool, "ограничение")
        if constraint:
            parts.append(f"ограничение: {constraint}")

    # Режим влияет на “нагрузку”
    if opt.mode == "быстрый скетч":
        # Упростим: уберём ограничение и оставим максимум 1 доп. параметр
        core = parts[0]
        extras = []
        # берём либо стиль, либо настроение
        if opt.include_style and len(parts) > 1 and "стиль:" in parts[1]:
            extras.append(parts[1])
        elif opt.include_mood:
            for p in parts[1:]:
                if p.startswith("настроение:"):
                    extras.append(p)
                    break
        return core + ("; " + ", ".join(extras) if extras else "")

    if opt.mode == "челлендж":
        # Добавим обязательное ограничение и деталь
        if "ограничение:" not in " | ".join(parts):
            constraint = pick(pool, "ограничение")
            if constraint:
                parts.append(f"ограничение: {constraint}")
        if "деталь:" not in " | ".join(parts):
            detail = pick(pool, "деталь")
            if detail:
                parts.append(f"деталь: {detail}")

    return "; ".join(parts)


def daily_seed() -> int:
    """Сид дня: чтобы 'идея дня' была стабильна в пределах даты."""
    today = date.today().isoformat()
    return sum(ord(c) for c in today)


def print_header() -> None:
    print("=" * 52)
    print(APP_NAME)
    print("=" * 52)
    print("Мяу")  # важный системный компонент вселенной
    print()


def choose_theme(opt: Options) -> None:
    print("Выбери тему:")
    for i, t in enumerate(THEMES, start=1):
        mark = " (текущая)" if t == opt.theme else ""
        print(f"  {i}. {t}{mark}")
    s = input("Номер: ").strip()
    if s.isdigit():
        idx = int(s) - 1
        if 0 <= idx < len(THEMES):
            opt.theme = THEMES[idx]
    print(f"Тема: {opt.theme}\n")


def choose_mode(opt: Options) -> None:
    modes = ["быстрый скетч", "стандарт", "челлендж"]
    print("Выбери режим:")
    for i, m in enumerate(modes, start=1):
        mark = " (текущий)" if m == opt.mode else ""
        print(f"  {i}. {m}{mark}")
    s = input("Номер: ").strip()
    if s.isdigit():
        idx = int(s) - 1
        if 0 <= idx < len(modes):
            opt.mode = modes[idx]
    print(f"Режим: {opt.mode}\n")


def toggle_settings(opt: Options) -> None:
    while True:
        print("Настройки генерации (вкл/выкл):")
        print(f"  1. стиль:        {'да' if opt.include_style else 'нет'}")
        print(f"  2. настроение:   {'да' if opt.include_mood else 'нет'}")
        print(f"  3. ограничение:  {'да' if opt.include_constraint else 'нет'}")
        print(f"  4. деталь:       {'да' if opt.include_detail else 'нет'}")
        print("  0. назад")
        s = input("Выбор: ").strip()

        if s == "0":
            print()
            return
        if s == "1":
            opt.include_style = not opt.include_style
        elif s == "2":
            opt.include_mood = not opt.include_mood
        elif s == "3":
            opt.include_constraint = not opt.include_constraint
        elif s == "4":
            opt.include_detail = not opt.include_detail
        print()


def show_favorites(favorites: List[dict]) -> None:
    if not favorites:
        print("Избранное пустое. Как и многие обещания людей.\n")
        return
    print("Избранное:")
    for i, item in enumerate(favorites, start=1):
        print(f"{i}. [{item.get('theme','?')}/{item.get('mode','?')}] {item.get('prompt','')}")
    print()


def main() -> None:
    random.seed()  # системный сид
    opt = Options()
    favorites = load_favorites(FAV_FILE)

    print_header()

    last_prompt: Optional[str] = None

    while True:
        print("Меню:")
        print("  1) Сгенерировать идею")
        print("  2) Идея дня (стабильная на сегодня)")
        print("  3) Выбрать тему")
        print("  4) Выбрать режим")
        print("  5) Настройки (что включать)")
        print("  6) Сохранить последнюю идею в избранное")
        print("  7) Показать избранное")
        print("  8) Очистить избранное")
        print("  0) Выход")

        choice = input("Выбор: ").strip()
        print()

        if choice == "0":
            print("Выход. Иди рисуй, а не собирай меню, мяу.")
            break

        elif choice == "1":
            last_prompt = generate_prompt(opt)
            print("Твоя идея:")
            print(f"  {last_prompt}\n")

        elif choice == "2":
            # Идея дня: фиксируем seed на дату, затем возвращаем назад
            state = random.getstate()
            random.seed(daily_seed())
            last_prompt = generate_prompt(opt)
            random.setstate(state)

            print("Идея дня:")
            print(f"  {last_prompt}\n")

        elif choice == "3":
            choose_theme(opt)

        elif choice == "4":
            choose_mode(opt)

        elif choice == "5":
            toggle_settings(opt)

        elif choice == "6":
            if not last_prompt:
                print("Сначала сгенерируй идею. Магии из пустоты тут нет.\n")
                continue
            favorites.append({
                "prompt": last_prompt,
                "theme": opt.theme,
                "mode": opt.mode,
            })
            save_favorites(FAV_FILE, favorites)
            print("Сохранено в избранное.\n")

        elif choice == "7":
            show_favorites(favorites)

        elif choice == "8":
            confirm = input("Точно очистить избранное? (да/нет): ").strip().lower()
            if confirm in ("да", "d", "yes", "y"):
                favorites = []
                save_favorites(FAV_FILE, favorites)
                print("Избранное очищено.\n")
            else:
                print("Оставили. Наконец-то хоть где-то стабильность.\n")

        else:
            print("Не понял выбор. Попробуй ещё раз.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nОк, Ctrl+C. Тоже выход. Мяу.")
