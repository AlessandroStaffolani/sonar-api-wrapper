#!/bin/bash

source venv/bin/activate

echo "Tests"
pytest

# Check if pytest command was successful
if [ $? -ne 0 ]; then
  echo "Tests failed"
  exit 1
else
  echo "Tests succeeded"
fi

rm -rf dist/*

echo "Build"
python -m build -w

echo "Publish"
python -m twine upload dist/*

echo "Done"
