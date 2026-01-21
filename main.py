
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

        