from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tracardi_community',
    version='0.2.0',
    description='Tracardi for Unomi. Tracardi is GUI for Apache Unomi.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    author_email='risto.kowaczewski@gmail.com',
    packages=['app'],
    install_requires=[
        'fastapi',
        'uvicorn',
        'pydantic',
        'python-multipart',
        'httpx',
        'elasticsearch==7.9.1',
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)
