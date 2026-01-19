class EventSystem:
    def __init__(self, world):
        self.world = world
        self.events = []



    def add_event(self, event):
        self.events.append(event)

    def remove_event(self, event):
        if event.position in self.events:
            del self.events[event.position]

    def get_event(self, position):
        for event in self.events:
            if event.position == position:
                return event
        return None

    def update(self, player, action):
        for event in self.events:
            if event.should_trigger(action):
                event.activation()
