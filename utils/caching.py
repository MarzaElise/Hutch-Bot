class Cache(dict):

    # not used right now. hope i use it after i fully move to tortoise
    # this class has some retarded methods like add_key but only i use it so not much of a problem

    @classmethod
    def from_dict(cls, other: dict):
        return cls(other)

    def insert(self, key, value):
        # this method allows you to do something like add_key([1, 2, 3], 4) and it would add 1, 2 and 3 keys
        # with the 4 value this would indeed fuck up the create_opposite_copy method by overriding keys
        # for example, {1: 2, 3: 4, 10: 9, 11: 9} would try to turn into {2: 1, 4: 3, 9: 10, 9: 11} and end up
        # deleting the 9: 10 key value pair
        if isinstance(key, list):
            for actual in key:
                self.add_key(actual, value)
        else:
            self[key] = value
        return self

    add_key = insert

    def delete(self, key):
        if key in self:
            del self[key]
            return self
        raise RuntimeError(f"Key {key} is not in cache")

    def get_or_create(self, key, value):
        """Return the value of the given key if found else create new key and return the value"""
        if key in self.keys():
            return self[key]
        # key doesnt exist so create it
        return self.add_key(key, value)

    def contains(self, key) -> bool:
        return key in self.keys()

    def reverse(self):
        """
        Create a copy of the current dict with its keys and values reversed.

        For example, doing....

        ``Cache({1: 2}).create_opposite_copy()``

        would return

        ``Cache({2: 1})``

        Gets fucked up when multiple values are the same.
        """
        new = {value: key for key, value in self.items()}
        return create_new_cache(new)

    def __str__(self):
        return f"Cache({super().__str__()})"


def create_new_cache(initial_data: dict=None):
    return Cache() if not initial_data else Cache.from_dict(initial_data)
