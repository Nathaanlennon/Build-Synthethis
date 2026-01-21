import os

path = os.path.join(os.path.dirname(__file__), "..")

# Dossiers obligatoires
required_dirs = [
    "extensions",
    "assets",
    "assets/sprites",
    "assets/enemies",
    "assets/items",
    "assets/maps",
    "assets/shops",
    "assets/dialogues"
]

for d in required_dirs:
    os.makedirs(os.path.join(path, d), exist_ok=True)

input_file = os.path.join(path, 'assets/dialogues/DIALOGUE_FORMAT.txt')
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""DIALOGUES FORMAT - how to create a dialogue file for `assets/dialogues/*.json`

Structure
- The file is a JSON array. Each array element is a dialogue node.
- Nodes are referenced by their array index. Use integer `next` values in options to jump to another node.
- Use `-1` to indicate the conversation ends / UI closes.

Node fields (common)
- `speaker` (optional)
  - Type: string
  - Display name of the speaker (e.g. "PNJ", "Hero"). May be omitted for narration.
  speaker allows to show the sprite of the speaker, the name has to match an entry in assets/sprites/
- `text` (required)
  - Type: string
  - The message shown to the player. Can contain newlines. Long text is allowed. The ui will handle wrapping/scrolling so don't worry about it.
- `require` (optional)
  - Type: dictionary
  - Conditions can be multiples, all in the dictionnary
  - multiple conditions exists, like a boolen check on flags, or custom checks (like item presence)
  - they work with prefixes for universe and the player but can also work without (always in the player data then)
  - Exemple :
  require: { "has_key": true, "universe:quest_started": true }
  for the flags there are rules, they will be written in the end of this document
  - Keys are game flags or checks. Examples:
    - `"insulted_npc": true` (flag must be true)
    - `"has_item:health_potion": true` (custom check for item presence)
  - If `require` is omitted or `null`, the node is always available.
- `effects` (optional)
  - Type: dictionary
  - Applied when the node is reached (or when an option with `effects` is chosen).
  - Keys set or modify game state. Examples:
    - `"insulted_npc": false` (set a flag)
    - `"shop": 0` (trigger shop state), the value is the shop id from assets/shops/shops.json
    - `"mode": "inventory"` (change UI mode),

Options (player choices)
- `options` (optional)
  - Type: array of option objects.
  - If omitted, the node is terminal.
- Each option object:
  - `text` (required) — string shown on the choice button.
  - `next` (required) — integer index of the next node, or `-1` to close.
  - `require` (optional) — conditions for the choice to be shown (same format as node `require`).
  - `effects` (optional) — object applied when this option is chosen (same format as node `effects`).


DIALOGUE PREFIXES — require and effects

    Common prefixes (merged where behavior overlaps)

    player:
      - Require:
        - Format: `player:KEY` or `player:has_item:ITEM_ID`
        - Behavior: `player:has_item:ITEM_ID` checks `universe.player.inventory.items[ITEM_ID] >= 1`.
          Otherwise checks `universe.player.ext_data[KEY] == value`.
      - Effects:
        - Format: `player:KEY`
        - Behavior: sets `universe.player.ext_data[KEY] = value`.

    universe:
      - Require:
        - Format: `universe:KEY`
        - Behavior: checks `universe.ext_data[KEY] == value`.
      - Effects:
        - Format: `universe:KEY`
        - Behavior: sets `universe.ext_data[KEY] = value`.

    has_item:
      - Require only:
        - Format: `has_item:ITEM_ID`
        - Behavior: checks `universe.player.inventory.items[ITEM_ID] >= 1`.

    give_item:
      - Effects only:
        - Format: `give_item:ITEM_ID`
        - Behavior: if `int(value) > 0` calls `universe.player.inventory.add_item(ITEM_ID, int(value))`.
        exemple : `{"give_item:health_potion": 3}` gives 3 health potions.
        Note that the item id will be added to the player inventory regardless of its existence in assets/items/items.json
        (if an item id is invalid, trying to access to it later like opening the inventory will add an entry to the logger)

    remove_item:
      - Effects only:
        - Format: `remove_item:ITEM_ID`
        - Behavior: current logic only calls removal when `int(value) < 0` and does
          `universe.player.inventory.remove_item(ITEM_ID, value)` (note: expects positive values).

    Special effect keys (no prefix)
      - `heal` → calls `universe.player.heal(int(value))`.
      - `shop` → calls `shop_manager.set_shop(value)` and start a shop interaction.
      - `mode` → calls `universe.mode_change(value)`. Pre-existing modes: `"inventory"`, `"dialogue"`, `"exploration"`, `"combat"`.
      But you can add any mode you want, check the extensions files to learn more about it.

    Default (no prefix and not a special key)
      - Require:
        - Behavior: treated as `universe.player.ext_data[KEY] == value`.
      - Effects:
        - Behavior: stores `universe.player.ext_data[KEY] = value`.

    Examples
      - Require inventory: `{"has_item:health_potion": true}` or `{"player:has_item:health_potion": true}`
      - Effect give item: `{"give_item:gold_coin": 5}`
      - Effect set flag: `{"player:helped_npc": true}`
      - Effect open shop: `{"shop": 0}`

    Notes
      - Prefixes modify where keys are looked up or written (player ext_data vs universe ext_data).


Semantics / conventions
- Keep dialogue nodes in stable order; changing node order changes `next` targets.
- Use consistent flag names (snake_case recommended).
- `require` entries are checked as boolean or via project-specific handlers (e.g. item checks).
- `effects` values may be boolean, numeric, or string depending on your needs.
    Be aware that most of the time, the values will be stored in ext_data, either in player or universe scope.
- Use `-1` for immediate end/close

Examples (minimal)
- Simple node with two options:
  {
    "speaker": "PNJ",
    "text": "Bonjour. Que voulez-vous ?",
    "options": [
      { "text": "Rien.", "next": -1 },
      { "text": "Parler.", "next": 1 }
    ]
  }

- Node with requirement and effects:
  {
    "require": { "insulted_npc": true },
    "speaker": "PNJ",
    "text": "Tu m'as insulté !",
    "options": [
      {
        "text": "Désolé.",
        "next": -1,
        "effects": { "insulted_npc": false }
      }
    ]
  }

Notes
- When adding new condition/ effect keys, ensure game code can interpret them.
- Validate JSON (array of nodes) and keep strings properly escaped.
""")

input_file = os.path.join(path, 'assets/shops/SHOPS_FORMATS.txt')
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""SHOPS FORMAT - how to create a shop for `assets/shops/shops.json`

Overview
- Top-level structure: a JSON array of shop objects.
- Each element in the array is one shop. Use the shop's array index to open it.

Shop object fields
- `name` (required)
  - Type: string
  - Display name of the shop.
- `money` (required)
  - Type: integer (number) or string `"infinite"`
  - Shop funds. Use `"infinite"` to allow unlimited buying/selling.
- `items` (required)
  - Type: object (dictionary)
  - Keys: item IDs (must match IDs from the items database).
  - Values: item entries (see "Item entry" below).

Important implementation note
- In this project the shop loader converts each shop into an `Inventory` instance and calls `Inventory.load_data(shop)`. Because `ShopManager.require` expects each shop item to be a mapping (so it can call `.get("require", {})`), each shop item entry must be an object (not a raw integer). Use an object with at least a `quantity` field even when no `require` is needed.

Item entry (per item in `items`)
- `quantity` (required)
  - Type: integer or string `"infinite"`
  - How many units the shop has for that item.
- `require` (optional)
  - Type: object (dictionary) or falsy value (e.g. `{}` or `null` or `0`)
  - If missing, empty or falsy, the item is always available.
  - If present as a non-empty object, all keys in the object are evaluated; if any requirement fails the item is hidden.

Supported `require` formats and semantics (as implemented by `ShopManager.require`)
- General behavior:
  - The code iterates `for key, value in require.items():` and tests each entry. All must pass for the item to be available.
  - If `require` is empty/falsey, the item is available.

- `player:has_item:ITEM_ID`
  - Format: the requirement key is `"player:has_item:ITEM_ID"`
  - Behavior: checks `player.inventory.items.get(ITEM_ID, 0) >= 1`.
  - The associated requirement `value` is ignored by the current check (presence is tested).

- `player:KEY`
  - Format: key starts with `"player:"` and the rest is `KEY`
  - Behavior: checks `player.ext_data.get(KEY) == value`.

- `level:X`
  - Format: requirement key begins with `"level:NUMBER"` (e.g. `"level:5"`)
  - Behavior: the code parses the number from the key and checks `player.level >= NUMBER`. The `value` in the dict is not used.

- Default (no recognized prefix)
  - Format: `"flag_name": some_value`
  - Behavior: checks `player.ext_data.get(flag_name) == some_value`.

Notes about usage and caveats
- Because of implementation details:
  - Put item entries as objects with `quantity` and optional `require` (not bare integers).
  - For level checks, place the number in the key (`"level:3"`) rather than the value.
  - For item-presence checks, use the `player:has_item:ITEM_ID` key (or `player:has_item:ITEM_ID: true` — value is ignored).
- Shop selection:
  - Shops are accessed by index. Use `shop_manager.set_shop(index)` where `index` is the array position (0-based).
- Item prices:
  - Prices are read from the global items database (`assets/items/items.json`) via `ItemManager.get_item(...)`; do not put price inside shop item entries unless your game code has been extended to read it.
- Example item entry forms:
  - Always available, infinite stock:
    { "quantity": "infinite" }
  - Limited stock with no requirement:
    { "quantity": 5 }
  - Requires player level 3:
    { "quantity": 2, "require": { "level:3": true } }
  - Requires the player to own an item `guild_token`:
    { "quantity": 1, "require": { "player:has_item:guild_token": true } }
  - Requires a player flag `helped_smith` to equal `true`:
    { "quantity": 1, "require": { "player:helped_smith": true } }

Validation tips
- Ensure JSON is well-formed (commas, braces).
- Keep each shop item entry as an object with `quantity` when using `require`.
- Test shops in-game by calling `shop_manager.set_shop(index)` to verify filtered lists appear as expected.
""")
input_file = os.path.join(path, 'assets/maps/MAPS_FORMAT.txt')
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""Maps are quite easy to make. It's a simple text file, translated to a double array of characters by the program.
For the dimensions, you can choose the size you want but the max has to be the size of a screen you choose in the main.py, because if you dont and the terminal is not big enough it will crash.
Dont forget to put a border tho it will disapear behind the screen border if you made the map as big as possible (it's pretty I promise).
Here is an example of a simple map that was made:

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                                  │   │                              %
%──────────────────┐               │   │                  ┌─────┐     %
%            /\    └────────────┐  │   │    ┌─────────────┘     │     %
%           /  \                └──┤   ├────┘     ▲             └─────%
%          /────\                  │   │         /─\                  %
%  ┌───┐   │    │─┌─┐                            │ │              ▲   %
% <│ZOO│   │    │ │B│        *******             ├D┤             /─\  %
%  └───┘   │    │ └─┘      *    ┌─┐  *                  ┬─┬      │ │  %
%    │     │─DD─│        *             *                │ │      ├D┤  %
%─ ─ ┴ ─                *       🌳£      *              🧍£ │           %
%                      *     🌳£ 🌳£ 🌳£ ┌─┐*          N ====┴=          %
%─ ─ ─ ─               *       ☭£  🌳£     *                     ▲      %
%                      * ┌─┐   🌳£        *                    /─\     %
%       ▲               *               *   ┌─Théâtre─┐       │ │     %
%      /─\               *          ┌─┐*    │┌───────┐│       ├D┤     %
%      │ │                 *         *      │~       │D               %
%      ├D┤                   *******        └│┌─────┐│┘┐              %
%                                                                     %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Each map file is stored in assets/maps/ and is named with the map id (snake_case) followed by .txt
For example the map above is stored in assets/maps/village2.txt

You may have noticed multiple things. You have a lot of different characters, even unicode ones, and you have a lot of '£'.
The map is not rectangular either.
This is because of the unicode characters, they take 2 characters in the terminal but are registered as one character in the text file and the array.
It leads to collisions problems, this is why we use '£' after unicode characters as the ui turns them into '' but the collision is still there. I did not find a better way for now so please if you want to use unicode, you can absolutelu but you HAVE TO had a '£' after each unicode character.
Don't worry about the fact that the map is currently not rectangular, as the '£' are not visible, it looks rectangular in the end.

By default, the walkable characters are:
['.', ',', ';', ':', '*', ' '] so in our exemple, all the areas with '*' are walkable.
For now, if you want to change the walkable characters, you have to do a self.walkable_tiles = [...] when you create your map function/class (Sorry for that I did not make a method to change that yet).

Informations to add a map to the game are in extensions/data_extensions.py but here is a quick summary:
you can either use a class or a function to create your map. I suggess using a function most of the time as it's easier but you have the choice. Use a class if you need special values or methods for your map.
Either way, your map depend on the World class from engine/core/base.py so you have to import it.
if you use a function, you have to return a World object.
Here is an example of a map function:

from engine.core.base import World
def zooKeeperHouse(data):
    self = World(data, "zooKeeperHouse", "assets/maps/zooKeeperHouse.txt")

    self.add_entity(Entity(self, "door1Keeper", (14, 34), 'D',
                           [Event(data, self, "door1Keeper", "ON_INTERACT", "MOVE",
                                  target_scene="Zoo", target_position=(18, 55))]))
    self.add_entity(Entity(self, "door2Keeper", (14, 35), 'D',
                           [Event(data, self, "door2Keeper", "ON_INTERACT", "MOVE",
                                  target_scene="Zoo", target_position=(18, 56))]))

    self.add_entity(NPC(self, "zooKeeper", (8, 44), 'N', dialogue="assets/dialogues/test.json"))

    return self
Before we used classes for maps, that's why you see this "self" everywhere. You don't have to use it but if you wish to switch to a class later, you'll just have to change the def to class and add an __init__ method.
I'll put a more complete method in another text file for the creation of maps.""")

input_file = os.path.join(path, 'assets/items/ITEMS_FORMAT.txt')
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""ITEMS FORMAT - how to create an item for `assets/items/items.json`

Structure
- The file is a JSON object where each property key is the item's unique `id` (snake_case).
- Each item value is an object describing that item.

Top-level item fields (common)
- `id` (required)
  - Type: string
  - Must match the parent key (unique identifier).
- `name` (required)
  - Type: string
  - Display name (can contain spaces and accents).
- `type` (required)
  - Type: string (enum)
  - Typical values: `equipment`, `consumable`, `junk`, `quest_item`.
- `description` (optional)
  - Type: string
  - Short text describing the item.
- `price` (optional)
  - Type: integer (>= 0)
  - Shop price or value.

Equipment-specific
- Applies when `type` == `equipment`.
- `position` (required)
  - Type: string
  - Equipment slot, e.g., "weapon", "headgear", "chestplate", "leggings", "boots", "shield".
- `damages` (optional, for weapons)
  - Type: integer (>= 0)
  - Attack power when equipped.

Consumable-specific
- Applies when `type` == `consumable`.
- `effect` (optional)
  - Type: object
  - Contains one effect key such as:
    - `heal`: integer (amount of HP restored).
    - `damage`: integer (instant damage to target).

Quest item / capacity items
- Applies when `type` == `quest_item`.
- `capacity` (optional)
  - Type: object mapping internal ability keys to ability definitions.
  - Each ability object typically has:
    - `name`: string (display name of the ability).
    - `damage`: integer (damage value).
    - `accuracy`: number (0.0 to 1.0).
not every quest item needs a capacity; some may just be keys for story progression.
Capacities in quest items is more like a special case for items that grant abilities.
In game logic it would be like if you want to give and retrieve abilities easily.
Like a magician getting spells books or something

Junk items
- `type` == `junk`
- Minimal fields commonly used: `id`, `name`, `description`, `price`.

Validation rules / conventions
- `id` must be unique and match the key string exactly.
- Use snake_case for `id` and internal keys.
- Numeric fields (`price`, `damages`, `damage`, `heal`) should be non-negative integers.
- `accuracy` is a float between 0 and 1 (inclusive).
- Keep JSON well-formed: use commas between properties, proper braces/brackets.

Examples (minimal)
- Equipment example:
  {
    "my_sword": {
      "id": "my_sword",
      "name": "My Sword",
      "type": "equipment",
      "position": "weapon",
      "damages": 12,
      "price": 40
    }
  }

- Consumable example:
  {
    "small_potion": {
      "id": "small_potion",
      "name": "Small Potion",
      "type": "consumable",
      "effect": { "heal": 25 },
      "price": 5
    }
  }

- Quest item example:
  {
    "fire_tome": {
      "id": "fire_tome",
      "name": "Fire Tome",
      "type": "quest_item",
      "capacity": {
        "fireball": { "name": "Fireball", "damage": 75, "accuracy": 0.8 }
      }
    }
  }

Notes
- Add only the fields needed for the item's behavior; unused fields may be ignored by the game but keep data consistent.
- When adding new fields or types, update game code that reads items accordingly.
""")
input_file = os.path.join(path, 'assets/enemies/ENEMIES_FORMAT.txt')
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""ENEMIES FORMAT - how to create an enemy for `assets/enemies/enemies.json`

Structure
- The file is a JSON object where each property key is the enemy's unique `id` (snake_case).
- Each enemy value is an object describing that enemy.

Top-level enemy fields (common)
- `id` (required)
  - Type: string
  - Must match the parent key (unique identifier).
- `name` (required)
  - Type: string
  - Display name.
- `hp` (required)
  - Type: integer (>= 0)
  - Hit points / health.
- `damage` (required)
  - Type: integer (>= 0)
  - Base attack damage.
- `defense` (optional)
  - Type: integer (>= 0)
  - Damage reduction when attacked.
- `loot` (optional)
  - Type: object
  - Maps item_id to drop chance (0.0 - 1.0) or integer count.
  - Example: { "iron_sword": 0.2, "gold_coin": 1 }

Abilities
- `abilities` (optional)
  - Type: array of objects
  - Each ability object:
    - `name`: string
    - `damage`: integer (>= 0)
    - `accuracy`: number between 0.0 and 1.0

Validation rules / conventions
- Use snake_case for `id` and internal keys.
- Numeric fields (`hp`, `damage`, `defense`) should be non-negative integers.
- Drop chances are floats between 0 and 1 (inclusive).
- Keep JSON well-formed: use commas between properties, proper braces/brackets.

Examples (minimal)
- Simple enemy:
  {
    "slime": {
      "id": "slime",
      "name": "Slime",
      "hp": 8,
      "damage": 3,
      "defense": 1,
      "loot": { "slime_gel": 0.7 },
      "abilities": [
        { "name": "Splash", "damage": 4, "accuracy": 0.9 }
      ]
    }
  }

Notes
- Only include fields required by the game logic. Unused fields may be ignored.
- When adding new fields, update game code that reads `assets/enemies/enemies.json`.
""")
input_file = os.path.join(path, 'assets/sprites/SPRITE_FORMAT.txt')
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""Sprite are quite easy to make. It's a simple text file, translated to a double array of characters by the program.
I strongly recommend using ascii characters however since the sprites are not meant to have any interaction with the player (I mean no moving and no collisions) you can use any characters you want.
Unicode characters take two spaces so it makes things little weird but it messes up with the collision system so it should be fine here, however I never tried so I can't guarantee it will work perfectly.
Here is an example of a bat that I made:

 |\  /\_/\  /|
/ˊ_\.`\¨/ˊ./_`\ 
┐/ |`-┤ ├-ˊ| \┌
 ┐/_┌-'T'-┐_\┌
  ¯   / \   ¯

Be aware that the sprite may change a little depending on the terminal parameters you have, it may look stretched or squished.

Each sprite file is stored in assets/sprites/ and is named with the sprite id (snake_case) followed by .txt
For example the bat sprite is stored in assets/sprites/bat.txt
You can create your own sprites by making a text file and saving it in the assets/sprites/ folder.

All the sprites are saved in the assets/sprites/ folder regardless of their type (enemies, npcs, etc).
for npc sprite I recommand to use the maximum of space availabled by your screen size choice as in dialogues, all the top scene is used for the npc sprite.

for enemies, in the combat system there is a var that define the maximum amount of enemies that can be displayed at once, so I recommand that you make your enemy sprites small enough to fit that maximum amount on the screen at once.
By default the maximum amount of enemies displayed at once is 3, and they are placed side by side so the weidth of each enemy sprite should be at most one third of the scene width minus some space for padding.
The ui system will center the enemies automatically so you don't have to worry about that. If you have an ennemy that is sure to be alone you can make it wider however.

""")

# Fichier d’input system par défaut
input_file = os.path.join(path, 'extensions/ui_extensions.py')
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""#This module defines various UI extension modes for the application.

#It is very simple to use : just add new modes to the `modes` dictionary, where the key is the mode name and the value is the corresponding function that implements the mode's behavior.

#Each mode function should accept a single parameter, typically the standard screen object (`stdscr`), which is used for rendering the UI in that mode.

#Example:
#def custom_mode(self, stdscr):
#    # Custom mode implementation

ui_modes = {
    #cutom_mode: custom_mode,
}

# There is a key mapping in engine/ui/curses_ui.py that maps key codes to action strings.
# You can add more keys here if needed and even modify existing ones.
# Note that modifying existing keys may affect the default behavior of the application.

KEY_MAPPING = {
    # Example: ord('a'): "CUSTOM_ACTION",
}
""")
input_file = os.path.join(path, "extensions/input_extensions.py")
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""#this module defines various input extension modes for the application.

#It is very simple to use : just add new modes to the `modes` dictionary, where the key is the mode name and the value is the corresponding function that implements the mode's behavior.
#Each mode function should accept two parameters, typically the universe object and the key input, which is used for handling input in that mode.
#Note that the input is defined by a mapping from key codes to action strings in the engine/ui/curses_ui.py file.
#You can create your own mapping in ui_extensions.py if needed.
#exemple:
#def custom_input(universe, key):
#    # Custom input implementation

input_modes = {
    #custom_input: custom_input,
}
# the hud input is a set of actions that can be triggered from the hud, like opening the inventory, quitting the game, etc.
# you can add more actions here if needed and even modify existing ones.
# it works with the key mapping in engine/ui/curses_ui.py that maps key codes to action strings.
# the code will take the key if in the hud set and trigger the corresponding action by changing the mode of the universe.
# it will work this way : 
#    elif key in hud:
#        universe.mode_change(self, key.lower())
# so it is very important that the input action string matches the mode name in lowercase.
hud = {
    # Example: "CUSTOM_ACTION",
}
""")

input_file = os.path.join(path, "extensions/data_extensions.py")
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""# this is where all the additionnal data will be put, all the data that is not originally in the game-engine. 
# It will be imported in the universe_data and the player_data in the core but the said core will never know nor use it, it's only for your additional extensions that you make


# You need to import your world classes/function here to be able to use them in the worlds dictionary below.
# from world import Test, Test2, Test3 for exemple, if your worlds are classes defined in world.py
# from world import * for exemple, if your worlds are functions that build worlds defined in world.py
# (the fact that it is a class or a function doesnt change anything but it may be easier for you if you use functions to build your worlds)
# either ways, the core class for the world is Word, please use Word either with a class (class MyWorld(Word): ) or with a function (def MyWorld(): return Word(...) )

# this is where you define the different worlds that your game will have.
# the name of the wolrd is the key and the value is the Class that defines the world.
worlds = {
    #"my_world": MyWorldClass,
}

# VERY IMPORTANT: those data dictionaries bellow can contain any type you want, including objects 
# BUT : if you use objects instances, you HAVE TO MAKE SURE that the classes has a function called "extract_data" that will return a serializable version of the object as a dictionary
# You also need a function load_data(self, data) that will load the data from a dictionary to the object
# if you don't do that, saving/loading the game will not work properly.
universe_data = {
    
}

# If your objects need universe, add the instance in the list below, and self.universe in your class, so the program will do instance.universe = self
#you will need to import the instances at the top of the file too to do it.
# in those classes you HAVE TO HAVE the init_universe(self, universe) function that will set self.universe = universe at least, it's because yoy maybe need to init things that needs universe
instances = [
# exemple: instance1, instance2
]


player_data = {
    
}""")

input_file = os.path.join(path, "launch_game.py")
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""
import engine.core.SaveManager as SaveManager
import subprocess
import sys
import os

def main():
    universe_name = SaveManager.choose_universe()
    player_name = SaveManager.choose_player(universe_name)

    # Path toward the main (same repository)
    script_path = os.path.join(os.path.dirname(__file__), "main.py")

    # Launch script
    subprocess.run([
        sys.executable,   # python used to launch THIS script
        script_path,
        universe_name,
        player_name
    ])

if __name__ == "__main__":
    main()

        """)
input_file = os.path.join(path, "main.py")
if not os.path.exists(input_file):
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("""
import os
# Change working directory to the script's directory so relative imports/files resolve correctly
os.chdir(os.path.dirname(__file__))
# Import UniverseData class from the engine core module (used to load/create universe state)
from engine.core.base import UniverseData
import sys


def main():
    # load name and player from command-line arguments, passed from launch_game.py
    universe_name = sys.argv[1]
    player_name = sys.argv[2]

    # loading the universe here
    # you choose the starting world here, it's where the character will first spawn
    # Create a UniverseData instance:
    # - "default" is the starting world key/name
    # - (20 * 2, 71) is the map/interface size (lines, columns) (idea is that you get two screens by defautlt)
    # - universe_name and player_name are passed from the CLI
    # - (2,2) is the starting coordinates within the world
    data = UniverseData("default", (20 * 2, 71),
                        universe_name, player_name, (2,2))  # size is the size with the map and interface, number of lines and columns

    # Import the curses-based UI and instantiate it with the loaded UniverseData
    from engine.ui.curses_ui import CursesUI

    # Create the interface object that will handle rendering and input
    interface = CursesUI(data) # curses for now but le engine is separated from the ui so you can make your own ui if you want
    interface.run()  # start the display and game loop

if __name__ == "__main__":
    main()

        """)
