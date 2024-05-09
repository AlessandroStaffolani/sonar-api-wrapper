#!/bin/bash

source venv/bin/activate

echo "Test"
pytest

echo "Build"
python -m build -w

echo "Publish"
python -m twine upload dist/*

echo "Done"
