from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='tracardi',
    version='0.6.26',
    description='Tracardi Customer Data Platform backend',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    author_email='risto.kowaczewski@gmail.com',
    packages=['tracardi'],
    install_requires=[
        'pip>=21.2.4',
        'pydantic',
        'aiohttp',
        'aiohttp[speedups]',
        'redis',
        'aioredis',
        'elasticsearch[async]==7.10.1',
        'prodict>=0.8.18',
        'tzlocal',
        'python-multipart>=0.0.5',
        'lark>=0.11.3',
        'dateparser',
        'dotty-dict==1.3.0',
        'pytz',
        'device_detector==5.0.1',
        'deepdiff>=5.5.0',
        'tracardi-plugin-sdk>=0.6.30',
        'tracardi_graph_runner>=0.6.9',
        'tracardi-dot-notation>=0.6.6',
        'pytimeparse',
        'barcodenumber',
        'astral',
        'jsonschema',
        'python-dateutil',
        'mailchimp-transactional',
        'email-validator',
        'lxml',
        'beautifulsoup4',
        'names==0.3.0',
        'motor~=2.5.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['tracardi'],
    include_package_data=True,
    python_requires=">=3.8",
)
