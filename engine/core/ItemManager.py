from engine.core.logging_setup import logger
import os
import json


def load_items(file_path="assets/items/items.json"):
    """Charge les items depuis un fichier JSON. Retourne un dict vide si le fichier est absent ou invalide."""
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Erreur lors du chargement de {file_path} : {e}")
            return {}
    else:
        logger.warning(f"Fichier d'items introuvable : {file_path}")
        return {}


items = load_items()

def get_item(item) -> dict:
    """Récupère un item par son ID. Retourne un placeholder si absent et log l'erreur."""
    if item not in items:
        logger.warning(f"Item '{item}' introuvable dans la base de données d'items.")
        return {
            "name": "Objet inconnu",
            "description": "Cet objet n'existe pas ou n'est pas encore défini.",
        }
    return items[item]
def get_item_part(item, part): # part is like price, name, description -> any:
    """Récupère une partie spécifique d'un item par son ID. Retourne None si absent et log l'erreur."""
    if item not in items:
        return None
    return items[item].get(part, None)

class ItemsListRenderer:
    def __init__(self):
        self.max_items_per_page = 0
        self.items = {} # Liste des items dans la scène
        self.items_ids = []
        self.pages = []
        self.focused = False
        self.current_index = 0
        self.name = ""

    def get_item(self, key):
        # Accept int or single-char str: '0'-'9' -> 0-9, 'a'-'z'/'A'-'Z' -> 10-35 (base36-like)
        if not self.items_ids:
            return None
        idx = None
        if isinstance(key, int):
            idx = key
        elif isinstance(key, str) and len(key) == 1:
            if '0' <= key <= '9':
                idx = ord(key) - ord('0')
            else:
                k = key.lower()
                if 'a' <= k <= 'z':
                    idx = ord(k) - ord('a') + 10
        if idx is None:
            return None
        idx = idx + self.max_items_per_page * self.current_index -1
        return self.items_ids[idx] if 0 <= idx < len(self.items) else None

    def set_list(self, items, name= "Inventory"):
        self.items = {}
        self.items_ids = []
        for k, v in items.items():
            self.items[k] = v
            self.items_ids.append(k)
        self.current_index = 0
        self.name = name


item_list_renderer = ItemsListRenderer()

class Inventory:
    def __init__(self, money = 0):
        self.items = {}  # dict of item_id: quantity
        self.money = money
        self.name = "Inventory"
        self.equipment = {
            "headgear": "",
            "chestplate": "",
            "leggings": "",
            "boots": "",
            "weapon": "",
            "shield": "",
            "special": ""
        }

    def add_item(self, item_id, quantity=1):
        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity

    def remove_item(self, item_id, quantity=1):
        if item_id in self.items:
            if isinstance(self.items[item_id], int):
                self.items[item_id] -= quantity
                if self.items[item_id] <= 0:
                    del self.items[item_id]
            elif isinstance(self.items[item_id], dict):
                if self.items[item_id]["quantity"] != "infinite":
                    self.items[item_id]["quantity"] -= quantity
                    if self.items[item_id] <= 0:
                        del self.items[item_id]

    def get_quantity(self, item_id):
        item = self.items.get(item_id, 0)
        return item["quantity"] if isinstance(item, dict) else item

    # i need to make a method that will export a list of the items and their quantities as a dictionary
    def get_list(self):
        item_list = {}
        for item_id, data in self.items.items():
            item_list[item_id] = data["quantity"] if isinstance(data, dict) else data
        return item_list

    def export_data(self):
        data = {}
        for k, v in self.__dict__.items():
            data[k] = v
        return data
    def load_data(self, data):
        self.items = data.get("items", {})
        self.money = data.get("money", 0)
        self.name = data.get("name", "Inventory")
        self.equipment = data.get("equipment", {
            "headgear": "",
            "chestplate": "",
            "leggings": "",
            "boots": "",
            "weapon": "",
            "shield": "",
            "special": ""
        })

class DealItem:
    def __init__(self, item_id = None, inventory_a=None, inventory_b=None, mode="use"):
        # sell will be from inventory_a to inventory_b ; buy will be from inventory_b to inventory_a
        self.item_id = item_id
        self.inventory_a = inventory_a  # e.g., player's inventory most of the time ; we will suppose that iventory_a as not an "infinite" money
        self.inventory_b = inventory_b  # e.g., shop's inventory most of the time but can be a chest fo exemple
        self.mode = mode  # e.g., "sell", "buy"
        self.item_data = get_item(item_id)
        self.active = False

    def execute(self, input=1):
        if self.mode == "sell":
            if self.inventory_b.money == "infinite" or self.inventory_b.money >= self.item_data.get("price", 0) * input:
                if self.inventory_a.get_quantity(self.item_id) >= input:
                    self.inventory_a.remove_item(self.item_id, input)
                    if self.inventory_b.money != "infinite":
                        self.inventory_b.add_item(self.item_id, input)
                        self.inventory_b.money -= self.item_data.get("price", 0) * input
                    self.inventory_a.money += self.item_data.get("price", 0) * input

        elif self.mode == "buy":
            if self.inventory_a.money >= self.item_data.get("price", 0) * input:
                if self.inventory_b.get_quantity(self.item_id) == "infinite" or self.inventory_b.get_quantity(self.item_id) >= input:
                    if self.inventory_b != "infinite":
                        self.inventory_b.remove_item(self.item_id, input)
                    self.inventory_a.add_item(self.item_id, input)
                    self.inventory_a.money -= self.item_data.get("price", 0) * input
        elif self.mode == "use":
            if self.inventory_a.get_quantity(self.item_id):
                item_type = get_item_part(self.item_id, "type")
                if item_type == "equipment":
                    slot = get_item_part(self.item_id, "position")
                    self.inventory_a.equipment[slot] = self.item_id
                # For other item types, implement their effects here
                elif item_type == "consumable":
                    ...


        self.active=False
    def set_up_item(self, item_id):
        self.item_id = item_id
        self.item_data = get_item(item_id)

    def setup_dealer(self, inventory_a, inventory_b = None, mode = "use", item = None):
        self.inventory_a = inventory_a
        self.inventory_b = inventory_b
        self.mode = mode
        if item is not None:
            self.set_up_item(item)
dealItem = DealItem()
