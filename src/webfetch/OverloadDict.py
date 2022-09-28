import typing


class OverloadList(list):
    """A list subclass.

    """


class OverloadDict(dict[typing.Any, OverloadList]):
    """Similar to a dictionary, but turns multiple occurances of a key into a list of
    values intead of overwriting the previous value.

    Additionally, multiple keys and values can be set at once, for example:
    ```
    d = OverloadDict()
    d["a", "b", "c"] = 1, 2, 3
    ```

    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    

    def _set_item(self, __k, __v) -> None:
        if __k not in self:
            return super().__setitem__(__k, OverloadList([__v]))
        return self[__k].append(__v)


    def __setitem__(self, __k, __v) -> None:
        if type(__k) == tuple and type(__v) not in [tuple, list]:
            raise TypeError("multiple values must be used if assigning multiple keys")
        if type(__k) == tuple:
            for k, v in zip(__k, __v):
                self._set_item(k, v)
            return
        return self._set_item(__k, __v)
