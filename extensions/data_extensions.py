# this is where all the additionnal data will be put, all the data that is not originally in the game-engine. 
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
    
}