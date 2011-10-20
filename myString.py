# I needed a string object that had the write function
class StringWithWrite:                  # todo subclass str?
    def __init__(self):
        self.s = ""
        
    def write(self, s):
        self.s += s

    def __str__(self):
        return self.s
