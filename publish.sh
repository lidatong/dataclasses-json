#!/bin/bash

if [ -z $1 ]
then
  echo 'must supply tag'
  exit 1
else
  # git tag $1
  # python setup.py sdist bdist_wheel
  # twine upload dist/*
  portray on_github_pages
fi
