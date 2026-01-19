import json  # used to load dialogues from JSON files
import os    # used to check file paths

from engine.core.ItemManager import dealItem
from engine.core.ShopSystem import shop_manager

class DialogueSystem:
    """Manage dialogue flow for the game: loading dialogues,
    handling choices, and advancing lines or branches.
    Text is kept in `current_dialogue` and the UI is responsible for segmentation/drawing.
    """
    def __init__(self, universe):
        # store reference to the game universe to trigger mode changes when dialogues end
        self.universe = universe
        # list of dialogue entries loaded from a JSON file
        self.dialogues = []
        # remaining text of the current dialogue line yet to be shown
        self.current_dialogue = ""
        self.current_say = ""
        # state controls how the system behaves: NEXT_LINE, TEXT_CHUNK, CHOICE
        self.state = "NEXT_LINE"
        # list of visible choice texts for the current dialogue entry
        self.choices = []
        # index of the current dialogue entry in self.dialogues
        self.index = -1
        self.max_length = 100 # max size for now, UI handles wrapping/segmenting

        self.speaker = None

    def check_requirements(self, require):
        """
        Vérifie si les conditions d'un dialogue ou d'une option sont remplies.
        see code comments in original for supported keys.
        """
        if not require or require == {}:
            return True

        for key, value in require.items():
            if key.startswith("player:"):
                subkey = key.split(":", 1)[1]
                if subkey.startswith("has_item:"):
                    item_id = subkey.split(":", 1)[1]
                    if self.universe.player.inventory.items.get(item_id, 0) < 1:
                        return False
                else:
                    if self.universe.player.ext_data.get(subkey) != value:
                        return False
            elif key.startswith("universe:"):
                subkey = key.split(":", 1)[1]
                if self.universe.ext_data.get(subkey) != value:
                    return False
            elif key.startswith("has_item:"):
                item_id = key.split(":", 1)[1]
                if self.universe.player.inventory.items.get(item_id, 0) < 1:
                    return False
            else:
                if self.universe.player.ext_data.get(key) != value:
                    return False
        return True

    def apply_effects(self, effects):
        """
        Applique les effets définis dans un dialogue ou une option.
        """
        if not effects:
            return

        for key, value in effects.items():
            if key.startswith("player:"):
                subkey = key.split(":", 1)[1]
                self.universe.player.ext_data[subkey] = value
            elif key.startswith("universe:"):
                subkey = key.split(":", 1)[1]
                self.universe.ext_data[subkey] = value
            elif key.startswith("give_item:"):
                item_id = key.split(":", 1)[1]
                if int(value) > 0:
                    self.universe.player.inventory.add_item(item_id, int(value))
            elif key.startswith("remove_item:"):
                item_id = key.split(":", 1)[1]
                if int(value) < 0:
                    self.universe.player.inventory.remove_item(item_id, value)
            elif key == "heal":
                self.universe.player.heal(int(value))
            elif key == "shop":
                shop_id = value
                shop_manager.set_shop(shop_id)
                self.universe.mode_change("inventory")
            elif key=="mode":
                self.universe.mode_change(value)

            else:
                self.universe.player.ext_data[key] = value

    def set_dialogues(self, file_path):
        """Load dialogues from file_path if it exists, otherwise fall back to default."""
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                self.dialogues = json.load(file)
        else:
            with open("assets/dialogues/default_dialogues.json", 'r') as file:
                self.dialogues = json.load(file)
        self.index = 0
        self.set_current_dialogue()

    def set_current_dialogue(self):
        """Set self.current_dialogue and determine the next state based on length
        and presence of options for choice-based branching."""
        if 0 <= self.index < len(self.dialogues):
            if self.check_requirements(self.dialogues[self.index].get("require", None)):
                self.current_dialogue = self.dialogues[self.index].get("text", "")
                if len(self.current_dialogue) > self.max_length:
                    self.state = "TEXT_CHUNK"
                elif "options" in self.dialogues[self.index]:
                    self.state = "CHOICE"
                    self.set_choices()
            else:
                self.index += 1
                self.set_current_dialogue()
        self.speaker = self.dialogues[self.index].get("speaker", None)

    def as_choices(self):
        return "options" in self.dialogues[self.index]

    def notify_reading_consumed(self):
        """
        Called by the UI when it has finished displaying the current dialogue text.
        Ensures an immediate transition:
          - to `CHOICE` (and populates choices) if the current entry has options,
          - to `NEXT_LINE` if there are no options,
          - or keeps `TEXT_CHUNK` if there is still remaining text.
        """
        # ensure index valid
        if not (0 <= self.index < len(self.dialogues)):
            return

        # treat empty/whitespace-only as consumed
        if self.current_dialogue.strip() == "":
            if self.as_choices():
                self.state = "CHOICE"
                self.set_choices()
            else:
                self.state = "NEXT_LINE"
        else:
            # still has text -> remain in TEXT_CHUNK
            self.state = "TEXT_CHUNK"

    def set_choices(self):
        """Populate self.choices with the text of available options for the current entry."""
        self.choices = []
        if "options" in self.dialogues[self.index]:
            for choice in self.dialogues[self.index]["options"]:
                if self.check_requirements(choice.get("require", None)):
                    self.choices.append(choice["text"])

    def set_next_line(self, choice_index=None):
        """Advance the dialogue index. Handle choice branching or linear progression."""
        if self.state == "CHOICE" and choice_index is not None:
            choice = self.dialogues[self.index]["options"][choice_index]
            self.index = choice["next"]
            if "effects" in choice:
                self.apply_effects(choice["effects"])
            self.choices = []
            self.state = "NEXT_LINE"
        else:
            self.index += 1

        # clear remaining raw dialogue text (UI will receive new text after set_current_dialogue)
        self.current_dialogue = ""
        # if index is out of range or set to -1, return to exploration mode in universe
        if self.index == -1 or self.index >= len(self.dialogues):
            if self.universe.mode == "dialogue":
                self.universe.mode_change("exploration")
        else:
            self.set_current_dialogue()

dialogue_system = DialogueSystem(None)  # Placeholder, will be set with universe reference later
def setup_dialogue_system(universe):
    dialogue_system.universe = universe