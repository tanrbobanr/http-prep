# A tool to easily create complicated and dynamic prepared http requests.

## Install
`pip install web-fetch`

## Important note
Although it is not incredibly intensive, if you are making a simple request, you should probably stick with `requests`. This is meant more for the dynamic construction of complicated requests. Below is an example of a situation where it would **not** be necessary to use this:
```py
def example(paths = None):
    paths = paths or []
    return "http://example.com" + ("/" if paths else "") + "/".join(paths)
```

## Example usage
```py
# GOAL:
# Create a function to send a POST request to
# http://example.com/a/b with optional port, query
# parameters, and fragment. Additionally, include
# Authorization and Content-Type headers.

from webfetch import PreparedFetch


def example(port = "IGNORE_THIS", fragment = "IGNORE_THIS", query_parameters: list[tuple[str, str]] = None):
    # create object with basic URL information
    prepped = PreparedFetch(
        no_value_indicator = "IGNORE_THIS",
        protocol = "http",
        subdomain = None,
        domain = "example", # we don't include a top-level domain because it is "com" by default
        port = port,
        paths = ["a", "b"],
        fragment = fragment
    )
    # set the headers
    prepped.request_kwargs["headers", "Authorization"] = "abc123"
    prepped.request_kwargs["headers", "Content-Type"] = "application/json"
    prepped.request_kwargs["headers", "Referrer"] = "IGNORE_THIS"
    # set the parameters
    for (key, value) in query_parameters:
        # we don't need to worry about having multiple
        # of the same value overwrite eachother
        prepped.parameters[key] = value
    return prepped


PREPPED = example(port = "8008", fragment = "FRAG", query_parameters=[
    ("arg1", "ONE"),
    ("arg2", "TWO"),
    ("arg2", "2"),
    ("arg3", "IGNORE_THIS")
])
print(PREPPED.url)
>>> 'http://example.com:8008/a/b?arg1=ONE&arg2=TWO&arg2=2#FRAG'
print(PREPPED.request_kwargs)
>>> {'headers': {'Authorization': 'abc123', 'Content-Type': 'application/json'}}
print(type(PREPPED.post()))
>>> <class 'requests.Response'>
```
