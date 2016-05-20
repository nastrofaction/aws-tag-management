try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'AWS Tag Mangement',
    'author': 'Henry Snow',
    'author_email': 'henry.snow@nielsen.com',
    'version': '0.0.1',
    'install_requires': ['boto3', 'botocore', 'PyYAML'],
    'packages': ['AwsResources'],
    'scripts': [],
    'name': 'AwsTagManagement'
}

setup(**config)
