#!/usr/bin/env bash
apt-get update && apt-get install -y python3 python3-pip python3-venv
# Yolov8 Ultralytics stuff, missing some shared libraries otherwise
DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y libgl1-mesa-dev libglib2.0-0
