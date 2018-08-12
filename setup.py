from setuptools import setup, find_packages

setup(
    name="dataclasses-json",
    version="0.0.8",
    packages=find_packages(exclude=("tests*",)),
    author="lidatong",
    author_email="charles.dt.li@gmail.com",
    description="Easily serialize dataclasses to and from JSON",
    url="https://github.com/lidatong/dataclasses-json",
    license="Unlicense",
    keywords="dataclasses json",
    install_requires=[],
    python_requires=">=3.7",
    extras_require={
        "dev": ["pytest", "ipython", "mypy", "hypothesis"]
    },
    include_package_data=True
)
