from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='tracardi',
    version='0.6.9',
    description='Tracardi Customer Data Platform backend',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    author_email='risto.kowaczewski@gmail.com',
    packages=['tracardi'],
    install_requires=[
        'pydantic==1.8.2',
        'aiohttp==3.7.4.post0',
        'aiohttp[speedups]',
        'elasticsearch==7.13.4',
        'prodict==0.8.18',
        'tzlocal==2.1',
        'python-multipart==0.0.5',
        'lark==0.11.3',
        'dateparser==1.0.0',
        'dotty-dict==1.3.0',
        'pytz==2021.1',
        'tracardi-plugin-sdk>=0.6.4',
        'tracardi_graph_runner>=0.6.4',
        'tracardi-dot-notation>=0.6.2',
        'device_detector==0.10',
        'pip>=21.2.4',
        'deepdiff>=5.5.0',

        'tracardi-key-counter',

        'tracardi-rabbitmq-publisher',

        'tracardi-weather',
        'tracardi-maxmind-geolite2',
        'tracardi-day-night-split',
        'tracardi-discord-webhook',
        'tracardi-remote-call',
        'tracardi-zapier-webhook',

        'tracardi-mongodb-connector',
        'tracardi-postgresql-connector',
        'tracardi-mysql-connector',
        'tracardi-redshift-connector',
        'tracardi-url-parser',
        'tracardi-local-timespan'
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
