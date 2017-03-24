# Manuskript

[Manuskript](http://www.theologeek.ch/manuskript) is an open-source tool for writers.

![Main view](http://www.theologeek.ch/manuskript/wp-content/uploads/2016/03/manuskript-0.3.0.jpg)


## [Download](http://www.theologeek.ch/manuskript/download)

## Running from sources

To run the application without installing just:

* Download [latest code archive](https://github.com/olivierkes/manuskript/archive/master.zip) or clone the repository.
* Run:
  * On Linux/Mac: bin/manuskript

Be sure to have all **dependencies** installed!

## Dependencies
- Python 3
- PyQt5
- Qt SVG (`libqt5svg5` on Ubuntu)
- Qt Webkit (`python3-pyqt5.qtwebkit` on Ubuntu)
- lxml (`python3-lxml` on Ubuntu)

Optional:
- pyenchant
- zlib

### To install dependencies on Linux:
- Arch Linux:
```sudo pacman -S --needed python python-pyqt5 qt5-svg python-lxml python-pyenchant zlib```

- Debian based (Ubuntu, Linux Mint, etc.):
```sudo apt-get install python3-pyqt5 libqt5svg5 python3-lxml python3-enchant zlib1g```  
  An additional package might be needed: ``sudo apt-get install python3-pyqt5.qtwebkit``
