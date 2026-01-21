How to use the engine : 
You must launch setup_environment.py at first, it may show an error but it's normal. The setup will create the necessary files and folders for the engine to work properly.
It will also provide you with explanation files for the different assets in assets/ folder. Read them to understand how to create your own assets and feel free to check the git hub repository for a simple exemple.
Then, you can start creating your game, everything is explained in the files created by setup_environment.py


# Core architecture — concise plan


Purpose: describe how core components interact at a glance.

1. Structure (important files)
   1. `engine/core/base.py` — base types (Player, Entities).
   2. `engine/core/CombatSystem.py` — enemy loading and fight management.
   3. `engine/core/DialogueSystem.py` — dialogue state and lines.
   4. `engine/core/EventSystem.py` — event dispatch / listeners.
   5. `engine/core/InputSystem.py` — translates input into events.
   6. `engine/core/ItemManager.py` — items inventory, persistence.
   7. `engine/core/logging_setup.py` — provides `logger`.
   8. `engine/ui/curses_ui.py` — UI, renders state and sends input.

2. High\-level interactions (who talks to who)
   1. User -> UI (`engine/ui/curses_ui.py`) -> `InputSystem`.
   2. `InputSystem` -> pushes events to `EventSystem`.
   3. `EventSystem` -> dispatches to subscribers: `CombatSystem`, `DialogueSystem`, `ItemManager`, `base.Player`, UI.
   4. `CombatSystem` -> reads enemy definitions from `assets/enemies/enemies.json` (via `load_enemies_list`), creates `Enemy` instances, manages `fighters`.
   5. `DialogueSystem` -> receives trigger events, updates dialogue state, notifies UI or EventSystem for branch choices.
   6. `ItemManager` -> responds to pickup/use events, updates `Player` inventory and persists as needed.
   7. All components log through `logger` from `engine/core/logging_setup.py`.

3. Data flow examples (short)
   1. Start combat: UI -> Input -> EventSystem emits `start_combat` -> `CombatSystem` loads enemy data and appends fighters -> UI renders combat state.
   2. Pick item: UI selects item -> Input -> EventSystem emits `item_pick` -> `ItemManager` updates Player -> EventSystem emits `inventory_changed`.

4. File loading / execution note
   - Relative paths (e.g. `assets/enemies/enemies.json`) are resolved against the current working directory. Running a module directly from `engine/core` may make those paths fail even if files exist in the project root.