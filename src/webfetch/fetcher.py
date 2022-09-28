import urllib.parse, typing, requests


class OverloadList(list):
    """A list subclass.

    """


class MultiDict(dict):
    def __init__(self, *args, **kwargs) -> None:
        """Similar to a dictionary, multiple keys default to nested dictionaries.

        Essentially:
        ```
        # this:
        v = {}
        v["a"] = {}
        v["a"]["b"] = {}
        v["a"]["b"]["c"] = "d"
        print(v)
        >>> {'a': {'b': 'c'}}

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


class OverloadDict(dict):
    """Similar to a dictionary, but turns multiple occurances of a key into a list of
    values intead of overwriting.

    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    

    def __setitem__(self, __k: str, __v: str) -> None:
        if __k in self and isinstance(self[__k], OverloadList):
            return self[__k].append(__v)
        if __k in self:
            return super().__setitem__(__k, OverloadList([self[__k], __v]))
        return super().__setitem__(__k, __v)


def _format_protocol(protocol: str, separator: str) -> str:
    return protocol + separator if protocol else ""


def _format_subdomain(subdomain: str, separator: str) -> str:
    return subdomain + separator if subdomain else ""


def _format_top_level_domain(top_level_domain: str, separator: str) -> str:
    return separator + top_level_domain if top_level_domain else ""


def _format_param(k: str, v: str, equator: str) -> str:
    """Formats a single URL query parameter.
    
    """
    return f"{k}{equator}{urllib.parse.quote(str(v))}"


def _format_parameters(no_value_indicator: typing.Any, parameters: OverloadDict, separator: str, joiner: str, equator: str) -> str:
    """Format an OverloadDict into a query string.
    
    """
    if not parameters:
        return ""
    formatted_query_parameters = []
    for k, v in parameters.items():
        if v == no_value_indicator:
            continue
        if isinstance(v, OverloadList):
            formatted_query_parameters.extend([_format_param(k, v_, equator) for v_ in v])
            continue
        formatted_query_parameters.append(_format_param(k, v, equator))
    return f"{separator}{joiner.join(formatted_query_parameters)}" if formatted_query_parameters else ""


def _clean_dict(no_value_indicator: typing.Any, target: dict[typing.Any, dict]) -> dict | None:
    if not target:
        return {}
    new = {}
    for k1, v1 in target.items():
        if type(v1) == dict:
            temp = {}
            for k2, v2 in v1.items():
                if v2 != no_value_indicator:
                    temp[k2] = v2
            if temp:
                new[k1] = temp
            continue
        if type(v1) != no_value_indicator:
            new[k1] = v1
    return new


def _format_path(paths: list[str], separator: str) -> str:
    return f"{separator}{separator.join(paths)}" if paths else ""


def _format_port(no_value_indicator: typing.Any, port: int | str, separator: str) -> str:
    return "" if port == no_value_indicator else f"{separator}{str(port)}" if port else ""


def _format_fragment(no_value_indicator: typing.Any, fragment: str, separator: str) -> str:
    return "" if fragment == no_value_indicator else f"{separator}{fragment}" if fragment else ""


def _make_request(no_value_indicator: typing.Any, method: str, url: str, kwargs1: dict, kwargs2: dict) -> requests.Response:
    _kwargs = {"method": method, "url": url}
    _kwargs.update(_clean_dict(no_value_indicator, kwargs1))
    _kwargs.update(kwargs2)
    return requests.request(**_kwargs)


class PreparedFetch:
    def __init__(
        self,
        *,
        no_value_indicator     : typing.Any   = ...,
        protocol               : str          = "https",
        protocol_separator     : str          = "://",
        domain_separator       : str          = ".",
        subdomain              : str          = "www",
        domain                 : str          = None,
        top_level_domain       : str          = "com",
        port_separator         : str          = ":",
        port                   : int | str    = None,
        path_separator         : str          = "/",
        paths                  : list[str]    = ...,
        query_string_separator : str          = "?",
        query_string_joiner    : str          = "&",
        query_string_equator   : str          = "=",
        fragment_separator     : str          = "#",
        fragment               : str          = None
    ) -> None:
        """Prepare, then execute an http request.

        Arguments
        ---------
        no_value_indicator : any, default=...
            Any value in `parameters` or `request_kwargs` that equal this value will be
            ignored when constructing (and later executing) the request.
        protocol : str, default="https"
        protocol_separator : str, default="://"
            Separates the protocol and subdomain.
        domain_separator : str, default="."
            Separates the subdomain, domain, and top level domain.
        subdomain : str, default="www"
        domain : str, default=None
        top_level_domain : str, default="com"
        port_separator : str, default=":"
            Separates the full domain and the port.
        port : int or str, default=None
        path_separator : str, default="/"
            Separates the path entries.
        paths : list of str, default=...,
            The list (in order) of paths to be joined with `path_separator`.
        query_string_separator : str, default="?"
            Separates the end of the domain / path / port and the query string.
        query_string_joiner : str, default="&"
            Separates multiple query key-value pairs.
        query_string_equator : str, default="="
            Separates query string keys and values.
        fragment_separator : str, default="#"
            Separates the end of the domain / path / port / query string and the
            fragment.
        fragment : str, default=None
    
        Attributes
        ----------
        parameters : OverloadDict
            The query parameters used to construct the query string. Values will be
            cleaned (i.e. any value that is equal to `no_value_indicator` will be
            removed).
        request_kwargs : MultiDict
            The dict used to hold extra kwargs for the request. Values will be
            cleaned (i.e. any value that is equal to `no_value_indicator` will be
            removed).

            Multiple keys may be passed into this parameter at once, which will create
            empty `dict` objects for each key that is not present (and is not the
            recipient of the value). For example:
            ```
            request_kwargs["headers", "cookie"] = "..."
            print(request_kwargs)
            >>> {'headers': {'cookie' : '...'}}
            ```
        
        """
        self.no_value_indicator     = no_value_indicator
        self.protocol               = protocol
        self.protocol_separator     = protocol_separator
        self.domain_separator       = domain_separator
        self.subdomain              = subdomain
        self.domain                 = domain
        self.top_level_domain       = top_level_domain
        self.port_separator         = port_separator
        self.port                   = port
        self.path_separator         = path_separator
        self.paths                  = paths if paths != ... else []
        self.query_string_separator = query_string_separator
        self.query_string_joiner    = query_string_joiner
        self.query_string_equator   = query_string_equator
        self.parameters             = OverloadDict()
        self.fragment_separator     = fragment_separator 
        self.fragment               = fragment
        self.request_kwargs         = MultiDict()
    

    @property
    def url(self) -> str:
        """Formats the given URL information into a URL.
        
        """
        protocol         = _format_protocol(self.protocol, self.protocol_separator)
        subdomain        = _format_subdomain(self.subdomain, self.domain_separator)
        top_level_domain = _format_top_level_domain(self.top_level_domain, self.domain_separator)
        port             = _format_port(self.no_value_indicator, self.port, self.port_separator)
        path             = _format_path(self.paths, self.path_separator)
        parameters       = _format_parameters(self.no_value_indicator, self.parameters, self.query_string_separator, self.query_string_joiner, self.query_string_equator)
        fragment         = _format_fragment(self.no_value_indicator, self.fragment, self.fragment_separator)
        return f"{protocol}{subdomain}{self.domain}{top_level_domain}{port}{path}{parameters}{fragment}"


    def request(self, method: str, **kwargs) -> requests.Response:
        """Run a request of given method.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`. The same applies for the
        `method` key.

        """
        return _make_request(self.no_value_indicator, method, self.url, self.request_kwargs, kwargs)


    async def async_request(self, method: str, **kwargs) -> requests.Response:
        """Run a request of given method asynchronously.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`. The same applies for the
        `method` key.

        """
        return _make_request(self.no_value_indicator, method, self.url, self.request_kwargs, kwargs)


    def get(self, **kwargs) -> requests.Response:
        """Run a GET request.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "GET", self.url, self.request_kwargs, kwargs)


    async def async_get(self, **kwargs) -> requests.Response:
        """Run a GET request asynchronously.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "GET", self.url, self.request_kwargs, kwargs)


    def options(self, **kwargs) -> requests.Response:
        """Run an OPTIONS request.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "OPTIONS", self.url, self.request_kwargs, kwargs)


    async def async_options(self, **kwargs) -> requests.Response:
        """Run an OPTIONS request asynchronously.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "OPTIONS", self.url, self.request_kwargs, kwargs)


    def head(self, **kwargs) -> requests.Response:
        """Run a HEAD request.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "HEAD", self.url, self.request_kwargs, kwargs)


    async def async_head(self, **kwargs) -> requests.Response:
        """Run a HEAD request asynchronously.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "HEAD", self.url, self.request_kwargs, kwargs)


    def post(self, **kwargs) -> requests.Response:
        """Run a POST request.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "POST", self.url, self.request_kwargs, kwargs)


    async def async_post(self, **kwargs) -> requests.Response:
        """Run a POST request asynchronously.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "POST", self.url, self.request_kwargs, kwargs)


    def put(self, **kwargs) -> requests.Response:
        """Run a PUT request.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "PUT", self.url, self.request_kwargs, kwargs)


    async def async_put(self, **kwargs) -> requests.Response:
        """Run a PUT request asynchronously.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "PUT", self.url, self.request_kwargs, kwargs)


    def patch(self, **kwargs) -> requests.Response:
        """Run a PATCH request.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "PATCH", self.url, self.request_kwargs, kwargs)


    async def async_patch(self, **kwargs) -> requests.Response:
        """Run a PATCH request asynchronously.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "PATCH", self.url, self.request_kwargs, kwargs)


    def delete(self, **kwargs) -> requests.Response:
        """Run a DELETE request.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "DELETE", self.url, self.request_kwargs, kwargs)


    async def async_delete(self, **kwargs) -> requests.Response:
        """Run a DELETE request asynchronously.
        
        `kwargs` will be passed into the `requests.request` call.
        
        Notes
        -----
        Any key in `PreparedFetch.request_kwargs` that is present in `kwargs` will be
        overridden by the corresponding value in `kwargs`. Similarly, if the `url` key
        is used in `kwargs`, the constructed url (`PreparedFetch.url`) will be
        overridden by the corresponding value in `kwargs`.

        """
        return _make_request(self.no_value_indicator, "DELETE", self.url, self.request_kwargs, kwargs)
