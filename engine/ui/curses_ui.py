import curses
import os
from engine.core.logging_setup import logger
from engine.core.ItemManager import item_list_renderer, get_item, dealItem, get_item_part
from engine.core.CombatSystem import combat_system
from engine.core.DialogueSystem import dialogue_system
from engine.core.ShopSystem import shop_manager

if os.path.exists("extensions/ui_extensions.py") and os.path.isfile("extensions/ui_extensions.py"):
    import extensions.ui_extensions as ui_ext

    charged = True
else:
    logger.warning(f"Module 'extensions/ui_extensions' is missing. Please run setup_environment.py in the engine")
    charged = False

curses.initscr()

# Table de correspondance Unicode -> curses ACS
CHAR_MAP = {
    '£': '' # when a caracter takes 2 spaces, it fucks the rendering and the collisions so £ create a collision for the remaining space and the '' makes the space invisible. Please add £ after any 2 space taking caracter in your maps
}

# mapping global, créé une seule fois
KEY_MAPPING = {
    ord('Z'): "UP", ord('z'): "UP",
    ord('S'): "DOWN", ord('s'): "DOWN",
    ord('Q'): "LEFT", ord('q'): "LEFT",
    ord('D'): "RIGHT", ord('d'): "RIGHT",
    ord('E'): "INTERACT", ord('e'): "INTERACT",
    27: "ESCAPE",  # ESCAPE key
    ord('X'): "QUIT", ord('x'): "QUIT",
    ord('W'): "DEBUG", ord('w'): "DEBUG",
    ord('I'): "INVENTORY", ord('i'): "INVENTORY",
    curses.KEY_UP: "UP",
    curses.KEY_DOWN: "DOWN",
    curses.KEY_LEFT: "LEFT",
    curses.KEY_RIGHT: "RIGHT",
    9: "TAB",
}
HUD_ACTIONS = {"INVENTORY", "QUIT", "DEBUG"}
HUD_KEYS = {}
for k, v in KEY_MAPPING.items():
    if v in HUD_ACTIONS and v not in HUD_KEYS.values():
        HUD_KEYS[k] = v

# chiffres 0-9 → renvoie directement l'entier
for i in range(10):
    KEY_MAPPING[ord(str(i))] = i


def key_to_action(key):
    return KEY_MAPPING.get(key, key)




# modes de "gameplay"

def exploration_mode(self, stdscr):
    self.show_scene(stdscr)
    self.draw_player(stdscr)
    self.draw_entities(stdscr)
    # self.draw_events(stdscr) # events dont have sprite for now
    self.draw_hud(stdscr)

def dialogue_mode(self, stdscr):
    if dialogue_system.current_dialogue:
        dialogue_system.current_say = self. get_dialogue_segment(((self.screens["hud"]["size"][0]-1)//2), self.screens["hud"]["size"][1]-2)
        self.draw_dialogue_lines(stdscr, "hud", 1, 1, dialogue_system.current_say)
    if dialogue_system.state == "CHOICE":
        self.draw_dialogue_lines(stdscr, "hud",1,1, dialogue_system.current_say)

        for idx, choice in enumerate(dialogue_system.choices):
            self.draw(stdscr, "hud", idx + self.screens["hud"]["size"][0]//2, 1, f"{idx + 1}. {choice}")
    sprite, (max_x, max_y) = self.load_sprite("assets/sprites/{}.txt".format(dialogue_system.speaker))
    self.draw_sprite("scene",sprite, self.screens["scene"]["size"][0]-max_y-1, (self.screens["scene"]["size"][1]-max_x)//2, stdscr)



def inventory_mode(self, stdscr):
    if not item_list_renderer.focused:
        self.render_item_list(stdscr, "hud", f"[{item_list_renderer.name}]")
        if dealItem.mode != "use":
            self.draw(stdscr, "hud", self.screens["hud"]["size"][0]-2, 1, "TAB to switch")
            money = 'ထ ' if shop_manager.current_shop.money == 'infinite' else shop_manager.current_shop.money
            self.draw(stdscr, "hud", self.screens["hud"]["size"][0]-2, self.screens["hud"]["size"][1]- 22, f"Shop money : {money} G")

        # equiped and shit :
        # show everything equiped, so the key and the name of the value, from player.inventory
        self.draw(stdscr, "scene", 1,1, "[equipement]")
        idx = 0
        for key, value in self.universe.player.inventory.equipment.items():
            self.draw(stdscr, "scene", 2+idx, 1, f"{key} : {value}")
            idx += 1

        # stats :
        self.draw(stdscr, "scene", 1, self.screens["scene"]["size"][1]//2, "[Stats]")
        self.draw(stdscr, "scene", 2, self.screens["scene"]["size"][1]//2, f"HP : {self.universe.player.hp}")
        self.draw(stdscr, "scene", 3, self.screens["scene"]["size"][1]//2, f"Money : {self.universe.player.inventory.money}")



    else:
        self.draw_item_detail(stdscr, "scene", dealItem.item_id)
        if dealItem.mode == "use":
            self.draw_button(stdscr, "hud", 1, 1, "0 : Back")
            type = get_item_part(dealItem.item_id, "type")
            if type == "consumable":
                self.draw_button(stdscr, "hud", 4, 1, "1 : Use Item")
            elif type == "equipment":
                self.draw_button(stdscr, "hud", 4, 1, "1 : Equip Item")
        elif dealItem.mode == "buy":
            self.draw_button(stdscr, "hud", 1, 1, "0 : Back")
            self.draw_button(stdscr, "hud", 4, 1, f"1 : Buy Item for {get_item_part(dealItem.item_id, 'price')} G")
        elif dealItem.mode == "sell":
            self.draw_button(stdscr, "hud", 1, 1, "0 : Back")
            self.draw_button(stdscr, "hud", 4, 1, f"1 : Sell Item for {get_item_part(dealItem.item_id, 'price')} G")




def shop_mode(self, stdscr):
    self.render_item_list(stdscr, "hud", "[Shop]")


def combat_mode(self, stdscr):
    # TODO: changer la variable là qui se fait à chaque itération, ça sert à rien bordel
    self.draw(stdscr, "hud", 0, 0, "COMBAT MODE")
    nb_enemies = len(combat_system.fighters)
    for idx, enemy in enumerate(combat_system.fighters):
        enemy_sprite, (max_x, max_y) = self.load_sprite("assets/sprites/{}.txt".format(enemy.id))
        x = 1 + (idx + 1) * (self.universe.size[1] - 2) // (nb_enemies + 1) - max_x // 2
        y = (self.universe.size[0] - 1) // 2 - max_y - 2
        self.draw(stdscr, "scene", (self.universe.size[0] - 1) // 2 - 2, x, f"{enemy.name}")
        self.draw(stdscr, "scene", (self.universe.size[0] - 1) // 2 - 1, x, f"{enemy.hp}/{enemy.max_hp}")

        self.draw_sprite("scene",enemy_sprite, y, x, stdscr)

    self.draw(stdscr, "hud", 1, 1, "Player HP: {}".format(self.universe.player.hp))

    q0 = combat_system.queue[0] if combat_system.queue else ""

    if combat_system.state == "START":
        self.draw(stdscr, "hud", 1, 1, "A wild enemy appears!")
    elif combat_system.state == "PLAYER_TURN":
        if q0 == "PLAYER_CHOICE":
            self.draw(stdscr, "hud", 1 + 1, 1, "Choose your action:")
            self.draw_button(stdscr, "hud", 1 + 1 + 1, 1, "1. Attack")
            self.draw_button(stdscr, "hud", 1 + 2 + 2+1, 1, "2. Ability")
            self.draw_button(stdscr, "hud", 1 + 2 + 4+2, 1, "3. Use Item")
        elif q0 == "ABILITY_CHOICE":
            self.draw(stdscr, "hud", 1 + 1, 1, "Choose your ability:")
            self.draw(stdscr, "hud", 1 + 1 + 1, 1, "0. Back")
            for idx, ability in enumerate(self.universe.player.ext_data["abilities"].values()):
                self.draw(stdscr, "hud", 1 + 1 + 2 + idx, 1, f"{idx + 1}. {ability['name']}")
        elif q0 == "ITEM_CHOICE":
            self.draw(stdscr, "hud", 1 + 1, 1, "Choose your item:")
            self.draw(stdscr, "hud", 1 + 1 + 1, 1, "0. Back")
            inventory_items = list(self.universe.player.inventory.items.keys())
            for idx, item_name in enumerate(inventory_items):
                item_data = get_item(item_name)
                quantity = self.universe.player.inventory.items[item_name]
                if quantity > 0 and item_data["type"] == "consumable":
                    self.draw(stdscr, "hud", 1 + 2 + 1 + idx, 1, f"{idx + 1}. {item_data['name']} x{quantity}")
        elif q0 == "CHOOSE_TARGET":
            self.draw(stdscr, "hud", 1 + 1, 1, "Choose your target:")
            self.draw(stdscr, "hud", 1 + 1 + 1, 1, "0. Back")
            for idx, enemy in enumerate(combat_system.fighters):
                self.draw(stdscr, "hud", 1 + 2 + 1 + idx, 1, f"{idx + 1}. {enemy.name}")
        elif q0:
            self.draw(stdscr, "hud", 1 + 1, 1, q0)


    elif combat_system.state == "ENEMIES_TURN" and q0:
        self.draw(stdscr, "hud", 1 + 1, 1, q0)
    elif combat_system.state == "VICTORY":
        self.draw(stdscr, "hud", 1 + 1 + 2, 1, "You won the combat!")
        self.draw(stdscr, "hud", 1 + 1 + 3, 1, "Loot:")
        for idx, (item_id, quantity) in enumerate(combat_system.loot):
            item = get_item(item_id)
            self.draw(stdscr, "hud", 1 + 1 + 4 + idx, 1, f"{item['name']} x{quantity}")

def debug_mode(self, stdscr):
    exploration_mode(self, stdscr)
    self.draw(stdscr, "hud", 1, 1 + self.screens["hud"]["size"][1] - 12, "DEBUG MODE")



class CursesUI:
    def __init__(self, universe):
        self.universe = universe
        self.modes = {
            "exploration": exploration_mode,
            "dialogue": dialogue_mode,
            "inventory": inventory_mode,
            "debug": debug_mode,
            "combat": combat_mode,
            "shop": shop_mode
        }
        self.cursor = (0, 0)

        # the area for screen, the border is inculded
        self.screens = {
            "scene": {
                "position": (0, 0),
                "size": (universe.size[0] // 2, universe.size[1]),
            },
            "hud": {
                "position": (universe.size[0] - universe.size[0] // 2, 0),
                "size": (universe.size[0] // 2, universe.size[1]),
            }
        }



        if charged:
            self.modes.update(ui_ext.ui_modes)

        self.mode_draw_function = self.modes[universe.mode]
        self.universe.set_mode_change_callback(self.change_mode)

        self.input_wanted = False
        self.input_buffer = ""
        self.input_prompt = ""
        self.input_callback = None
        self.input_y, self.input_x = (5,1)

        # Register this method so input_system can trigger text input
        universe.request_text_input = self.start_text_input





    def run(self):
        curses.wrapper(self.main_loop)

    def change_mode(self, mode):
        self.mode_draw_function = self.modes.get(mode, exploration_mode)

    def main_loop(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)  # Non-blocking getch()

        while True:
            stdscr.erase()

            if stdscr.getmaxyx()[0] <= self.universe.size[0] or stdscr.getmaxyx()[1] <= self.universe.size[1]:
                stdscr.addstr(0, 0, "Veuillez agrandir la fenêtre")
            else:
                self.mode_draw_function(self, stdscr)
                self.draw_border(self.screens["scene"]["position"], self.screens["scene"]["size"], stdscr)
                self.draw_border(self.screens["hud"]["position"], self.screens["hud"]["size"], stdscr)

                if self.input_wanted:
                    # Draw input field with cursor
                    input_text = self.input_prompt + self.input_buffer + "_"
                    self.draw(stdscr, "hud", self.input_y, self.input_x, input_text)

                key = stdscr.getch()
                if key != -1:  # Non-blocking returns -1 if no key pressed
                    if self.input_wanted:
                        self.process_input_key(key)
                    else:
                        self.universe.input_system(self.universe, key_to_action(key))

            stdscr.refresh()

    def start_text_input(self, callback, prompt="", input_type="string", max_length=50,y=5,x=1):
        self.input_wanted = True
        self.input_buffer = ""
        self.input_prompt = prompt
        self.input_callback = callback
        self.input_type = input_type  # "string", "int", "float", etc.
        self.max_length = max_length
        self.input_y = y
        self.input_x = x

    def process_input_key(self, key):
        if key == 27:  # ESC
            self.input_wanted = False
            self.input_buffer = ""
        elif key == 10:  # ENTER
            if self.input_callback:
                result = self.validate_input(self.input_buffer)
                if result is not None:
                    self.input_callback(result)
                    self.input_wanted = False
                self.input_buffer = ""
        elif key == 127 or key == curses.KEY_BACKSPACE:
            self.input_buffer = self.input_buffer[:-1]
        elif 32 <= key <= 126:  # Printable characters
            if len(self.input_buffer) < self.max_length:
                self.input_buffer += chr(key)

    def validate_input(self, value):
        """Validates and converts input based on input_type."""
        if self.input_type == "string":
            return value
        elif self.input_type == "int":
            try:
                return int(value)
            except ValueError:
                return None  # Invalid, don't call callback
        elif self.input_type == "float":
            try:
                return float(value)
            except ValueError:
                return None
        return value

    def show_scene(self, stdscr):
        scene = self.universe.scenes[self.universe.current_world]
        for y, ligne in enumerate(scene.map_data):
            self.draw(stdscr, "scene", y, 0, ligne)

    def draw_player(self, stdscr):
        player = self.universe.player
        y, x = player.position
        self.draw(stdscr, "scene", y, x, player.sprite)

    def draw_entity(self, stdscr, entity):
        y, x = entity.position
        self.draw(stdscr, "scene", y, x, entity.sprite)

    def draw_entities(self, stdscr):
        scene = self.universe.scenes[self.universe.current_world]
        for entity in scene.entities.values():
            self.draw_entity(stdscr, entity)

    def draw_event(self, stdscr, event):
        y, x = event.position
        self.draw(stdscr, "scene", y, x, event.sprite)

    def draw_events(self, stdscr):
        scene = self.universe.scenes[self.universe.current_world]
        for event in scene.event_system.events.values():
            self.draw_event(stdscr, event)

    def draw_hud(self, stdscr):
        # draw hud at fixed coordinate like for exemple for now like this : [key] : action
        for idx, (k, v) in enumerate(HUD_KEYS.items()):
            self.draw(stdscr, "hud", idx + 0 + 1, 0 + 1, f"[{chr(k)}] : {v}")

    def draw_border(self, position, size, stdscr):
        """

        :param position: (y,x)
        :param size: (h,w)
        :param stdscr:
        :return:
        """
        h, w = size
        y, x = position

        # Bordures
        stdscr.addstr(y, x, '┌' + '─' * (w - 2) + '┐')
        stdscr.addstr(y + h - 1, x, '└' + '─' * (w - 2) + '┘')

        # Bordures latérales sans remplir
        for i in range(1, h - 1):
            stdscr.addstr(y + i, x, '│')
            stdscr.addstr(y + i, x + w - 1, '│')

    def convert_text_special(self, text):
        # unused for now
        """
        it checks if the character has to be turned into a special one
        :param stdscr:
        :param text:
        :param y:
        :param x:
        :return:
        """
        text_list = list(text)
        for idx, char in enumerate(text_list):
            if char in CHAR_MAP:
                text_list[idx] = CHAR_MAP[char]
        return ''.join(text_list)

    def load_sprite(self, path):
        """
        Charge un sprite ASCII depuis un fichier texte.
        Retourne :
            - liste des lignes
            - largeur maximale (max_x)
            - hauteur (max_y)
        """
        sprite_lines = []
        max_x = 0
        max_y = 0

        with open(path, "r", encoding='utf-8') as f:
            for line in f:
                line = line.rstrip("\n")
                sprite_lines.append(line)

                length = len(line)
                if length > max_x:
                    max_x = length

                max_y += 1

        return sprite_lines, (max_x, max_y)

    def draw_sprite(self, scene, sprite_lines, y, x, stdscr):
        """
        Affiche un sprite ligne par ligne à partir d'une liste de lignes.
        sprite_lines = liste obtenue via load_sprite().
        """
        a,b = self.screens[scene]["position"]
        for idx, line in enumerate(sprite_lines):
            # Chaque ligne est dessinée à la position (y + idx, x)
            self.draw(stdscr, scene, y + idx+a, x+b, line)

    def draw(self, stdscr, scene, y, x, text):
        """
        Dessine du texte à une position relative à une scène (scene ou hud).
        Les positions de la scène sont ajoutées aux coordonnées fournies.
        :param scene:
        :param y:
        :param x:
        :param text:
        :param stdscr:
        :return:
        """
        if scene in self.screens:
            pos = self.screens[scene]["position"]
        else:
            pos = (0, 0)
        text = self.convert_text_special(text)
        stdscr.addstr(y + pos[0], x + pos[1], text)

    def draw_text(self, stdscr, scene, y, x, text):
        x_max = self.screens[scene]["size"][1] - 2 - x
        words = text.split()
        current_line = ""
        size_line = 0

        for word in words:
            size_word = len(word)
            space_needed = 1 if current_line else 0

            # Le mot tient dans la ligne courante
            if size_line + size_word + space_needed <= x_max:
                if current_line:
                    current_line += " "
                    size_line += 1
                current_line += word
                size_line += size_word

            else:
                # On affiche la ligne courante
                if current_line:
                    self.draw(stdscr, scene, y, x, current_line)
                    y += 1

                # Découper les mots trop longs
                while size_word > x_max:
                    part = word[:x_max - 1] + "-"  # Xmax-1 + "-" = Xmax
                    self.draw(stdscr, scene, y, x, part)
                    y += 1
                    word = word[x_max - 1:]
                    size_word = len(word)

                # Le reste du mot pour après
                current_line = word
                size_line = size_word

        # Dernière ligne
        if current_line:
            self.draw(stdscr, scene, y, x, current_line)

    def segment_text(self, stdscr, scene,y,x):
        max_text = ((self.screens[scene]["size"][0]-1)//2) * (self.screens[scene]["size"][1]-2)
        if len(dialogue_system.current_dialogue)> max_text:
            while dialogue_system.current_dialogue[max_text] !=" ":
                max_text -=1
            new_text = dialogue_system.current_dialogue[:max_text]
            dialogue_system.current_dialogue = \
                dialogue_system.current_dialogue[max_text:]
            return new_text
        else:
            return dialogue_system.current_dialogue

    def get_dialogue_segment(self, max_lines, x_max):
        """
        Extrait un segment du dialogue, mot par mot, jusqu'à max_lines et x_max par ligne.
        Retourne une liste de lignes à afficher et met à jour current_dialogue.
        """
        text = dialogue_system.current_dialogue
        words = text.split()
        y_used = 0
        current_line = ""
        size_line = 0
        displayed_words = 0
        lines_to_draw = []

        for word in words:
            word_len = len(word)
            space_needed = 1 if current_line else 0

            if size_line + word_len + space_needed <= x_max:
                if current_line:
                    current_line += " "
                    size_line += 1
                current_line += word
                size_line += word_len
            else:
                # ligne complète
                lines_to_draw.append(current_line)
                y_used += 1
                if y_used >= max_lines:
                    break

                # découper les mots trop longs
                while word_len > x_max:
                    part = word[:x_max - 1] + "-"
                    lines_to_draw.append(part)
                    y_used += 1
                    if y_used >= max_lines:
                        break
                    word = word[x_max - 1:]
                    word_len = len(word)

                current_line = word
                size_line = len(word)

            displayed_words += 1

        if y_used < max_lines and current_line:
            lines_to_draw.append(current_line)

        # mise à jour du dialogue restant
        dialogue_system.current_dialogue = " ".join(words[displayed_words:])
        if dialogue_system.current_dialogue == "":
            dialogue_system.notify_reading_consumed()

        return lines_to_draw

    def draw_dialogue_lines(self, stdscr, scene, y, x, lines):
        """Affiche les lignes déjà préparées."""
        for idx, line in enumerate(lines):
            self.draw(stdscr, scene, y + idx, x, line)

    def draw_button(self, stdscr, scene, y, x, text):
        """Dessine un bouton avec du texte centré."""
        (border_y,border_x) = y + self.screens[scene]["position"][0], x + self.screens[scene]["position"][1]
        button_width = len(text) + 4  # 2 espaces de chaque côté
        self.draw_border((border_y, border_x), (3, button_width), stdscr)
        self.draw(stdscr, scene, y + 1, x + 2, text)

    def render_item_list(self, stdscr, scene, title):
        area_h, area_w = self.screens[scene]["size"]
        inner_w = max(0, area_w - 2)  # space inside borders
        inner_h = max(0, area_h - 2)

        # reserve 1 line for title, 1 for header and 1 for page indicator
        max_items = max(1, inner_h - 3)
        item_list_renderer.max_items_per_page = max_items

        item_keys = list(item_list_renderer.items.keys())
        num_items = len(item_keys)

        # pagination
        max_pages = max(1, (num_items + max_items - 1) // max_items)
        current_index = getattr(item_list_renderer, "current_index", 0)
        if current_index < 0:
            current_index = 0
        if current_index >= max_pages:
            current_index = max_pages - 1
        item_list_renderer.current_index = current_index

        start_idx = current_index * max_items

        # compute category width from item types (the "type" field)
        get_part_fn = getattr(item_list_renderer, "get_item_part", None)
        max_type_len = 0
        for name in item_keys:
            if callable(get_part_fn):
                t = get_part_fn(name, "type") or ""
            else:
                item_data = get_item(name)
                t = item_data.get("type", "") if item_data else ""
            if len(t) > max_type_len:
                max_type_len = len(t)
        category_w = max(1, max(len("Category"), max_type_len))

        # padding: 5% of available inner width each side (at least 1)
        pad = max(1, int(inner_w * 0.05))

        # ensure there is still enough space for minimal columns
        id_w = 1  # first column shows nothing in header but holds the single-char index
        qty_min = 3
        price_min = 6
        sep_count = 4  # separators between ID | Item | Category | Quantity | Price
        # each separator will use 3 chars: ' ' + '│' + ' ' to add breathing room
        minimal_total = id_w + category_w + qty_min + price_min + sep_count * 3 + 1  # +1 for at least 1 char name
        if inner_w - 2 * pad < minimal_total:
            # reduce padding to fit minimal layout
            pad = max(0, (inner_w - minimal_total) // 2)
        usable_w = max(1, inner_w - 2 * pad)

        # draw centered title within usable area
        title_x = 1 + pad + max(0, (usable_w - len(title)) // 2)
        self.draw(stdscr, scene, 1, title_x, title)

        # column size constraints requested
        qty_w = max(qty_min, len("Quantity"))
        price_w = max(price_min, len("Price"))

        # compute name column width from remaining usable space
        name_w = usable_w - (id_w + category_w + qty_w + price_w + sep_count * 3)
        if name_w < len("Item"):
            # try to free space by shrinking qty and price down to their minimal sizes
            extra_needed = len("Item") - name_w
            reduce_qty = min(extra_needed, qty_w - qty_min)
            qty_w -= reduce_qty
            extra_needed -= reduce_qty
            if extra_needed > 0:
                reduce_price = min(extra_needed, price_w - price_min)
                price_w -= reduce_price
                extra_needed -= reduce_price
            name_w = usable_w - (id_w + category_w + qty_w + price_w + sep_count * 3)

        if name_w < 1:
            name_w = 1

        # compute absolute x positions (relative to hud inner area, +1 for left padding and +pad)
        x0 = 1 + pad
        id_x = x0
        # layout:
        # [id_w][space]['│'][space][name_w][space]['│'][space][category_w][space]['│'][space][qty_w][space]['│'][space][price_w]
        sep1_x = id_x + id_w + 1  # position of first '│' (after id)
        name_x = sep1_x + 2  # start of name column (after '│' and its right space)
        sep2_x = name_x + name_w + 1
        category_x = sep2_x + 2
        sep3_x = category_x + category_w + 1
        qty_x = sep3_x + 2
        sep4_x = qty_x + qty_w + 1
        price_x = sep4_x + 2

        # headers: first column empty, Item uses remaining space, then Category, Quantity and Price
        headers = [
            ("", id_x, id_w),
            ("Item", name_x, name_w),
            ("Category", category_x, category_w),
            ("Quantity", qty_x, qty_w),
            ("Price", price_x, price_w),
        ]
        for h, hx, hw in headers:
            # ensure header fits: if still larger, truncate (should be rare due to adjustments)
            h_display = h if len(h) <= hw else h[:hw]
            hx_center = hx + max(0, (hw - len(h_display)) // 2)
            self.draw(stdscr, scene, 2, hx_center, h_display)

        # draw vertical separators matching items rows (start after header)
        sep_positions = (sep1_x, sep2_x, sep3_x, sep4_x)
        for row in range(3, 3 + max_items):
            for sx in sep_positions:
                # left padding space (inside usable area)
                if sx - 1 >= x0:
                    self.draw(stdscr, scene, row, sx - 1, " ")
                # the separator itself
                self.draw(stdscr, scene, row, sx, "│")
                # right padding space (inside usable area)
                if sx + 1 < x0 + usable_w:
                    self.draw(stdscr, scene, row, sx + 1, " ")

        # helper to produce single-char input id: 1-9 then a,b,c...
        def input_label_for(n):
            if n <= 9:
                return str(n)
            else:
                # 10 -> a, 11 -> b, ...
                return chr(ord('a') + (n - 10))

        # draw items rows
        for idx in range(max_items):
            item_idx = start_idx + idx
            if item_idx < num_items:
                item_name = item_keys[item_idx]
                quantity = item_list_renderer.items.get(item_name, 0)

                get_part = getattr(item_list_renderer, "get_item_part", None)
                if callable(get_part):
                    price = get_part(item_name, "price")
                    category = get_part(item_name, "type") or ""
                else:
                    item_data = get_item(item_name)
                    price = item_data.get("price", 0) if item_data else 0
                    category = item_data.get("type", "") if item_data else ""

                # ID label based on index on the page (1-based)
                label_num = idx + 1
                id_label = input_label_for(label_num)
                self.draw(stdscr, scene, idx + 3, id_x, id_label)

                # item name truncated to name_w
                name_text = f"{item_name}"
                if len(name_text) > name_w:
                    name_text = name_text[:max(0, name_w - 3)] + "..."
                self.draw(stdscr, scene, idx + 3, name_x, name_text)

                # category: truncate to fit
                cat_text = f"{category}"
                if len(cat_text) > category_w:
                    cat_text = cat_text[:category_w]
                self.draw(stdscr, scene, idx + 3, category_x, cat_text)

                # quantity: align right in qty_w
                qty_text = str(quantity).rjust(qty_w)
                self.draw(stdscr, scene, idx + 3, qty_x, qty_text)

                # price: align right in price_w, add currency suffix if fits
                price_text = f"{price}G"
                if len(price_text) > price_w:
                    price_text = price_text[-price_w:]
                price_text = price_text.rjust(price_w)
                self.draw(stdscr, scene, idx + 3, price_x, price_text)

        # draw centered page indicator under items within usable area
        page_text = f"[Page {current_index + 1} / {max_pages}]"
        page_x = 1 + pad + max(0, (usable_w - len(page_text)) // 2)
        self.draw(stdscr, scene, 3 + max_items, page_x, page_text)

    def draw_item_detail(self, stdscr, scene, item_id):
        area_h, area_w = self.screens[scene]["size"]
        inner_w = max(0, area_w - 2)  # space inside borders
        inner_h = max(0, area_h - 2)

        item_data = get_item(item_id)
        if not item_data:
            return  # item not found

        y = 1
        x = 1

        # Title: item name centered
        title = item_data.get("name", "Unknown Item")
        title_x = 1 + max(0, (inner_w - len(title)) // 2)
        self.draw(stdscr, scene, y, title_x, title)
        y += 2

        # Type
        item_type = item_data.get("type", "Unknown Type")
        type_text = f"Type: {item_type}"
        self.draw(stdscr, scene, y, x, type_text)
        y += 1

        # Price
        price = item_data.get("price", 0)
        price_text = f"Price: {price}G"
        self.draw(stdscr, scene, y, x, price_text)
        y += 2

        # Description (wrapped)
        description = item_data.get("description", "No description available.")
        self.draw_text(stdscr, scene, y, x, description)