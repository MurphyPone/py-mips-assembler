class Address():
    def __init__(self, x=0x0):
        self.address = x

    def increment(self, amt):
        self.address += amt

    def set_address(self, x):
        self.address = x

    def __repr__(self):
        return str(self.address)
    