sudo apt-get -qq update
sudo apt-get -qq install python3-pip python3-dev build-essential qt5-default libxml2-dev libxslt1-dev mesa-utils libgl1-mesa-glx libgl1-mesa-dev

pyenv local 3.6.3
python --version
easy_install pip
pip install pyqt5==5.9 lxml pytest pytest-faulthandler