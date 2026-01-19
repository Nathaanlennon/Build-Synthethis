import os

path = os.path.join(os.path.dirname(__file__), "..")

# Dossiers obligatoires
required_dirs = [
    "extensions"
]

for d in required_dirs:
    os.makedirs(os.path.join(path, d), exist_ok=True)

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


input_file= os.path.join(path, "extensions/data_extensions.py")
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