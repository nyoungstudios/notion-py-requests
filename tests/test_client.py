try:
    # only needs to be run if testing on local environment with environment variables in .env file
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import json
import os
import random
import requests
import string
import unittest

from notion_requests import Client
from types import FunctionType


def pretty_print(data):
    print(json.dumps(data, indent=4))


class MetaClass(type):
    def catch_http_exception(fn):
        def wrapper(*args, **kwargs):
            try:
                fn(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                data = e.response.json()
                # pretty print for better formatted debugging
                pretty_print(data)
                raise Exception(str(data))

        return wrapper

    def __new__(mcs, classname, bases, class_dict):
        new_class_dict = {}
        for attribute_name, attribute in class_dict.items():
            # only wrap the attributes that are functions and start with the word "test"
            if isinstance(attribute, FunctionType) and attribute_name.startswith('test'):
                attribute = mcs.catch_http_exception(attribute)

            # set attributes
            new_class_dict[attribute_name] = attribute

        return type.__new__(mcs, classname, bases, new_class_dict)


class TestBase(unittest.TestCase, metaclass=MetaClass):
    def setUp(self):
        self.notion = Client(os.environ['NOTION_TOKEN'])


class TestDatabases(TestBase):
    def test_query(self):
        database_id = os.environ['NOTION_DATABASE_QUERY_ID']
        query = {
            'database_id': database_id,
            'filter': {
                'and': [
                    {
                        'property': 'Type',
                        'select': {
                            'equals': 'fruit'
                        }
                    },
                    {
                        'property': 'Notes',
                        'text': {
                            'is_not_empty': True
                        }
                    }
                ]
            },
            'sorts': [
                {
                    'property': 'Name',
                    'direction': 'ascending'
                }
            ]
        }

        expected_count = 2
        actual_count = 0
        for response in self.notion.databases.query(**query):
            actual_count += len(response['results'])

        self.assertEqual(expected_count, actual_count)

    def test_query_pagination(self):
        database_id = os.environ['NOTION_DATABASE_QUERY_ID']
        query = {
            'database_id': database_id,
            'filter': {
                'and': [
                    {
                        'property': 'Type',
                        'select': {
                            'equals': 'fruit'
                        }
                    },
                    {
                        'property': 'Notes',
                        'text': {
                            'is_not_empty': True
                        }
                    }
                ]
            },
            'sorts': [
                {
                    'property': 'Name',
                    'direction': 'ascending'
                }
            ],
            'page_size': 1
        }

        expected_count = 2
        actual_count = 0
        for response in self.notion.databases.query(**query):
            actual_count += len(response['results'])

        self.assertEqual(expected_count, actual_count)

    def test_create_and_update_and_delete(self):
        parent_page_id = os.environ['NOTION_PARENT_PAGE_ID']
        database_name = 'Grocery List'
        create_payload = {
            'parent': {
                'type': 'page_id',
                'page_id': parent_page_id
            },
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': database_name
                    }
                }
            ],
            'properties': {
                'Name': {
                    'title': {}
                },
                'Description': {
                    'rich_text': {}
                },
                'In stock': {
                    'checkbox': {}
                }
            }
        }

        response = self.notion.databases.create(**create_payload)
        self.assertEqual('database', response['object'])
        self.assertEqual(database_name, response['title'][0]['plain_text'])
        self.assertIn('Name', response['properties'])
        self.assertIn('Description', response['properties'])
        self.assertIn('In stock', response['properties'])
        self.assertEqual('page_id', response['parent']['type'])
        self.assertEqual(parent_page_id, response['parent']['page_id'].replace('-', ''))

        database_id = response['id']
        new_database_name = "Today's Grocery List"

        update_payload = {
            'database_id': database_id,
            'title': [
                {
                    'text': {
                        'content': new_database_name
                    }
                }
            ],
        }

        response = self.notion.databases.update(**update_payload)
        self.assertEqual(new_database_name, response['title'][0]['plain_text'])

        self.notion.blocks.delete(database_id)

    def test_retrieve(self):
        database_id = os.environ['NOTION_DATABASE_QUERY_ID']
        database_name = os.environ['NOTION_DATABASE_QUERY_NAME']

        response = self.notion.databases.retrieve(database_id)
        self.assertEqual('database', response['object'])
        self.assertEqual(database_id, response['id'].replace('-', ''))
        self.assertEqual(database_name, response['title'][0]['plain_text'])

    def test_list(self):
        expected_count = 1
        actual_count = 0
        for response in self.notion.databases.list():
            actual_count += len(response['results'])

        self.assertEqual(expected_count, actual_count)


class TestPages(TestBase):
    def test_retrieve(self):
        page_id = os.environ['NOTION_PAGE_ID']
        page_name = os.environ['NOTION_PAGE_NAME']
        response = self.notion.pages.retrieve(page_id)
        self.assertEqual('page', response['object'])
        self.assertEqual(page_id, response['id'].replace('-', ''))
        self.assertEqual(page_name, response['properties']['title']['title'][0]['plain_text'])

    def test_create_and_update(self):
        parent_page_id = os.environ['NOTION_PAGE_ID']
        new_page_name = 'Nested Page'
        create_payload = {
            'parent': {
                'page_id': parent_page_id
            },
            'properties': {
                'title': [
                    {
                        'text': {
                            'content': new_page_name,
                        }
                    }
                ]
            }
        }

        response = self.notion.pages.create(**create_payload)
        self.assertEqual('page', response['object'])
        self.assertEqual(parent_page_id, response['parent']['page_id'].replace('-', ''))
        self.assertEqual(new_page_name, response['properties']['title']['title'][0]['text']['content'])

        new_page_id = response['id']
        new_page_name = 'A different title'

        update_payload = {
            'page_id': new_page_id,
            'properties': {
                'title': {
                    'title': [
                        {
                            'type': 'text',
                            'text': {
                                'content': new_page_name
                            }
                        }
                    ]
                }
            }
        }
        response = self.notion.pages.update(**update_payload)
        self.assertEqual(new_page_name, response['properties']['title']['title'][0]['text']['content'])

        self.notion.blocks.delete(new_page_id)


class TestBlocks(TestBase):
    def test_retrieve(self):
        block_id = os.environ['NOTION_TEXT_BLOCK_ID']
        text_block_content = os.environ['NOTION_TEXT_BLOCK_CONTENT']
        response = self.notion.blocks.retrieve(block_id)
        self.assertEqual('block', response['object'])
        self.assertEqual(block_id, response['id'].replace('-', ''))
        self.assertEqual(text_block_content, response['paragraph']['text'][0]['text']['content'])

    def test_update(self):
        letters = string.ascii_letters
        random_text = ''.join(random.choice(letters) for i in range(10))

        block_id = os.environ['NOTION_UPDATE_TEXT_BLOCK_ID']

        update_payload = {
            'block_id': block_id,
            'paragraph': {
                'text': [{
                    'type': 'text',
                    'text': {
                        'content': random_text
                    }
                }]
            }
        }
        response = self.notion.blocks.update(**update_payload)
        self.assertEqual('block', response['object'])
        self.assertEqual(random_text, response['paragraph']['text'][0]['text']['content'])

    def test_children_list(self):
        block_id = os.environ['NOTION_LIST_CHILD_BLOCK_ID']

        expected_count = 3
        actual_count = 0

        for response in self.notion.blocks.children.list(block_id):
            actual_count += len(response['results'])

        self.assertEqual(expected_count, actual_count)

    def test_children_append(self):
        text_content = 'An awesome fruit'
        block_id = os.environ['NOTION_APPEND_CHILD_BLOCK_ID']

        append_payload = {
            'block_id': block_id,
            'children': [
                {
                    'object': 'block',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'text': [{
                            'type': 'text',
                            'text': {
                                'content': text_content
                            }
                        }]
                    }
                }
            ]
        }

        response = next(self.notion.blocks.children.append(**append_payload))

        self.assertEqual('list', response['object'])
        self.assertEqual('block', response['results'][0]['object'])
        self.assertEqual(text_content, response['results'][0]['bulleted_list_item']['text'][0]['text']['content'])

        self.notion.blocks.delete(response['results'][0]['id'])


class TestUsers(TestBase):
    def test_retrieve(self):
        user_name = os.environ['NOTION_USER_NAME']
        user_id = os.environ['NOTION_USER_ID']

        response = self.notion.users.retrieve(user_id)
        self.assertEqual('user', response['object'])
        self.assertEqual(user_name, response['name'])
        self.assertEqual(user_id, response['id'])

    def test_list(self):
        expected_count = 2
        actual_count = 0
        for response in self.notion.users.list():
            actual_count += len(response['results'])

        self.assertEqual(expected_count, actual_count)

    def test_me(self):
        response = self.notion.users.me()
        user_name = os.environ['NOTION_USER_NAME']
        user_id = os.environ['NOTION_USER_ID']

        self.assertEqual('user', response['object'])
        self.assertEqual(user_name, response['name'])
        self.assertEqual(user_id, response['id'])


class TestSearch(TestBase):
    def test_search(self):
        expected_count = 1
        actual_count = 0

        search_query = {
            'query': os.environ['NOTION_DATABASE_QUERY_NAME'],
            'sort': {
                'direction': 'ascending',
                'timestamp': 'last_edited_time'
            }
        }
        for response in self.notion.search(**search_query):
            actual_count += len(response['results'])

        self.assertEqual(expected_count, actual_count)
