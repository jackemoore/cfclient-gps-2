# Crazyflie PC client

The Crazyflie PC client enables flashing and controlling the Crazyflie.
There's also a Python library that can be integrated into other applications
where you would like to use the Crazyflie.

## Windows

To install the Crazyflie PC client in Windows, download the installation
program from the [binary download
page](http://wiki.bitcraze.se/projects:crazyflie:binaries:index)."Crazyflie
client" will be added to the start menu.

Running from source
-------------------

## Windows

Install dependencies. With Windows installers (tested with 32-Bit versions):
 - Vcredist_86.exe
 - Python 2.7 2.7.9 (https://www.python.org/downloads/windows/)
 - PyQT4 for Python 2.7 4.11.3 (http://www.riverbankcomputing.com/software/pyqt/download)
 - Scipy for Python 2.7 0.15.1 (http://sourceforge.net/projects/scipy/files/scipy/)
 - PyQTGraph 0.9.10 (http://www.pyqtgraph.org/)
 - Numpy  for Python 2.7 0.6.9
 - Py2exe for Python 2.7 1.9.2

Python libs (to be install by running 'setup.py install'):
 - PyUSB 1.0.0 (https://github.com/walac/pyusb/releases)
 - Pysdl2 0.9.3 (https://bitbucket.org/marcusva/py-sdl2/downloads)

Download SDL2 2.0.3 from http://libsdl.org/download-2.0.php and copy SDL2.dll in the
crazyflie-clients-python folder.

Install Git 1.9.5

Install GitHub

Install Folium 0.1.2 with Leaflet 0.7.3 - with Jinja2 dependency

Add pointers to System Variables PATH 

Run with:
```
C:\Python27\python bin\cfclient
```
