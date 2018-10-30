#!/bin/bash
set -ev
brew update
# upgrade to python 3.x
brew upgrade python
brew install enchant
brew postinstall python # this installs pip
sudo -H pip3 install --upgrade pip setuptools wheel
pip3 install pyinstaller PyQt5 lxml pyenchant pytest pytest-faulthandler
brew install qt hunspell
# fooling PyEnchant as described in the wiki: https://github.com/olivierkes/manuskript/wiki/Package-manuskript-for-OS-X
sudo touch /usr/local/share/aspell
