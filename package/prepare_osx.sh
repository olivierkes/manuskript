#!/bin/bash
set -ev   # display each line executed along with output

# seriously the CI needs to stop testing 99% of the time if homebrew has updates or not
export HOMEBREW_NO_AUTO_UPDATE=1 # (please let it go, homebrew!)

brew update # (safe the CI some time)

# Upgrade to python 3.x
# brew upgrade python # (should be fine)

brew install enchant
brew postinstall python   # this installs pip
sudo -H pip3 install --upgrade pip setuptools wheel
pip3 install pyinstaller PyQt5 lxml pyenchant pytest pytest-faulthandler
brew install hunspell
# Fooling PyEnchant as described in the wiki.
#   https://github.com/olivierkes/manuskript/wiki/Package-manuskript-for-OS-X
sudo touch /usr/local/share/aspell
#
# Note that if qt install is terminated by Travis CI then it is likely
#   building from source instead of pouring from a homebrew bottle.
#   Fix by choosing lowest osx_image value [1] for xcode that has a
#   homebrew qt bottle [2].
#   [1] https://docs.travis-ci.com/user/reference/osx#os-x-version
#   [2] https://formulae.brew.sh/formula/qt
brew install qt
