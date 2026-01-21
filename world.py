from engine.core.base import World, Entity, Event, NPC

def TestWorld(data):
    self = World(data, "TestWorld", "assets/maps/exemple_map.txt")
    return self