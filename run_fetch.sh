#!/bin/bash
# Script to run fetch_scholar.py with the virtual environment

cd "$(dirname "$0")"
source venv/bin/activate
python fetch_scholar.py
