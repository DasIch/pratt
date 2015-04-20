# encoding: utf-8
"""
    setup
    ~~~~~

    :copyright: 2014 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import os
import re
from io import open # PY2

from setuptools import setup


def get_version():
    pratt_py_path = os.path.join(
        os.path.dirname(__file__),
        'pratt.py',
    )
    with open(pratt_py_path, encoding='utf-8') as f:
        pratt_py_content = f.read()
    match = re.search(r'__version__\s*=\s*\'(\d+\.\d+.\d+)\'', pratt_py_content)
    version = match.group(1)
    return version


def get_long_description():
    readme_path = os.path.join(
        os.path.dirname(__file__),
        'README.rst'
    )
    with open(readme_path, encoding='utf-8') as f:
        return f.read()


setup(
    name='pratt',
    version=get_version(),
    description='A library for creating pratt parsers',
    long_description=get_long_description(),
    url='https://github.com/DasIch/pratt',
    author='Daniel Neuhäuser',
    author_email='ich@danielneuhaeuser.de',
    py_modules=['pratt']
)
