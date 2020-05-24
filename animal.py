import config

class Animal:
    def __init__(self, height, weight, age, num_of_legs, tail):
        self.height = height  # cm
        self.weight = weight  # kg
        self.age = age  # 1 - 300
        self.num_of_legs = num_of_legs  # 0 - 10
        self.tail = tail  # true/false

    # sort order by fields: height->weight->age->num of legs
    # <=
    def __le__(self, other):
        for att in config.list:
            if getattr(self,att) < getattr(other, att):
                return True
            elif getattr(self,att) > getattr(other, att):
                return False

    # >=
    def __ge__(self, other):  # >=
        for att in config.list:
            if getattr(self,att) > getattr(other, att):
                return True
            elif getattr(self, att) < getattr(other, att):
                return False

    # <
    def __lt__(self, other):  # <
        for att in config.list:
            if getattr(self, att) < getattr(other, att):
                return True
            elif getattr(self, att) > getattr(other, att):
                return False



    # >
    def __gt__(self, other):  # >
        for att in config.list:
            if getattr(self, att) > getattr(other, att):
                return True
            elif getattr(self, att) < getattr(other, att):
                return False

    def __repr__(self):
        return '(height: {0}, weight: {1}, age: {2}, num_of_legs: {3}, tail: {4})'. \
            format(self.height, self.weight, self.age, self.num_of_legs, self.tail)

    # sort order by fields: height->weight->age->num of legs