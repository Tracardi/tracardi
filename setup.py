from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()



setup(
    name='tracardi',
    version='0.7.3-dev',
    description='Tracardi Customer Data Platform backend',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    author_email='risto.kowaczewski@gmail.com',
    packages=['tracardi'],
    install_requires=[
        'pip>=21.2.4',
        'pydantic',
        'aiohttp==3.8.3',
        'aiohttp[speedups]',
        'redis',
        'aioredis',
        'elasticsearch[async]==7.10.1',
        'prodict>=0.8.18',
        'tzlocal',
        'python-multipart>=0.0.5',
        'lark==1.1.2',
        'dateparser',
        'dotty-dict @ git+https://github.com/Tracardi/dotty_dict@master#egg=dotty-dict',
        'pytz',
        'device_detector==5.0.1',
        'deepdiff>=5.5.0',
        'pytimeparse',
        'barcodenumber',
        'astral==2.2',
        'jsonschema==4.16.0',
        'python-dateutil==2.8.2',
        'mailchimp-transactional',
        'email-validator',
        'lxml==4.9.1',
        'beautifulsoup4',
        'names==0.3.0',
        'motor~=2.5.0',
        'aiodns',
        'urllib3==1.26.12',
        'geoip2==4.2.0',
        'aiomysql==0.1.1',
        'kombu==5.2.4',
        'asyncpg==0.26.0',
        'aiobotocore~=1.4.2',
        'google-api-python-client == 2.33.0',
        'google_auth_oauthlib == 0.4.6',
        'python_weather==0.4.2',
        'geopy',
        'influxdb-client',
        'grpcio==1.48.2',
        'grpcio-tools==1.48.2',
        'protobuf==3.20.2',
        'certifi==2022.9.24',
        'celery==5.2.6',
        'random-password-generator==2.2.0',
        'asyncio-mqtt==0.12.1',
        'worker @ git+https://github.com/Tracardi/worker.git@master#egg=worker',
        'ElasticEmail @ git+https://github.com/elasticemail/elasticemail-python.git@4.0.20#ElasticEmail',
        'googletrans==3.1.0a0',
        'tweepy==4.10.1',
        'strsimpy==0.2.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['tracardi'],
    include_package_data=True,
    python_requires=">=3.9",
)
