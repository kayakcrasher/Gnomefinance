class DApp:
    def __init__(self, name):
        self.name = name
        self.connected = False

    def connect(self):
        self.connected = True
        print(f"{self.name} connected.")

    def disconnect(self):
        self.connected = False
        print(f"{self.name} disconnected.")

    def status(self):
        if self.connected:
            print(f"{self.name}: Connected")
        else:
            print(f"{self.name}: Disconnected")
