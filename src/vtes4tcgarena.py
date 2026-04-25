import csv
import json
import datetime
import requests

krcg_static_url = "https://static.krcg.org/data/vtes.json"

def main():
    discipline_map = load_discipline_map("disciplines.csv")
    cards_data = fetch_cards_using_static()
    if cards_data:
        generate_cards_json(cards_data, "VTES_Cards.json", discipline_map)
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
    try:
        response = requests.get(krcg_static_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_cards_json(source_data, output_path, discipline_map):
    if not isinstance(source_data, list):
        raise ValueError("Source JSON must be a list of cards.")

    target_dict = {}
    for card in source_data:
        transformed = transform_card(card, discipline_map)
        target_dict[transformed["id"]] = transformed

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(target_dict, f, indent=2, ensure_ascii=False)

    print(f"Successfully converted {len(source_data)} cards to {output_path}")

def transform_card(source_card, discipline_map):
    return {
        "id": extract_id(source_card),
        "face": build_card_face(source_card),
        "name": extract_name(source_card),
        "type": extract_original_type(source_card),
        "capacity": extract_capacity(source_card),
        "clan": extract_clans(source_card),
        "group": extract_group(source_card),
        "set": extract_set_name(source_card),
        "title": extract_title(source_card),
        "cost": calculate_cost(source_card),
        "disciplines": transform_disciplines(source_card, discipline_map),
        "_legal": determine_legal_status(source_card)
    }

def extract_id(source_card):
    return str(source_card.get("id", ""))

def extract_name(source_card):
    return source_card.get("printed_name", "").strip('"')

def extract_original_type(source_card):
    card_types = source_card.get("types", [])
    return card_types[0] if card_types else ""

def extract_capacity(source_card):
    return check_capacity_value(source_card.get("capacity", 0))

def extract_clans(source_card):
    return source_card.get("clans", [])

def extract_group(source_card):
    group_raw = source_card.get("group", "0")
    try:
        return int(group_raw)
    except (ValueError, TypeError):
        return 0

def extract_set_name(source_card):
    ordered_sets = source_card.get("ordered_sets", [])
    return ordered_sets[0] if ordered_sets else ""

def extract_title(source_card):
    return source_card.get("title", "")

def calculate_cost(source_card):
    blood_cost = source_card.get("blood_cost", "")
    pool_cost = source_card.get("pool_cost", "")
    capacity = extract_capacity(source_card)
    return blood_cost or pool_cost or str(capacity) or "0"

def extract_image_url(source_card):
    image_url = source_card.get("url", "")
    if not image_url:
        scans = source_card.get("scans", {})
        image_url = next(iter(scans.values()), "")
    return image_url

def extract_card_type_info(source_card):
    card_types = source_card.get("types", [])
    original_type = card_types[0] if card_types else ""
    is_vampire = "Vampire" in card_types
    front_type = "Crypt" if is_vampire else original_type
    return {"original_type": original_type, "is_vampire": is_vampire, "front_type": front_type}

def build_card_face(source_card):
    type_info = extract_card_type_info(source_card)
    name = extract_name(source_card)
    cost = calculate_cost(source_card)
    image_url = extract_image_url(source_card)

    face = {
        "front": {
            "name": name,
            "type": type_info["front_type"],
            "cost": cost,
            "image": image_url,
            "isHorizontal": False
        },
        "back": None
    }

    if type_info["is_vampire"]:
        face["back"] = {
            "name": name,
            "type": "Crypt",
            "cost": cost,
            "image": "https://static.krcg.org/card/cardbackcrypt.jpg"
        }

    return face

def transform_disciplines(source_card, discipline_map):
    disciplines_list = source_card.get("disciplines", [])
    return [discipline_map.get(code, code) for code in disciplines_list]

def determine_legal_status(source_card):
    banned_date = source_card.get("banned", "")
    classic_compatible = not bool(banned_date)

    card_sets = source_card.get("sets", {})
    v5_compatible = any(
        is_v5_compatible_item(item)
        for items in card_sets.values()
        for item in items
    )

    if v5_compatible and not classic_compatible:
        v5_compatible = False

    return {"CLASSIC": classic_compatible, "V5": v5_compatible}

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

if __name__ == '__main__':
    main()
