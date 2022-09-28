class MultiDict(dict):
    def __init__(self, *args, **kwargs) -> None:
        """Similar to a dictionary, but multiple keys default to nested dictionaries.

        Essentially:
        ```
        # this:
        v = {}
        v["a"] = {}
        v["a"]["b"] = {}
        v["a"]["b"]["c"] = "d"
        print(v)
        >>> {'a': {'b': {'c': 'd'}}}

        # turns into this:
        v = MultiDict()
        v["a", "b", "c"] = "d"
        print(v)
        >>> {'a': {'b': {'c': 'd'}}}
        ```
        
        """
        super().__init__(*args, **kwargs)
    

    def __setitem__(self, __k, __v, *, _pass = None) -> None:
        if _pass is None:
            _pass = self
        if type(__k) == tuple and len(__k) > 1:
            if __k[0] not in _pass:
                _pass[__k[0]] = {}
            return self.__setitem__(__k[1:], __v, _pass = _pass[__k[0]])
        if type(__k) == tuple:
            [__k] = __k
        return dict.__setitem__(_pass, __k, __v)
