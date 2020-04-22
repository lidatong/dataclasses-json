import os
from setuptools import setup, find_packages
from distutils.command.register import register as register_orig
from distutils.command.upload import upload as upload_orig


with open('README.md', 'r', encoding='utf8') as f:
    readme = f.read()


class register(register_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')


class upload(upload_orig):
    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')


setup(
    name='dataclasses-json',
    version='0.4.2-twk',
    packages=find_packages(exclude=('tests*',)),
    package_data={"dataclasses_json": ["py.typed"]},
    author='lidatong',
    author_email='charles.dt.li@gmail.com',
    description='Easily serialize dataclasses to and from JSON',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/lidatong/dataclasses-json',
    license='MIT',
    keywords='dataclasses json',
    cmdclass={
        'register': register,
        'upload': upload,
    },

    install_requires=[
        'dataclasses;python_version=="3.6"',
        'marshmallow>=3.3.0,<4.0.0',
        'marshmallow-enum>=1.5.1,<2.0.0',
        'typing-inspect>=0.4.0',
        'stringcase==1.2.0,<2.0.0'
    ],
    python_requires='>=3.6',
    extras_require={
        'dev': [
            'pytest',
            'ipython',
            'mypy>=0.710',
            'hypothesis',
            'portray',
            'flake8',
            'simplejson'
        ]
    },
    include_package_data=True
)






