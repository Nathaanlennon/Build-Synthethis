import os
from engine.core.logging_setup import logger

SAVES_DIR = "saves"

def choose_universe():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)
        logger.info(f"Created saves directory: {SAVES_DIR}")

    universes = [d for d in os.listdir(SAVES_DIR)
                 if os.path.isdir(os.path.join(SAVES_DIR, d))]

    print("Available universes:")
    for i, u in enumerate(universes, start=1):
        print(f"{i}. {u}")
    print("0. Create new universe")

    choice = input("Select a universe: ").strip()
    if choice == "0":
        new_universe = input("Enter new universe name: ").strip()
        universe_path = os.path.join(SAVES_DIR, new_universe)
        os.makedirs(universe_path, exist_ok=True)
        logger.info(f"Universe created: {new_universe}")
        return new_universe
    else:
        try:
            index = int(choice) - 1
            selected_universe = universes[index]
            logger.info(f"Universe loaded: {selected_universe}")
            return selected_universe
        except (ValueError, IndexError):
            logger.warning("Invalid universe selection, retrying...")
            print("Invalid choice, try again.")
            return choose_universe()


def choose_player(universe_name):
    universe_path = os.path.join(SAVES_DIR, universe_name)
    players = [d for d in os.listdir(universe_path)
               if os.path.isdir(os.path.join(universe_path, d))]

    print(f"Available players in '{universe_name}':")
    for i, p in enumerate(players, start=1):
        print(f"{i}. {p}")
    print("0. Create new player")

    choice = input("Select a player: ").strip()
    if choice == "0":
        new_player = input("Enter new player name: ").strip()
        player_path = os.path.join(universe_path, new_player)
        os.makedirs(player_path, exist_ok=True)
        logger.info(f"Player created: {new_player} in universe {universe_name}")
        return new_player
    else:
        try:
            index = int(choice) - 1
            selected_player = players[index]
            logger.info(f"Player loaded: {selected_player} from universe {universe_name}")
            return selected_player
        except (ValueError, IndexError):
            logger.warning(f"Invalid player selection in universe {universe_name}, retrying...")
            print("Invalid choice, try again.")
            return choose_player(universe_name)
