class EdgeDetector:
    def __init__(self):
        self.prev_state = False

    def update(self, current_state: bool) -> bool:
        """Returns True only on the rising edge (when state goes from False to True)."""
        triggered = current_state and not self.prev_state
        self.prev_state = current_state
        return triggered
