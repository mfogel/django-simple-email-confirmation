import re
from os import path
from setuptools import setup


# read() and find_version() taken from jezdez's python apps, ex:
# https://github.com/jezdez/django_compressor/blob/develop/setup.py

def read(*parts):
    return open(path.join(path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M,
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-simple-email-confirmation',
    version=find_version('simple_email_confirmation', '__init__.py'),
    author='Mike Fogel',
    author_email='mike@fogel.ca',
    description="Simple email confirmation for django.",
    long_description=read('README.rst'),
    url='https://github.com/mfogel/django-simple-email-confirmation',
    license='BSD',
    packages=[
        'simple_email_confirmation',
        'simple_email_confirmation.migrations',
        'simple_email_confirmation.south_migrations',
        'simple_email_confirmation.tests',
        'simple_email_confirmation.tests.myproject',
        'simple_email_confirmation.tests.myproject.myapp',
    ],
    install_requires=['django>=1.5.0'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: BSD License',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        'Topic :: Utilities',
        "Framework :: Django",
    ]
)
