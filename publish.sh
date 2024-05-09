#!/bin/bash

source venv/bin/activate

echo "Test"
pytest

rm -rf dist/*

echo "Build"
python -m build -w

echo "Publish"
python -m twine upload dist/*

echo "Done"
