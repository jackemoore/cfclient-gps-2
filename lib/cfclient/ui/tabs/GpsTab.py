#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2011-2013 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
This tab plots different logging data defined by configurations that has been
pre-configured.
"""
import math

__author__ = 'Bitcraze AB'
__all__ = ['GpsTab']

import glob
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui, uic, QtWebKit, QtNetwork 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from pprint import pprint
import datetime
import functools

#from cfclient.ui.widgets.plotwidget import PlotWidget

from cflib.crazyflie.log import Log, LogVariable, LogConfig

from cfclient.ui.tab import Tab

from PyQt4.QtCore import *
from PyQt4.QtGui import *


should_enable_tab = True
gps_connected = False

import sys

gps_tab_class = uic.loadUiType(sys.path[0] +
                                "/cfclient/ui/tabs/gpsTab.ui")[0]

class GpsTab(Tab, gps_tab_class):
    """Tab for plotting logging data"""

    _log_data_signal = pyqtSignal(int, object, object)
    _log_error_signal = pyqtSignal(object, str)

    _disconnected_signal = pyqtSignal(str)
    _connected_signal = pyqtSignal(str)
    _console_signal = pyqtSignal(str)


    def __init__(self, tabWidget, helper, *args):
        super(GpsTab, self).__init__(*args)
        self.setupUi(self)

        self.tabName = "GPS"
        self.menuName = "GPS"

        self.tabWidget = tabWidget
        self.helper = helper
        self._cf = helper.cf
        self._got_home_point = False
#        self._line = ""

        if not should_enable_tab:
            self.enabled = False

        if self.enabled:

            self._mapview = MapviewWidget()
            
            # create the slider
#            self.zoomSlider = QSlider(Qt.Horizontal)

            self._reset_max_btn.clicked.connect(self._reset_max)

            # add all the components
            self.map_layout.addWidget(self._mapview)
            
            # Connect the signals
            self._log_data_signal.connect(self._log_data_received)
            self._log_error_signal.connect(self._logging_error)
            self._connected_signal.connect(self._connected)
            self._disconnected_signal.connect(self._disconnected)

            # Connect the callbacks from the Crazyflie API
            self.helper.cf.disconnected.add_callback(
                self._disconnected_signal.emit)
            self.helper.cf.connected.add_callback(
                self._connected_signal.emit)

        else:
            logger.warning("GPS tab not enabled")

        self._max_speed = 0.0

        self._fix_types = {
            0: "No fix",
            1: "Dead reckoning only",
            2: "2D-fix",
            3: "3D-fix",
            4: "GNSS+dead",
            5: "Time only fix"
        }

    def _connected(self, link_uri):
        lg = LogConfig("GPS", 100)
        lg.add_variable("gps.lat")
        lg.add_variable("gps.lon")
        lg.add_variable("gps.hMSL")
        lg.add_variable("gps.heading")
        lg.add_variable("gps.gSpeed")
        lg.add_variable("gps.hAcc")
        lg.add_variable("gps.fixType")
        self._cf.log.add_config(lg)
        if lg.valid:
            lg.data_received_cb.add_callback(self._log_data_signal.emit)
            lg.error_cb.add_callback(self._log_error_signal.emit)
            lg.start()
        else:
            logger.warning("Could not setup logging block for GPS!")
        self._max_speed = 0.0

    def _disconnected(self, link_uri):
        """Callback for when the Crazyflie has been disconnected"""
        self._got_home_point = False
        return

    def _logging_error(self, log_conf, msg):
        """Callback from the log layer when an error occurs"""
        QMessageBox.about(self, "Plot error", "Error when starting log config"
                " [%s]: %s" % (log_conf.name, msg))

    def _reset_max(self):
        """Callback from reset button"""
        self._max_speed = 0.0
        self._speed_max.setText(str(self._max_speed))

        self._mapview.clear_data() 

        self._long.setText("")
        self._lat.setText("")
        self._height.setText("")

        self._speed.setText("")
        self._heading.setText("")
        self._accuracy.setText("")

        self._fix_type.setText("")


    def _log_data_received(self, timestamp, data, logconf):
        """Callback when the log layer receives new data"""

        long = float(data["gps.lon"])/10000000.0
        lati = float(data["gps.lat"])/10000000.0
        alt = float(data["gps.hMSL"])/1000.0
        speed = float(data["gps.gSpeed"])/1000.0
        accuracy = float(data["gps.hAcc"])/1000.0
        fix_type = float(data["gps.fixType"])
        heading = float(data["gps.heading"])/100000.0

        self._long.setText(str(long))
        self._lat.setText(str(lati))
        self._height.setText(str(alt))

        self._speed.setText(str(speed))
        self._heading.setText(str(heading))
        self._accuracy.setText(str(accuracy))
        if speed > self._max_speed:
            self._max_speed = speed
        self._speed_max.setText(str(self._max_speed))

        self._fix_type.setText(self._fix_types[fix_type])
        
        if self._got_home_point:
            if fix_type >=2:
                locked = 2.0
            else:
                locked = 0.0
        else:
            if fix_type >=3:
                self._got_home_point = True
                locked = 1.0
            else:
                locked = 0.0
                
        if locked > 0.0:  
            self._mapview.add_data(long, lati, alt, accuracy, locked)

if should_enable_tab:
    class MapviewWidget(QtGui.QWidget):

        def __init__(self):
            super(MapviewWidget, self).__init__()
            self.setupUi()  
            self.show()
            self.raise_()

        def setupUi(self):
#            self._points = []
            self._lat = None
            self._lng = None
            self._height = None
            self._accu =  None
            self._locked =  0.0

            vbox = QtGui.QVBoxLayout()
            self.setLayout(vbox)

            label = self.label = QtGui.QLabel()
            sp = QtGui.QSizePolicy()
            sp.setVerticalStretch(0)
            label.setSizePolicy(sp)
            vbox.addWidget(label)

            view = self.view = QtWebKit.QWebView()

            cache = QtNetwork.QNetworkDiskCache()
            cache.setCacheDirectory("cache")
            view.page().networkAccessManager().setCache(cache)
            view.page().networkAccessManager()

            view.page().mainFrame().addToJavaScriptWindowObject("MapviewWidget", self) 
            view.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
            view.load(QtCore.QUrl('gpstab_map.html'))
            view.loadFinished.connect(self.onLoadFinished)
            view.loadFinished.connect(self.addPoints) 
            view.linkClicked.connect(QtGui.QDesktopServices.openUrl)
            vbox.addWidget(view)

            self.lat = 33.7650
            self.lng = -117.5008
            self.locked = 0.0

            button = QtGui.QPushButton('Go to Home')
            panToHome = functools.partial(self.panMap, self.lng, self.lat)
            button.clicked.connect(panToHome)
            vbox.addWidget(button)
 
        def onLoadFinished(self):
            with open('gpstab_map.js', 'r') as f:
                frame = self.view.page().mainFrame()
                frame.evaluateJavaScript(f.read())

        def addPoints(self):
            self.onGpsUpdate(self.lat,self.lng,self.locked)

        @QtCore.pyqtSlot(float, float)

        def onMapMove(self, lat, lng):
            self.label.setText('MapLat: {:.5f}, MapLon: {:.5f}'.format(lat, lng))

        def panMap(self, lng, lat):
            frame = self.view.page().mainFrame()
            frame.evaluateJavaScript('map.panTo(L.latLng({}, {}));'.format(lat, lng))
 
        def onGpsUpdate(self, lat, lng, locked):
            frame = self.view.page().mainFrame()
            frame.evaluateJavaScript('gpsPoint({}, {}, {});'.format(lat, lng, locked))

        def goOut(self,lat,lng,locked):
            self.onGpsUpdate(lat, lng, locked) 

        def clear_data(self):
#            self._points = []
            self._lat = None
            self._lng = None
            self._height = None
            self._accu =  None
            self._locked =  0.0

        def add_data(self, lng, lat, height, accu, locked):
#            self._points.append([lng, lat, height, accu, locked])
            self._lat = lat
            self._lng = lng
            self._height = height
            self._accu =  accu
            self._locked =  locked
#            self.update()
            self.goOut(self._lat, self._lng, self._locked)            
            
                 
