from engine.core.logging_setup import logger
import os
import json
import random
import engine.core.ItemManager as ItemManager


def load_enemies_list(file_path="assets/enemies/enemies.json"):
    """Charge les combattants depuis un fichier JSON. Retourne une liste vide si le fichier est absent ou invalide."""
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Erreur lors du chargement de {file_path} : {e}")
            return {}
    else:
        logger.warning(f"Fichier de combattants introuvable : {file_path}")
        return {}



class CombatSystem:
    def __init__(self, player):
        self.player = player
        self.enemies_list = load_enemies_list()
        self.fighters = []
        self.loot = []
        self.max_enemies = 3

        self.state = "START" # États possibles : START, PLAYER_TURN, ENEMIES_TURN, VICTORY, DEFEAT
        self.queue = []

        self.player_action = {
            "action" : "", # e.g. "attack", "ability", "use_item"
            "data" : None, # Détails supplémentaires sur l'action (ex: quelle capacité ou quel objet)
            "target" : None # L'ennemi ciblé par l'action du joueur
        }


    class Enemy:
        def __init__(self, combat_system, enemy_data):
            self.name = enemy_data.get("name", "Ennemi inconnu")
            self.id = enemy_data.get("id", "unknown_enemy")
            self.abilities = enemy_data.get("abilities", [])
            self.damage = enemy_data.get("damage", 0)
            self.defense = enemy_data.get("defense", 0)
            self.max_hp = enemy_data.get("hp", 10)
            self.hp = self.max_hp
            self.loot = enemy_data.get("loot", [])

            self.combat_system = combat_system


        def attack(self):
            if self.abilities:
                if random.randint(0,1):
                    attack = random.choice(self.abilities)
                    self.combat_system.queue.append('ATTACK: {} uses {}'.format(self.name, attack["name"]))
                    if random.randint(1, 100) <= attack["accuracy"] * 100:
                        return attack["damage"]
                    else:
                        self.combat_system.queue.append('MISS: {}\'s attack missed!'.format(self.name))
                        return 0
            return self.damage


        def death(self):
            """Gère la mort de l'ennemi."""
            for item, proba in self.loot.items():
                if random.random() <= proba:
                    self.combat_system.loot.append((item, 1))
            self.combat_system.remove_fighter(self)


    def add_fighter(self, fighter):
        """Ajoute un combattant à la liste des combattants en fonction de son ID.

            Args:
                fighter (str): L'ID du combattant à ajouter.
        """
        if fighter in self.enemies_list:
            self.fighters.append(self.Enemy(self, self.enemies_list[fighter]))
            return True
        else:
            logger.warning(f"Combattant inconnu de enemies.json : {fighter}")
            return False

    def remove_fighter(self, fighter):
        """Retire un combattant de la liste des combattants.

            Args:
                fighter (Enemy): L'instance du combattant à retirer.
        """
        if fighter in self.fighters:
            self.fighters.remove(fighter)

    def attack_target(self, attacker, target):
        """Effectue une attaque basique sur la cible."""

        attack_value = attacker.damage
        inv = getattr(attacker, "inventory", None)
        equip = getattr(inv, "equipment", {}) if inv else {}

        weapon_id = equip.get("weapon")
        if weapon_id:
            attack_value += ItemManager.get_item_part(weapon_id, "damages") or 0

        damage = random.randint(attack_value - 2, attack_value + 2)
        self.queue.append('ATTACK: {} hits {}'.format(attacker.name, target.name))
        self.receive_damage(target, damage)

    def receive_damage(self, target, damage):
        """Réduit les points de vie de l'ennemi."""
        # Liste des emplacements qui peuvent apporter de l'armure
        ARMOR_SLOTS = ["headgear", "chestplate", "leggings", "boots", "shield"]

        armor = target.defense

        inv = getattr(target, "inventory", None)
        equip = getattr(inv, "equipment", {}) if inv else {}

        # Additionne l'armure fournie par chaque pièce d'équipement
        for slot in ARMOR_SLOTS:
            item = equip.get(slot)
            if item:
                # get_item_part peut retourner None, donc fallback 0
                armor += ItemManager.get_item_part(item, "armor") or 0

        hit = max(0,damage - armor)
        target.hp -= hit
        if target.hp < 0:
            target.hp = 0
        self.queue.append('DAMAGE: {} takes {} damage'.format(target.name, hit))
        if target.hp <= 0:
            self.queue.append('DEATH: {} has been defeated'.format(target.name))
            target.death()

    def give_loot(self):
        """Donne le loot au joueur après le combat."""
        for item_id, quantity in self.loot:
            self.player.inventory.add_item(item_id, quantity)
        self.loot = []

    def player_turn(self):
        """Effectue le tour du joueur."""
        # Pour l'instant, le joueur attaque le premier ennemi dans la liste
        self.state="PLAYER_TURN"
        self.queue.append("PLAYER_CHOICE")

    def execute_player_action(self):
        if self.fighters and self.player_action["action"] is not None:
            if self.player_action["action"] == "attack":
                if self.player_action["target"] is not None:
                    if self.player_action["target"] in self.fighters:
                        self.attack_target(self.player, self.player_action["target"])
            elif self.player_action["action"] == "ability":
                ability = self.player_action["data"]
                self.queue.append('ATTACK: Player uses {}'.format(ability["name"]))
                damage = self.ability_use(ability)
                self.receive_damage(self.fighters[0], damage)
            elif self.player_action["action"] == "use_item":
                item = self.player_action["data"]
                self.use_object(self.player, obj=item, target=self.player_action.get("target", None))
        self.player_action = {
            "action" : "",
            "data" : None,
            "target" : None
        }
    def heal_target(self, target, amount):
        amount = min(amount, target.max_hp - target.hp)
        target.hp = min(target.max_hp, target.hp + amount)
        self.queue.append('{} heals {} HP'.format(target.name, amount))
    def use_object(self, user, obj, target = None):
        if obj["id"] in user.inventory.items:
            if target is None:
                target = self.player
            if obj["type"] == "consumable" and "effect" in obj:
                self.queue.append('{} uses {} on {}'.format(user.name, obj["name"], target.name))
                if "heal" in obj["effect"]:
                    self.heal_target(target, obj["effect"]["heal"])
                elif "damage" in obj["effect"]:
                    damage_amount = obj["effect"]["damage"]
                    self.receive_damage(target, damage_amount)
            user.inventory.remove_item(obj["id"], 1)

    def enemies_turn(self):
        """Effectue le tour des ennemis."""
        self.state="ENEMIES_TURN"
        if self.fighters:
            for fighter in self.fighters:
                if fighter.abilities:
                    if random.randint(0, 1):
                        attack = random.choice(fighter.abilities)
                        self.queue.append('ATTACK: {} uses {}'.format(fighter.name, attack["name"]))
                        self.receive_damage(self.player, self.ability_use(attack)+ random.randint(-2,2))
                    else:
                        self.attack_target(fighter, self.player)
        else:
            self.state="VICTORY"


    def ability_use(self, ability):
        if random.randint(1, 100) <= ability["accuracy"] * 100:
            return ability["damage"]
        else:
            self.queue.append('MISS: it missed!')
            return 0

    def new_round(self):
        """Démarre un nouveau round de combat."""
        if self.fighters:
            self.player_turn()
        else:
            self.state="VICTORY"

    def reset_combat(self):
        """Réinitialise le système de combat pour un nouveau combat."""
        self.fighters = []
        self.loot = []
        self.queue = []
        self.state = "START"
    def setup_combat(self, enemies):
        """

        :param enemies: couples list of ennemies and their probability to appear
        :return: None
        """
        i = 0 # counter of enemies added
        while not i:
            for enemy_id, prob in enemies:
                if random.random() <= prob:
                    if self.add_fighter(enemy_id):
                        i+= 1
                        if i >= self.max_enemies:
                            break


combat_system = CombatSystem(None)

def setup_combat_system(player):
    combat_system.player = player
