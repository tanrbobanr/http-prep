import sys
sys.path.append(".")
from src import httpprep


h = httpprep.Headers()
h.Accept = "*/*"
h.Content_Type = "application/json"

u = httpprep.URL()
u.components.queries["v"] = 1
u.components.queries["v"] = 2
u.components.domain = "test"
print(u.build())
print(h.format_lines())
