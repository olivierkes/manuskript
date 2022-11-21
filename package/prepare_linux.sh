#!/bin/bash
set -ev   # display each line executed along with output
sudo apt-get -qq update
sudo apt-get -qq install python3-pip python3-dev \
     build-essential qt5-default libxml2-dev libxslt1-dev \
     mesa-utils libgl1-mesa-glx libgl1-mesa-dev

pyenv local 3.6.7
python3 --version
sudo pip3 install --upgrade pip setuptools wheel
pip3 install pyqt5==5.9 lxml pytest pytest-faulthandler
