import time


class RefreshController:
    def __init__(self, cooldown=10):
        self.cooldown = cooldown
        self.last_refresh = 0

    def can_refresh(self):
        current_time = time.time()

        return current_time - self.last_refresh >= self.cooldown

    def refresh(self):
        if not self.can_refresh():
            remaining = self.cooldown - (
                time.time() - self.last_refresh
            )

            print(
                f"Please wait {remaining:.1f} "
                "seconds before refreshing again."
            )

            return False

        self.last_refresh = time.time()

        return True
