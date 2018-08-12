from setuptools import setup, find_packages

setup(
    name="dataclasses-json",
    version="0.0.9",
    packages=find_packages(exclude=("tests*",)),
    author="lidatong",
    author_email="charles.dt.li@gmail.com",
    description="Easily serialize dataclasses to and from JSON",
    url="https://github.com/lidatong/dataclasses-json",
    license="Unlicense",
    keywords="dataclasses json",
    install_requires=[
        "dataclasses;python_version=='3.6'"
    ],
    python_requires=">=3.6",
    extras_require={
        "dev": ["pytest", "ipython", "mypy", "hypothesis"]
    },
    include_package_data=True
)
