import json
import datetime
import requests
import os

def main():
    fetch_cards_using_static()
    convert_json_file("vtes.json", "VTES_Cards.json")
    delete_temp_files()

def fetch_cards_using_static():
    url = "https://static.krcg.org/data/vtes.json"
    save_path = "vtes.json"
    try:
        # Send GET request to the URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Write the content of the response to a local file
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully: {save_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def transform_card(source_card):
    card_sets = source_card.get("sets", {})
    card_id = str(source_card.get("id", ""))
    name = source_card.get("name", "").strip('"')
    card_types = source_card.get("types", [])
    clans = source_card.get("clans", [])
    disciplines_list = source_card.get("disciplines", [])
    ordered_sets = source_card.get("ordered_sets", [])
    scans = source_card.get("scans", {})
    blood_cost = source_card.get("blood_cost", "")
    pool_cost = source_card.get("pool_cost", "")
    capacity = check_capacity_value(source_card.get("capacity", 0))
    cost = blood_cost or pool_cost or capacity or 0
    banned_date = source_card.get("banned_date", "")
    standard_compatible = not bool(banned_date)

    v5_compatible = any(
        is_v5_compatible_item(item)
        for items in card_sets.values()
        for item in items
    )

    original_type = card_types[0] if card_types else ""
    is_vampire = "Vampire" in card_types
    front_type = "Crypt" if is_vampire else original_type
    clan = clans[0] if clans else ""
    group_raw = source_card.get("group", "0")
    try:
        group = int(group_raw)
    except (ValueError, TypeError):
        group = 0

    set_name = ordered_sets[0] if ordered_sets else ""
    disciplines = " ".join(disciplines_list) if disciplines_list else ""
    image_url = source_card.get("url", "")
    if not image_url and scans:
        image_url = next(iter(scans.values()), "")

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
        "clan": clan,
        "group": group,
        "set": set_name,
        "title": "",
        "cost": cost,
        "disciplines": disciplines,
        "_legal": {
            "STD": standard_compatible,
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

def convert_json_file(input_path, output_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        if not isinstance(source_data, list):
            raise ValueError("Source JSON must be a list of cards.")
        target_dict = {}
        for card in source_data:
            transformed = transform_card(card)
            target_dict[transformed["id"]] = transformed
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(target_dict, f, indent=2, ensure_ascii=False)
        print(f"Successfully converted {len(source_data)} cards to {output_path}")
    except FileNotFoundError:
        print(f"Error: File {input_path} not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {input_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

def to_json(dictionary, filename):
    with open(filename,'w') as fp:
        json.dump(dictionary, fp,sort_keys=True, indent=4,ensure_ascii=False)

def delete_temp_files():
    if os.path.exists("vtes.json"):
        os.remove("vtes.json")
    else:
        print("The file does not exist")

if __name__ == '__main__':
    main()
