Conventions for DAOs
====================
This document describes conventions for the anansi DAOs.

## Settings

All settings, constants and magic strings can be stored in the
settings.py file.

## Return Types and Type Annotations

Using python's optional typing can help make the DAO code mode readable.
Currently, the DAOs' methods should return dictionary representations
of the objects. When writing the type annotations in your module, using
a type alias for the object you're working with can make the code much
more readable:

```python
...
from typing import Dict, Any
...

SeedList = Dict[str, Any]
...
```

Then when you write a method, it can return a dictionary representation
of the desired object and have a type annotation like:

```python
def serialize(cls, row: RowProxy) -> SeedList:
...
```

## DAO Methods

Here are a few possible methods for DAOs for the anansi crawler (where
`SomeObj` is the type alias for whatever object you are dealing with
as described in the previous section):

- `serialize(cls, row: RowProxy) -> SomeObj`: serialize a sqlalchemy
`RowProxy` of `SomeObj` into a python dictionary.
- `list(cls, **kwargs) -> List[SomeObj]`: return a list of dictionaries
representing appropriate instances of `SomeObj` in the database.
- `create(cls, **kwargs) -> SomeObj`: given the necessary kwargs create
a new instance of `SomeObj` and then return it.
- `get(cls, **kwargs) -> SomeObj`: given the necessary kwargs, fetch the
row matching them and return it as a dictionary.
- `update(cls, **kwargs) -> SomeObj`: update the row of `SomeObj`
specified by any relevant unique identifiers with kwargs passed to the
method, and then return the row as a dictionary.
- `delete(cls, **kwargs) -> None`: delete the row specified by kwargs.

The `serialize` method is useful in encapsulating logic that transforms
a SQLAlchemy `RowProxy` object into native python datatypes in the other
methods.
