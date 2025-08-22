#!/bin/bash

# Upgrade pip first
pip install --upgrade pip

# Install wheel (needed for some packages)
pip install wheel

# Install dependencies with constraints
pip install -r requirements.txt -c constraints.txt
