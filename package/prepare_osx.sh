#!/bin/bash
set -ev
brew update
brew install python3 enchant
sudo pip3 install --upgrade pip setuptools wheel
pip3 install pyinstaller PyQt5 lxml pyenchant
brew install qt hunspell
# fooling PyEnchant as described in the wiki: https://github.com/olivierkes/manuskript/wiki/Package-manuskript-for-OS-X
sudo touch /usr/local/share/aspell
