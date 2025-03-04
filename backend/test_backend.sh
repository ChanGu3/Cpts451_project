#!/bin/bash

rm database.db

python3 setup_db.py

pytest