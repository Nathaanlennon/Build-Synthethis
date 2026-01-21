# Build-Synthethis
It's a game engine for python projects on the terminal that allow to create games, by default you can create an easy RPG game whitout using a lot of code but it's fully customisable

to use the game engine, please verify first that you have curses installed in your system.

windows : 
```bash
# Check interpreter
python --version

# Upgrade pip (optional)
python -m pip install --upgrade pip

# Install the Windows curses binding
python -m pip install windows-curses

```

run : 
When you want to launch your project, go on the project repository and run the [launch_game.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/launch_game.py) file. DO NOT run [main.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/main.py) directly, has arguments are needed to launch the game properly.
```bash
py -3 [launch_game.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/launch_game.py)
```

Linux:
go on the repository and run
```bash
python3 [launch_game.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/launch_game.py)
```

# How to use the engine : 
You must launch [setup_environment.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/setup_environment.py) at first, it may show an error but it's normal. The setup will create the necessary files and folders for the engine to work properly.
It will also provide you with explanation files for the different assets in [assets/](https://github.com/Nathaanlennon/Build-Synthethis/tree/main/assets) folder. Read them to understand how to create your own assets and feel free to check the git hub repository for a simple exemple.
Check the [engine/README.md](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/engine/README.md) file for more information about the core architecture of the engine.
Please check the [extensions/](https://github.com/Nathaanlennon/Build-Synthethis/tree/main/extensions) folder as there is some important informations about how to had things, including your different worlds. For a simple rpg, the only code you have to do is to have your worlds functions and add the worlds in [extensions/data_extensions.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/extensions/data_extensions.py) accordingly to the explanations in the file.
The rest will just be adding your stuff in the [assets/](https://github.com/Nathaanlennon/Build-Synthethis/tree/main/assets) folder.


## Creating a world : 
You can create a world anywhere you want, using either a class or a function. You'll then have to add it into the [extensions/data_extensions.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/extensions/data_extensions.py) file in the worlds list.

### how to create a world : 

If you use a function, you have to create a function that will return a World instance. The function must take a data argument that will contain the universe basically, most of the time you don't need to worry about it as it's just a requiered argument for the World class.
Here is an exemple of a simple world function : 
```python
from engine.core.base import World
def World1(data):
    self = World(data, "zooKeeperHouse", "assets/maps/zooKeeperHouse.txt")
    return self
   ```
This will create a world called World1 that will have the map [assets/maps/zooKeeperHouse.txt](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/assets/maps/zooKeeperHouse.txt)

Now if you want/need to use the class way, you have to create a class that will inherit from World class.
Here is an exemple of a simple world class : 
```python
from engine.core.base import World
class Test(World):
    def __init__(self, data, **kwargs):
        super().__init__(data, "assets/maps/maptest.txt", (2, 3))
        self.name = "Monde1"
        # You can add more attributes and methods here as needed
```
I suggest using self as the name of the returned instance in the function as if you want to turn it into a class later, it will be easier to do so.

### add entities and events to the world :
You can add entities and events to the world using the add_entity and add_event methods of the World class. This way, using the function or the class doesn't matter at all so it's easier.
Entities are linked to the world.

ENTITIES & EVENTS - how to add entities and events to worlds

Overview
- Worlds manage entities and an EventSystem. Entities can hold events (linked to that entity) or events can be added directly to the world's event system.
- Use `World.add_entity(entity)` to register an entity. Use `entity.add_event(event)` or pass events to `Entity(...)` on creation to attach events to an entity.
- Events define activation conditions and actions. The engine checks event requirements and calls `Event.activation()` when triggered.

World.add_entity
- Call: `world.add_entity(entity)`
- Effect: registers the entity in `world.entities` and (when events exist) the event is added to the world's `EventSystem`.
- During save/load: entities are recreated first, then their events are added (this ordering is required).

Entity constructor (signature and typical args)
- Signature pattern:
  Entity(world, name, position, sprite, events=None, walkable=False, **kwargs)
- Parameters:
  - `world`: the World instance that owns the entity.
  - `name`: unique string identifier for the entity.
  - `position`: tuple (y, x) or (row, col).
  - `sprite`: char/string used for rendering.
  - `events`: optional list of `Event` instances to attach immediately.
  - `walkable`: boolean; whether other entities/players can walk through this entity.
- Use `entity.add_event(event)` to add events after creation.

Event constructor (signature and typical args)
- Signature pattern:
  Event(data, world, name, activation_type, action_type, entity=None, position=None, activate=True, **kwargs)
- Key parameters:
  - `data`: Universe/`UniverseData` instance (game-wide context).
  - `world`: World instance where the event lives.
  - `name`: event identifier.
  - `activation_type`: when to check/trigger (examples below).
  - `action_type`: what happens when triggered (examples below).
  - `entity`: optional Entity instance — when present the event is linked to that entity.
  - `position`: optional position for non-entity events.
  - `activate`: initial active flag (True/False).
  - `**kwargs`: action-specific arguments (e.g., `target_scene`, `dialogue`, `enemies`, `proba`, `mode`).

Activation types (what triggers the event)
- `ON_STEP`: triggers when player steps on the event tile. `Event.walkable` is True for `ON_STEP` (tile can be walked through).
- `ON_INTERACT`: triggers when player interacts while facing the event's position (or entity).
- `ALWAYS`: checked every movement/action; can be used for random encounters or repeated checks.
- The engine calls `Event.should_trigger(action)` to decide if the event should run.

Action types (what the event does when triggered)
- `MOVE`:
  - Required kwargs: `target_scene` (string/class), `target_position` (tuple).
  - Behavior: `UniverseData.set_world(target_scene)` and moves player to `target_position`.
- `DIALOGUE`:
  - Required kwargs: `dialogue` (path to dialogue JSON).
  - Behavior: switches mode to `dialogue` and opens the given dialogue file.
- `COMBAT`:
  - Required kwargs: `enemies` (list of (enemy, chance) tuples), `proba` (float 0..1).
  - Optional `max_enemies`.
  - Behavior: may switch to combat mode and setup combat when probability check passes.
- `MODE_CHANGE`:
  - Required kwargs: `mode` (string).
  - Behavior: calls `UniverseData.mode_change(mode)`.

Event argument validation
- Events set `necessary_args` depending on `action_type` and call `check_event_args` to disable the event if required kwargs are missing.
- If required args are missing the event is marked inactive and a warning is logged.

Adding events to entities and the world
- Attach events when creating an Entity:
  - Example pattern: `Entity(world, "door1", (14,34), 'D', [Event(data, world, "door1", "ON_INTERACT", "MOVE", target_scene="Zoo", target_position=(18,55))])`
- Or create an Entity then add events:
  - `e = Entity(world, "sign", (6,13), 'S')`
  - `e.add_event(Event(data, world, "sign_info", "ON_INTERACT", "DIALOGUE", dialogue="[assets/dialogues/sign.json](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/assets/dialogues/sign.json)"))`
- To add a world-level (non-entity) event:
  - `world.event_system.add_event(Event(data, world, "roaming_encounter", "ALWAYS", "COMBAT", enemies=[("goblin",0.2)], proba=0.15))`

NPC helper
- `NPC` is a convenience subclass that creates a basic entity and automatically adds a dialogue event:
  - Usage: `NPC(world, "npc_name", (y,x), 'N', dialogue="assets/dialogues/npc.json")`
  - It adds an `ON_INTERACT` `DIALOGUE` event tied to that NPC.

Walkability and collisions
- `World.is_walkable(tile)` uses `world.map_data` and `walkable_tiles` and also checks entities: if an entity at the tile has `is_walkable()` False the tile is blocked.
- If an event is created with `activation_type == "ON_STEP"`, the event's `walkable` is True by default; when attaching to an entity you can still set the entity's `walkable` flag to control collisions.

Saving / Loading notes
- When saving worlds, entities and events are serialized (`Entity.extract_data()`, `Event.extract_data()`).
- On load: worlds recreate entities first, then events are recreated and attached. Keep this ordering in mind if you write custom load code.

Examples (plain-text snippets you can copy)
- Door entity that moves to `Zoo` on interaction:
  Entity creation with event:
  Event(..., "ON_INTERACT", "MOVE", target_scene="Zoo", target_position=(18,55))
- Sign NPC with dialogue:
  NPC(..., dialogue=`assets/dialogues/zooSign.json`)
- Random combat event on the map:
  Event(..., "ALWAYS", "COMBAT", enemies=[("goblin",0.1),("bat",0.3)], proba=0.15, max_enemies=3)

References
- Implementation details and behavior can be found in [engine/core/base.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/engine/core/base.py) (`World`, `Entity`, `Event`, `NPC`) and the `EventSystem` used by `World.event_system`.


I'll setup an exemple in the git hub repository soon to illustrate how to create a world with entities and events as well as a youtube video way later.

## Assets : 
Some assets can be puted anywhere you want, like dialogue or maps as you have to give the path, but for most of them their location is important as the engine will search for them in specific folders (may change in the future).
When you run the [setup_environment.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/setup_environment.py) file, it will create the folders and files needed for the engine to work properly, including some explanation files in the [assets/](https://github.com/Nathaanlennon/Build-Synthethis/tree/main/assets) folder to help you understand how to create your own assets.
Please check them for more information about assets.

## Engine : 
The engine is separeted between the core and the ui and are kinda fully independant, so you can create your own ui if you want to. However you will need to recreate some mandatory methods to make it work properly.
The ui is currently based on the curses library, so you can check the [engine/ui/curses_ui.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/engine/ui/curses_ui.py) file to understand how it works and maybe create your own ui based on it.
As I created a specific file for curses ui, you can make another ui based on whatever you want and call this instead of [engine/ui/curses_ui.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/engine/ui/curses_ui.py) in the main.

The game engine works with a modes system, such as exploration mode, dialogue mode, combat mode, etc... Each mode function operate with a commun couple : an input mode in [engine/core/InputSystem.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/engine/core/InputSystem.py) and a render mode in [engine/ui/curses_ui.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/engine/ui/curses_ui.py). Each mode part, either ui or input has a reference in a dictionnary. The name is very important as it's a key used by the universe so make sure that your ui and your input has the same reference name in the dictionnary. 
For example, the exploration mode is referenced as "exploration" in both the ui and input dictionnary. So when the universe switch to exploration mode, both the input system and the ui will switch to their respective exploration mode part.
You can check both the [engine/core/InputSystem.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/engine/core/InputSystem.py) and [engine/ui/curses_ui.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/engine/ui/curses_ui.py) files to understand how the modes work and maybe create your own modes if you want to.
You can create your own modes in [extensions/mode_extensions.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/extensions/mode_extensions.py) and [extensions/ui_extensions.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/extensions/ui_extensions.py) files. Everything is explained in the files.
You can as well rewrite over the pre-existing modes if you wish so, exactly the same way as you add new modes but you put the same key as the pre-existing mode you want to overwrite.

There is a readme file in the [engine/](https://github.com/Nathaanlennon/Build-Synthethis/tree/main/engine/) folder that explain the core architecture of the engine if you want to understand better how it works.

### UI : 
The ui is screen based, what I mean by that is that there is multiple screens where the stuff is drew. By default, you have two screens positionned one on top of each other : the game screen and the info screen.
When something is written, the screen is given and the local coordinates. It means that the coordinates you chose is based on the screen, not the terminal.
For exemple you have a screen that is positionned in 2,4, and you want to write something in the left corner of this screen passed the border, you will have to give 1,1 coordinates and not 3,5.
It means that you can move the screen and everything will stay in place.
The size, the position and the number of screens are fully customisable, however there is no method or acces yet so you have to modify the [engine/ui/curses_ui.py](https://github.com/Nathaanlennon/Build-Synthethis/blob/main/engine/ui/curses_ui.py) file and I am sorry for that. By default the screens dictionnary is located at the [204 line](https://github.com/Nathaanlennon/Build-Synthethis/blob/6534c2b09f6b4a1a1505c0b347f6ffce05dc5ad0/engine/ui/curses_ui.py#L204).
Be aware that the border will be drew on top of everything so if you draw something under it, it will be covered by the border.