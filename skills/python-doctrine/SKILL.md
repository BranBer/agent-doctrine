---
name: python-doctrine
description: How to write Python under the doctrine - purpose folders inside the package, modules that grow into packages with __init__ and __all__, utils as subject modules, typed boundaries, thin scripts over importable modules, ruff and pyright. Use when writing or reviewing Python.
---

# Python doctrine

Load `doctrine` first. This pack is what its rules look like in Python. It
specialises rule 1 (a module is a unit; a package is its folder form), rule 9
(type hints at boundaries) and the folder model.

## Layout and purpose folders

```
pyproject.toml
src/
  app/
    __init__.py
    api/          HTTP or CLI entry points - thin, they parse and delegate
    services/     the logic, one unit per concern
    models/       data shapes: dataclasses, pydantic models, enums
    data/         one client module per external source (database, API, files)
    utils/        subject modules: dates.py, money/, text.py
tests/
  test_<unit>.py  or tests/<purpose>/test_<unit>.py, mirroring src/
scripts/          one-off and build scripts, each a thin entry point
```

`src/` layout keeps tests importing the installed package rather than the
working folder, which catches a missing `__init__.py` or a module left out of
the package before users do.

A small project of a handful of files can skip the purpose folders - a module
is already a unit - and add them when the second module of a kind appears.

## A module grows into a package

A module is a unit. When it outgrows 400 code lines, or grows parts only it
uses, it becomes a package of the same name - and callers do not change,
because the package's `__init__.py` exports what the module did:

```
services/billing.py         →    services/billing/
                                   __init__.py     from .invoices import issue_invoice
                                                   from .proration import prorate
                                                   __all__ = ["issue_invoice", "prorate"]
                                   invoices.py
                                   proration.py
```

`from app.services.billing import issue_invoice` works before and after.

**`__all__` is the entry point.** Outsiders import names listed in it; a
leading underscore marks a module or function as private to its package.
Importing `app.services.billing.proration` from outside the package reaches
past the entry - review it as such.

## `utils/` holds subjects

`utils/dates.py`, `utils/money/`, `utils/text.py` - each one subject, each
general purpose: plain values in, plain values out, knowing nothing about any
service. Never `utils/helpers.py` or `utils/misc.py`. A util never imports
from `services/`, `api/` or `data/`.

## Logic free of the framework

FastAPI, Flask, Django, Click and Typer live in `api/`. `services/` and
`models/` import none of them, so they run in a plain test and survive a
framework change. A route parses the request, calls a service, and shapes the
response:

```python
@router.post("/orders")
def create_order(body: OrderIn) -> OrderOut:
    return OrderOut.from_quote(orders.place(body.to_order()))
```

## Types at the boundary

Every public function has type hints on its parameters and return. Data
crossing in from outside (requests, files, environment) is validated where it
enters - pydantic or a dataclass with explicit parsing - and typed from there
on. pyright checks it; give the project a `pyrightconfig.json` or a
`[tool.pyright]` section so `health` treats type errors as failures.

## Scripts are entry points only

```python
# scripts/build_audio.py
from app.audio import build_all

if __name__ == "__main__":
    build_all()
```

The work lives in an importable module, so it can be tested and reused; the
script only calls it. A script that holds 200 lines of logic under
`if __name__ == "__main__":` cannot be imported, tested or split.

## Configuration

Read settings once, at startup, into a typed object (pydantic-settings or a
dataclass), and pass that object in. Nothing reads `os.environ` deep inside a
service.

## Health

`health` runs ruff (with bandit's security rules and complexity), pyright,
vulture for unused code, an import-cycle scan, duplication, sizes, secrets and
dependency scans. A project's own ruff config is used when it has one.
