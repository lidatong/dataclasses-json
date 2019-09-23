#!/bin/bash

if [ -z $1 ]
then
  echo 'must supply tag'
  exit 1
else
  . venv/bin/activate
  git tag $1
  portray on_github_pages
  python setup.py sdist bdist_wheel
  twine upload dist/*
fi
