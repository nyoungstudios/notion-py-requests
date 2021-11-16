import os
from setuptools import setup, find_packages


def read_content(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        content = f.read()

    return content


def get_version():
    """
    Gets the version since it is likely the dependencies are not installed on the system when running this setup
    :return: a string of the package's version
    """
    content = read_content('notion_requests/version.py')
    parts = content.rstrip().split(' ')
    return parts[-1]


setup(
    name='notion-requests',
    version=get_version(),
    description='Notion Python SDK Client using Requests.',
    long_description=read_content('README.md'),
    long_description_content_type='text/markdown',
    author='Nathaniel Young',
    author_email='',
    maintainer='Nathaniel Young',
    maintainer_email='',
    url='https://github.com/nyoungstudios/notion-py-requests',
    license='MIT',
    packages=find_packages(exclude=('tests',)),
    python_requires='>=3.6,<4.0',
    install_requires=[
        'requests',
    ],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities'
    ),
    keywords='notion api client sdk python'
)
