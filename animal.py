
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
        if self.height < other.height:
            return True
        elif self.height > other.height:
            return False
        else:  # equals, checking weight
            if self.weight < other.weight:
                return True
            elif self.weight > other.weight:
                return False
            else:  # equals, checking age
                if self.age < other.age:
                    return True
                elif self.age > other.age:
                    return False
                else:  # equals, checking num of legs
                    return self.num_of_legs < other.num_of_legs

    # <
    def __lt__(self, other):  # <
        if self.height < other.height:
            return True
        elif self.height > other.height:
            return False
        else:  # equals, checking weight
            if self.weight < other.weight:
                return True
            elif self.weight > other.weight:
                return False
            else:  # equals, checking age
                if self.age < other.age:
                    return True
                elif self.age > other.age:
                    return False
                else:  # equals, checking num of legs
                    return self.num_of_legs < other.num_of_legs

    # >=
    def __ge__(self, other):  # >=
        if self.height > other.height:
            return True
        elif self.height < other.height:
            return False
        else:  # equals, checking weight
            if self.weight > other.weight:
                return True
            elif self.weight < other.weight:
                return False
            else:  # equals, checking age
                if self.age > other.age:
                    return True
                elif self.age < other.age:
                    return False
                else:  # equals, checking num of legs
                    return self.num_of_legs > other.num_of_legs

    # >
    def __gt__(self, other):  # >
        if self.height > other.height:
            return True
        elif self.height < other.height:
            return False
        else:  # equals, checking weight
            if self.weight > other.weight:
                return True
            elif self.weight < other.weight:
                return False
            else:  # equals, checking age
                if self.age > other.age:
                    return True
                elif self.age < other.age:
                    return False
                else:  # equals, checking num of legs
                    return self.num_of_legs > other.num_of_legs

    def __repr__(self):
        return '(height: {0}, weight: {1}, age: {2}, num_of_legs: {3}, tail: {4})'.\
            format(self.height, self.weight, self.age, self.num_of_legs, self.tail)

