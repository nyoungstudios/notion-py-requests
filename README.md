<h1 align="center">Notion Python Requests</h1>

[![tests](https://github.com/nyoungstudios/notion-py-requests/actions/workflows/python_test.yml/badge.svg)](https://github.com/nyoungstudios/notion-py-requests/actions/workflows/python_test.yml)
[![codecov](https://codecov.io/gh/nyoungstudios/notion-py-requests/branch/main/graph/badge.svg?token=9M2UZ4WJ36)](https://codecov.io/gh/nyoungstudios/notion-py-requests)
[![Gitpod ready](https://img.shields.io/badge/Gitpod-ready-blue?logo=gitpod)](https://gitpod.io/#https://github.com/nyoungstudios/notion-py-requests)
[![PyPI version shields.io](https://img.shields.io/pypi/v/notion-requests.svg)](https://pypi.python.org/project/notion-requests/)
[![PyPI license](https://img.shields.io/pypi/l/notion-requests.svg)](https://pypi.python.org/project/notion-requests/)

This is a mostly unopinionated Python client for Notion's API using the Python Requests library. This means that the
structure of functions and usage of this client library is almost identical to the official
[Notion JavaScript SDK](https://developers.notion.com/reference/intro). The only opinionated part is that this client
library automatically handles pagination, so you do not have to.

## Why?
Why does this library exist when there are other Python Notion clients available?
- [`notion-py`](https://github.com/jamalex/notion-py) - This reverse engineers Notion's internal API and was created
    before Notion officially released their public beta API
- [`notion-sdk-py`](https://github.com/ramnes/notion-sdk-py) - This uses Notion's official public beta API and
    uses `httpx` internally to make the requests. And it only supports Python 3.7 or later. And supports sync and async
    requests.

But the real reason why this library exists was because I was testing `notion-sdk-py` and was having trouble making a
database query with filtering. So, I ended up writing this client, and it was not until I wrote the unittests that I
figured out the original problem. So, you should probably use `notion-sdk-py` instead, but why delete this perfectly
good code that I wrote. You might prefer to use this client library over `notion-sdk-py` if you are already using
`requests` (and don't) want another dependency. Or you need Python 3.6 support. Or you like to have automatic
pagination.

## Install

```shell
pip install notion-requests
```

## Quickstart

```python
import json
import os
from notion_requests import Client

# initialize a Notion client
notion = Client(os.environ['NOTION_TOKEN'])

# get current user
response = notion.users.me()
print(json.dumps(response, indent=2))
```

```json
{
  "object": "user",
  "id": "16d84278-ab0e-484c-9bdd-b35da3bd8905",
  "name": "pied piper",
  "avatar_url": null,
  "type": "bot",
  "bot": {
    "owner": {
      "type": "user",
      "user": {
        "object": "user",
        "id": "5389a034-eb5c-47b5-8a9e-f79c99ef166c",
        "name": "christine makenotion",
        "avatar_url": null,
        "type": "person",
        "person": {
          "email": "christine@makenotion.com"
        }
      }
    }
  }
}
```

```python
query = {
    'database_id': '897e5a76-ae52-4b48-9fdf-e71f5945d1af',
    'filter': {
        'or': [
            {
                'property': 'In stock',
                'checkbox': {
                    'equals': True
                }
            },
            {
                'property': 'Cost of next trip',
                'number': {
                    'greater_than_or_equal_to': 2
                }
            }
        ]
    },
    'sorts': [
        {
            'property': 'Last ordered',
            'direction': 'ascending'
        }
    ]
}

# query a database
# it returns a generator object since this api endpoint supports pagination
for response in notion.databases.query(**query):
    for result in response['results']:
        print(json.dumps(result, indent=2))
```

```json
{
  "object": "page",
  "id": "2e01e904-febd-43a0-ad02-8eedb903a82c",
  "created_time": "2020-03-17T19:10:04.968Z",
  "last_edited_time": "2020-03-17T21:49:37.913Z",
  "parent": {
    "type": "database_id",
    "database_id": "897e5a76-ae52-4b48-9fdf-e71f5945d1af"
  },
  "archived": false,
  "url": "https://www.notion.so/2e01e904febd43a0ad028eedb903a82c",
  "properties": {
    "Recipes": {
      "id": "Ai`L",
      "type": "relation",
      "relation": [
        {
          "id": "796659b4-a5d9-4c64-a539-06ac5292779e"
        },
        {
          "id": "79e63318-f85a-4909-aceb-96a724d1021c"
        }
      ]
    },
    "Cost of next trip": {
      "id": "R}wl",
      "type": "formula",
      "formula": {
        "type": "number",
        "number": 2
      }
    },
    "Last ordered": {
      "id": "UsKi",
      "type": "date",
      "date": {
        "start": "2020-10-07",
        "end": null
      }
    },
    "In stock": {
      "id": "{>U;",
      "type": "checkbox",
      "checkbox": false
    }
  }
}
...
```

## Error Handling
```python
import requests

try:
    # try to retrieve a database that doesn't exist
    response = notion.databases.retrieve('897e5a76ae524b489fdfe71f5945d1af')
except requests.exceptions.HTTPError as e:
    # prints json output from failed request
    print(json.dumps(e.response.json(), indent=2))
```

```json
{
  "object": "error",
  "status": 404,
  "code": "object_not_found",
  "message": "Could not find database with ID: 897e5a76-ae52-4b48-9fdf-e71f5945d1af."
}
```

## More Documentation
The example data in the above quickstart was taken directly from Notion's API reference and adapted for this client
library. For more documentation about which functions to use and the inputs of this client library, you can check out
the [official Notion JavaScript SDK documentation](https://developers.notion.com/reference/intro).
