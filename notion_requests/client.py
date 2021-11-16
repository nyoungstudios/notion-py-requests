"""
A client for Notion's API using Requests
"""

import requests

from typing import Any, Callable, Generator


class Client:
    _BASE_URL = 'https://api.notion.com'
    _API_VERSION = 'v1'
    _NOTION_VERSION = '2021-08-16'

    def __init__(
        self,
        auth: str,
        notion_version: str = _NOTION_VERSION,
        api_version: str = _API_VERSION
    ):
        """
        Initializes a Notion client object to make requests to the Notion API.
        See https://developers.notion.com/reference/intro for more information

        :param auth: The Notion authorization token
        :param notion_version: The Notion version
        :param api_version: The api version
        """
        self._headers = {
            'Authorization': f'Bearer {auth}',
            'Notion-Version': notion_version,
            'Content-Type': 'application/json'
        }
        self._url_prefix = f'{self._BASE_URL}/{api_version}'

        self.databases = Databases(self)
        self.pages = Pages(self)
        self.blocks = Blocks(self)
        self.users = Users(self)
        self.search = Search(self)

    def request(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        """
        Makes a request to the Notion API with the correct Authorization headers and Notion Version

        :param method: GET, POST, PATCH, or DELETE
        :param endpoint: the path of the endpoint that comes after the base url and version
        :param kwargs: any other kwargs
        :return: A requests response object
        """
        url = f'{self._url_prefix}/{endpoint}'
        r = requests.request(method, url, headers=self._headers, **kwargs)

        r.raise_for_status()

        return r

    @staticmethod
    def paginate(fn: Callable, data: dict, *args: Any, **kwargs: Any) -> Generator[dict, None, None]:
        """
        Automatically paginates the output

        :param fn: the function to call
        :param data: the requests json data
        :param args: any of the function's arguments
        :param kwargs: any of the function's kwargs
        :return: A generator object which each item as the request's json data
        """
        yield data
        if data['has_more']:
            if kwargs is not None:
                kwargs['start_cursor'] = data['next_cursor']
            else:
                kwargs = {'start_cursor': data['next_cursor']}
            yield fn(*args, **kwargs)


class Endpoint:
    def __init__(self, client: Client):
        """
        Initializes a Notion Endpoint object

        :param client: A Notion object
        """
        self._client = client
        self._name = self.__class__.__name__.lower()

    def _build_endpoint(self, action: str) -> str:
        """
        Builds the endpoint by prepending the class name to action

        :param action: The part the comes after the name in the endpoint url
        :return: The endpoint path
        """
        if action is not None:
            endpoint = f'{self._name}/{action}'
        else:
            endpoint = self._name

        return endpoint

    def _get(self, action: str = None, **kwargs: Any) -> requests.Response:
        """
        Makes an authenticated get request

        :param action: The part the comes after the name in the endpoint url
        :param kwargs: Any additional request kwargs
        :return: A request response object
        """
        return self._client.request('GET', self._build_endpoint(action), **kwargs)

    def _post(self, action: str = None, **kwargs: Any) -> requests.Response:
        """
        Makes an authenticated post request

        :param action: The part the comes after the name in the endpoint url
        :param kwargs: Any additional request kwargs
        :return: A request response object
        """
        return self._client.request('POST', self._build_endpoint(action), **kwargs)

    def _patch(self, action: str = None, **kwargs: Any) -> requests.Response:
        """
        Makes an authenticated patch request

        :param action: The part the comes after the name in the endpoint url
        :param kwargs: Any additional request kwargs
        :return: A request response object
        """
        return self._client.request('PATCH', self._build_endpoint(action), **kwargs)

    def _delete(self, action: str = None, **kwargs: Any) -> requests.Response:
        """
        Makes an authenticated delete request

        :param action: The part the comes after the name in the endpoint url
        :param kwargs: Any additional request kwargs
        :return: A request response object
        """
        return self._client.request('DELETE', self._build_endpoint(action), **kwargs)


class Databases(Endpoint):
    def query(self, database_id: str, **payload: Any):
        """
        Queries a database with filters and sorts

        :param database_id: The database id
        :param payload: json payload
        :return: a generator object with each item being the json output of a single query api request
        """
        r = self._post(f'{database_id}/query', json=payload)

        data = r.json()
        yield from self._client.paginate(self.query, data, database_id, **payload)

    def create(self, **payload: Any):
        """
        Creates a database

        :param payload: json payload
        :return: the json output of the create api request
        """
        r = self._post(json=payload)
        return r.json()

    def update(self, database_id: str, **payload: Any):
        """
        Updates a database with new/existing properties

        :param database_id: The database id
        :param payload: json payload
        :return: the json output of the update api request
        """
        r = self._patch(database_id, json=payload)
        return r.json()

    def retrieve(self, database_id: str, **payload: Any):
        """
        Retrieves a database info

        :param database_id: The database id
        :param payload: json payload
        :return: the json output of the retrieve api request
        """
        r = self._get(database_id, json=payload)
        return r.json()

    def list(self, **payload: Any):
        """
        Lists all the databases shared with the authenticated integration

        :param payload: json payload
        :return: a generator object with each item being the json output of a single list api request
        """
        r = self._get(json=payload)
        data = r.json()
        yield from self._client.paginate(self.list, data, **payload)


class Pages(Endpoint):
    def retrieve(self, page_id: str, **payload: Any):
        """
        Retrieves a page info

        :param page_id: The page id
        :param payload: json payload
        :return: the json output of the retrieve api request
        """
        r = self._get(page_id, json=payload)
        return r.json()

    def create(self, **payload: Any):
        """
        Creates a page

        :param payload: json payload
        :return: the json output of the create api request
        """
        r = self._post(json=payload)
        return r.json()

    def update(self, page_id: str, **payload: Any):
        """
        Updates a page

        :param page_id: The page id
        :param payload: json payload
        :return: the json output of the update api request
        """
        r = self._patch(page_id, json=payload)
        return r.json()


class Blocks(Endpoint):
    def __init__(self, client: Client):
        super().__init__(client)

        self.children = BlocksChildren(client)

    def retrieve(self, block_id: str, **payload: Any):
        """
        Retrieves a block info

        :param block_id: The block id
        :param payload: json payload
        :return: the json output of the retrieve api request
        """
        r = self._get(block_id, json=payload)
        return r.json()

    def update(self, block_id: str, **payload: Any):
        """
        Updates a block

        :param block_id: The block id
        :param payload: json payload
        :return: the json output of the update api request
        """
        r = self._patch(block_id, json=payload)
        return r.json()

    def delete(self, block_id: str, **payload: Any):
        """
        Deletes a block

        :param block_id: The block id
        :param payload: json payload
        :return: the json output of the delete api request
        """
        r = self._delete(block_id, json=payload)
        return r.json()


class BlocksChildren(Endpoint):
    def list(self, block_id: str, **payload: Any):
        """
        Lists a block's children

        :param block_id: The block id
        :param payload: json payload
        :return: a generator object with each item being the json output of a single list api request
        """
        r = self._client.request('GET', f'blocks/{block_id}/children', json=payload)
        data = r.json()
        yield from self._client.paginate(self.list, data, block_id, **payload)

    def append(self, block_id: str, **payload: Any):
        """
        Appends content to a container block

        :param block_id: The block id
        :param payload: json payload
        :return: a generator object with each item being the json output of a single append api request
        """
        r = self._client.request('PATCH', f'blocks/{block_id}/children', json=payload)
        data = r.json()
        yield from self._client.paginate(self.append, data, block_id, **payload)


class Users(Endpoint):
    def retrieve(self, user_id: str, **payload: Any):
        """
        Retrieves a user info

        :param user_id: The user id
        :param payload: json payload
        :return: the json output of the retrieve api request
        """
        r = self._get(user_id, json=payload)
        return r.json()

    def list(self, **payload: Any):
        """
        Lists all users

        :param payload: json payload
        :return: the json output of the list api request
        """
        r = self._get(json=payload)
        data = r.json()
        yield from self._client.paginate(self.list, data, **payload)

    def me(self):
        """
        Retrieves your token's bot user

        :return: the json output of the me api request
        """
        r = self._get('me')
        return r.json()


class Search(Endpoint):
    def __call__(self, **payload: Any):
        """
        Searches all pages and child pages that are shared with the integration. The results may include databases.

        :param payload: json payload
        :return: the json output of the search api request
        """
        r = self._post(json=payload)
        data = r.json()
        yield from self._client.paginate(self.__call__, data, **payload)
