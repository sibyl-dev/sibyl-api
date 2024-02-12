#!/bin/bash

echo "Getting started"

# Bundle docs into zero-dependency HTML file
npx @redocly/cli build-docs docs/apispec.json --output index.html

echo -e "\nDone!"
