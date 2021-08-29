class Cache(dict):

    # not used right now. hope i use it after i fully move to tortoise

    def add_key(self, key, value):
        self[key] = value
        return self

    def del_key(self, key):
        if key in self:
            del self[key]
            return self
        raise RuntimeError(f"Key {key} is not in cache")

    def exists(self, key):
        return key in self.keys()


def create_new_cache(initial_data: dict):
    new = Cache()
    new.update(initial_data)
