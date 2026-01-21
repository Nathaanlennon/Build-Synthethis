#this module defines various input extension modes for the application.

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
