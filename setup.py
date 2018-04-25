from setuptools import setup, find_packages

setup(
    name="dataclasses-json",
    version="0.0.5",
    packages=find_packages(exclude=("tests*",)),
    author="lidatong",
    author_email="charles.dt.li@gmail.com",
    description="Easily serialize dataclasses to and from JSON",
    url="https://github.com/lidatong/dataclasses-json",
    license="Unlicense",
    keywords="dataclasses json",
    install_requires=[
        "dataclasses==0.5"
    ],
    python_requires=">=3.6",
    extras_require={
        "dev": ["pytest", "ipython"]
    },
    include_package_data=True
)
