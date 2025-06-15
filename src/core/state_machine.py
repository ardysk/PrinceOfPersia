class State:
    def __init__(self, game): self.game = game
    def handle_event(self, event): pass
    def update(self, dt):          pass
    def draw(self, screen):        pass

class StateMachine:
    def __init__(self, start_state: State):
        self.state = start_state
    def change(self, new_state: State):
        self.state = new_state
