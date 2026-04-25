import csv
import json
import datetime
import requests

def main():
    discipline_map = load_discipline_map("disciplines.csv")
    cards_data = fetch_cards_using_static()
    if cards_data:
        convert_json_from_memory(cards_data, "VTES_Cards.json", discipline_map)
    else:
        print("Failed to fetch cards. Exiting.")

def load_discipline_map(path):
    discipline_map = {}
    try:
        with open(path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                code = row.get("code", "").strip().lower()
                name = row.get("name", "").strip()
                if code and name:
                    discipline_map[code] = name
        print(f"Loaded {len(discipline_map)} disciplines")
        return discipline_map
    except FileNotFoundError:
        print(f"Disciplines map file not found: {path}. Using raw codes")
        return {}

def fetch_cards_using_static():
    url = "https://static.krcg.org/data/vtes.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def transform_card(source_card, discipline_map):
    card_id = str(source_card.get("id", ""))
    name = source_card.get("printed_name", "").strip('"')

    card_types = source_card.get("types", [])
    original_type = card_types[0] if card_types else ""
    is_vampire = "Vampire" in card_types
    front_type = "Crypt" if is_vampire else original_type

    blood_cost = source_card.get("blood_cost", "")
    pool_cost = source_card.get("pool_cost", "")
    capacity = check_capacity_value(source_card.get("capacity", 0))
    cost = blood_cost or pool_cost or capacity or 0

    scans = source_card.get("scans", {})
    image_url = source_card.get("url", "")
    if not image_url and scans:
        image_url = next(iter(scans.values()), "")

    clans = source_card.get("clans", [])
    group_raw = source_card.get("group", "0")
    try:
        group = int(group_raw)
    except (ValueError, TypeError):
        group = 0

    card_sets = source_card.get("sets", {})
    ordered_sets = source_card.get("ordered_sets", [])
    set_name = ordered_sets[0] if ordered_sets else ""

    title = source_card.get("title", "")

    disciplines_list = source_card.get("disciplines", [])
    reformatted_disciplines = []
    for code in disciplines_list:
        full_name = discipline_map.get(code, code)
        reformatted_disciplines.append(full_name)

    banned_date = source_card.get("banned", "")
    classic_compatible = not bool(banned_date)
    v5_compatible = any(
        is_v5_compatible_item(item)
        for items in card_sets.values()
        for item in items
    )
    if v5_compatible and not classic_compatible:
        v5_compatible = False


    back_face = None
    if is_vampire:
        back_face = {
            "name": name,
            "type": "Crypt",
            "cost": cost,
            "image": "https://static.krcg.org/card/cardbackcrypt.jpg"
        }

    target_card = {
        "id": card_id,
        "face": {
            "front": {
                "name": name,
                "type": front_type,
                "cost": cost,
                "image": image_url,
                "isHorizontal": False
            },
            "back": back_face
        },
        "name": name,
        "type": original_type,
        "capacity": capacity,
        "clan": clans,
        "group": group,
        "set": set_name,
        "title": title,
        "cost": cost,
        "disciplines": reformatted_disciplines,
        "_legal": {
            "CLASSIC": classic_compatible,
            "V5": v5_compatible
        }
    }
    return target_card

def check_capacity_value(capacity):
    if isinstance(capacity, str):
        try:
            capacity = int(capacity)
        except ValueError:
            capacity = 0
    return capacity

def is_v5_compatible_item(item):
    v5_release_date = datetime.date.fromisoformat("2020-11-01")
    if "release_date" not in item:
        return False
    try:
        return datetime.date.fromisoformat(item["release_date"]) > v5_release_date
    except (ValueError, TypeError):
        return False


def convert_json_from_memory(source_data, output_path, discipline_map):
    if not isinstance(source_data, list):
        raise ValueError("Source JSON must be a list of cards.")

    target_dict = {}
    for card in source_data:
        transformed = transform_card(card, discipline_map)
        target_dict[transformed["id"]] = transformed

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(target_dict, f, indent=2, ensure_ascii=False)

    print(f"Successfully converted {len(source_data)} cards to {output_path}")

if __name__ == '__main__':
    main()
