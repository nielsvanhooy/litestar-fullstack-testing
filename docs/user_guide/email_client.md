Phantom NMS has an internal Email-Client.
Setup can be done trough the use of environmental parameters
it can be run as a background process.

lala example stuff

```python
from starlite import get, Starlite


@get(["/", "/sub-path"])
def handler() -> None:
    ...


app = Starlite(route_handlers=[handler])
```

included functionality in the API to blacklist certain domains.
