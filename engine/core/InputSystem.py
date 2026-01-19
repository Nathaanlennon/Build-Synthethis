import os
from engine.core.logging_setup import logger
import engine.core.ItemManager as ItemManager
from engine.core.CombatSystem import combat_system
from engine.core.DialogueSystem import dialogue_system
from engine.core.ItemManager import item_list_renderer, dealItem
from engine.core.ShopSystem import shop_manager


if os.path.exists("extensions/input_extensions.py") and os.path.isfile("extensions/input_extensions.py"):
    import extensions.input_extensions as input_ext
    charged = True
else:
    logger.warning(f"Module 'extension/input_extensions' is missing. please run setup_environment.py. from engine")
    charged = False


def exploration_input(universe, key):
    if key == "UP":
        universe.player.move(-1, 0)  # Déplacer vers le haut
        universe.player.orientation = "UP"
    elif key == "DOWN":
        universe.player.move(1, 0)   # Déplacer vers le bas
        universe.player.orientation = "DOWN"
    elif key == "LEFT":
        universe.player.move(0, -1)  # Déplacer vers la gauche
        universe.player.orientation = "LEFT"
    elif key == "RIGHT":
        universe.player.move(0, 1)   # Déplacer vers la droite
        universe.player.orientation = "RIGHT"
    elif key in hud:
        if key == "INVENTORY":
            ...
        universe.mode_change(key.lower())
    elif key == "QUIT":
        universe.save_save()
        exit()



    elif key == "INTERACT":
        ...

    universe.scenes[universe.current_world].event_system.update(universe.player, key)

def dialogue_input(universe, key):
    if dialogue_system.state == "TEXT_CHUNK":
        if dialogue_system.current_dialogue == "":
            if dialogue_system.as_choices():
                dialogue_system.state = "CHOICE"
                dialogue_system.set_choices()
            else:
                dialogue_system.state = "NEXT_LINE"

        if key == "INTERACT":
            ...
    elif dialogue_system.state == "CHOICE":
        if isinstance(key, int):  # renvoie d'un chiffre via le mapping
            if 1 <= key <= len(dialogue_system.choices):
                dialogue_system.set_next_line(choice_index=key - 1)

    elif dialogue_system.state == "NEXT_LINE":
        if key == "INTERACT":
            dialogue_system.set_next_line()

def inventory_input(universe, key):
    if not item_list_renderer.focused:
        if dealItem.mode != "use":
            if key == "TAB":
                if dealItem.mode == "buy":
                    dealItem.mode = "sell"
                    item_list_renderer.set_list(dealItem.inventory_a.items, "Inventory")
                else:
                    dealItem.mode = "buy"
                    item_list_renderer.set_list(shop_manager.current_shop_filtered_items, "Shop")
        if key == "INVENTORY" or key == "ESCAPE":
            universe.mode_change("exploration")
            dealItem.mode = "use"
            dealItem.inventory_a = universe.player.inventory
            item_list_renderer.set_list(universe.player.inventory.items)

        elif key == "RIGHT":
            item_list_renderer.current_index += 1
        elif key == "LEFT":
            # Prevent going below zero
            if item_list_renderer.current_index > 0:
                item_list_renderer.current_index -= 1

        else:
            if not dealItem.active:
                item = item_list_renderer.get_item(key)
                if item is not None:
                    item_list_renderer.focused = True
                    dealItem.set_up_item(item)
                    dealItem.active = True
    else:
        if key == 0:
            dealItem.active = False
            item_list_renderer.focused = False
        else:
            if dealItem.mode == "buy":
                universe.request_text_input(
                    dealItem.execute,
                    prompt="How many do you wanna buy : ",
                    input_type="int"
                )
            elif dealItem.mode == "sell":
                universe.request_text_input(
                    dealItem.execute,
                    prompt="How many do you wanna sell : ",
                    input_type="int"
                )
            elif dealItem.mode == "use":
                dealItem.execute()
def shop_input(universe, key):
    if key == "ESCAPE":
        universe.mode_change("exploration")
    elif key == "RIGHT":
        item_list_renderer.current_index += 1
    elif key == "LEFT":
        # Prevent going below zero
        if item_list_renderer.current_index > 0:
            item_list_renderer.current_index -= 1
    else:
        item = item_list_renderer.get_item(key)
        if item is not None:
            item_list_renderer.focused = True
            dealItem.setup_dealer(universe.player.inventory, None, "use", item)

def debug_input(universe, key):
    ...

def combat_input(universe, key):
    # Placeholder for combat input handling
    if combat_system.state == "START":
        if key == "INTERACT":
            combat_system.player_turn()
    elif combat_system.state == "PLAYER_TURN":
        if combat_system.queue:
            if combat_system.queue[0] == "PLAYER_CHOICE":
                if isinstance(key, int):
                    if key == 1:
                        combat_system.player_action["action"] = "attack"
                        combat_system.queue.pop(0)
                        combat_system.queue.insert(0, "CHOOSE_TARGET")
                    elif key == 2:
                        combat_system.queue.append("ABILITY_CHOICE")
                        combat_system.queue.pop(0)
                    elif key == 3:
                        combat_system.queue.append("ITEM_CHOICE")
                        combat_system.queue.pop(0)
            elif combat_system.queue[0] == "ABILITY_CHOICE":
                if isinstance(key, int):
                    if key == 0:
                        combat_system.queue.pop(0)
                        combat_system.queue.insert(0, "PLAYER_CHOICE")
                        return
                    abilities = list(universe.player.ext_data["abilities"].values())
                    if 1 <= key <= len(abilities):
                        combat_system.player_action["action"] = "ability"
                        combat_system.player_action["data"] = abilities[key - 1]
                        combat_system.queue.pop(0)
                        combat_system.queue.insert(0, "CHOOSE_TARGET")
            elif combat_system.queue[0] == "ITEM_CHOICE":
                if isinstance(key, int):
                    if key == 0:
                        combat_system.queue.pop(0)
                        combat_system.queue.insert(0, "PLAYER_CHOICE")
                        return
                    inventory_items = list(universe.player.inventory.items.keys())
                    if 1 <= key <= len(inventory_items):
                        if not universe.player.inventory.items[inventory_items[key - 1]]:
                            # If the item quantity is zero, ignore the choice
                            return
                        item_data = ItemManager.get_item(inventory_items[key - 1])
                        if item_data["type"] != "consumable":
                            # If the item is not usable in combat, ignore the choice
                            return
                        combat_system.player_action["action"] = "use_item"
                        combat_system.player_action["data"] = item_data
                        if "damage" in item_data["effect"]:
                            combat_system.queue.pop(0)
                            combat_system.queue.insert(0, "CHOOSE_TARGET")
                        else:
                            combat_system.queue.pop(0)
                            combat_system.execute_player_action()

            elif combat_system.queue[0] == "CHOOSE_TARGET":
                if isinstance(key, int):
                    if key == 0:
                        combat_system.queue.pop(0)
                        combat_system.queue.insert(0, "PLAYER_CHOICE")
                        return
                    if 1 <= key <= len(combat_system.fighters):
                        combat_system.player_action["target"] = combat_system.fighters[key - 1]
                        combat_system.queue.pop(0)
                        combat_system.execute_player_action()

            else:
                # In combat, any key press could advance the combat log
                combat_system.queue.pop(0)
        if not combat_system.queue:
            # If the queue is empty, proceed to the next round
            combat_system.enemies_turn()
    elif combat_system.state == "ENEMIES_TURN":
        # During enemies' turn, we can just wait for the turn to end
        if combat_system.queue:
            # In combat, any key press could advance the combat log
            combat_system.queue.pop(0)
        if not combat_system.queue:
            combat_system.new_round()
    elif combat_system.state == "VICTORY":
        if key == "INTERACT":
            combat_system.give_loot()
            combat_system.reset_combat()
            universe.mode_change("exploration")



modes = {
    "exploration": exploration_input,
    "dialogue": dialogue_input,
    "inventory": inventory_input,
    "shop": shop_input,
    "debug": debug_input,
    "combat": combat_input,
}

# hud is the input handler for the hud elements like inventory and things like that, to add more if needed
hud = {"INVENTORY", "DEBUG"}

if charged:
    modes.update(input_ext.input_modes)

