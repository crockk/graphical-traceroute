#!/usr/bin/env bash


service nginx start &
service nginx restart &

wait -n

python3 /backend/app.py
