#!/bin/bash

set -e

. venv/bin/activate
git add .
git commit -m "chore: release $1"
git tag -a "$1"
git push --follow-tags
gh release create "$1" --latest --generate-notes --verify-tag
portray on_github_pages
# python setup.py sdist bdist_wheel
# twine upload dist/*
