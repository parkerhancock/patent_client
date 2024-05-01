# Async / Await Support

Patent Client optionally supports asyncio. Introduced in v.5, there are two alternative ways of using
Patent Client, one of which is entirely asynchronous, and the other synchronous. The two do not mix,
you should stick with one or the other, and then use the appropriate syntax.

## Synchronous Operation

To use the synchronous interface, just import models the normal way:

```python
from patent_client import USApplication
```

All operations are synchronous. No async/await syntax is needed.
Managers can be iterated over like a normal list:

```python
for app in USApplication.objects.filter(first_named_applicant="Tesla"):
    # do something
```

Calls to .get and .first are synchronous:

```python
app = USApplication.objects.get("16123456")
app = USApplication.objects.first(first_named_applicant="Tesla")
```

Related objects are also synchronous

```python
app = USApplication.objects.get("16123456")
app.patent
```

## Async Operation

To use the asynchronous interface, import from patent_client._async

```python
from patent_client._async import USApplication
```

Now, every call that could potentially create network activity is asynchronous.

Managers can be iterated over using async syntax:

```python
async for app in USApplication.objects.filter(first_named_applicant="Tesla"):
    # do something

[app async for app in USApplication.objects.filter(first_named_applicant="Tesla")]
```

Calls to .get and .first are asynchronous:

```python
app = await USApplication.objects.get("16123456")
app = await USApplication.objects.first(first_named_applicant="Tesla")
```

Related objects are also asynchronous, including related objects that may produce another manager

```python
app = await USApplication.objects.get("16123456")
patent = await app.patent
```

