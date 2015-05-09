#!/usr/bin/env python

from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork

import functools, time

class MapviewWidget(QtGui.QWidget):

    def __init__(self):
        super(MapviewWidget, self).__init__()
        self.setupUi()
        self.show()
        self.raise_()
#        self.lat = 51.504
#        self.lng = -0.09
#        self.goOut(self.lat, self.lng)
        self.lath = 33.7674
        self.lngh = -117.5008
        self.lockedh = 1.0
        self.goOut(self.lath, self.lngh, self.lockedh)
        time.sleep(1)
        self.latq = 33.7660
        self.lngq = -117.5008
        self.lockedq = 2.0
        self.goOut(self.latq, self.lngq, self.lockedq)  
        
    def setupUi(self):
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

#        self.lat = 51.505
#        self.lng = -0.09
        self.lat = 33.7674
        self.lng = -117.5008
        self.locked = 1.0

 
        button = QtGui.QPushButton('Go to Home')
        panToParis = functools.partial(self.panMap, self.lng, self.lat)
        button.clicked.connect(panToParis)
        vbox.addWidget(button)

    def onLoadFinished(self):
        with open('gpstab_map.js', 'r') as f:
            frame = self.view.page().mainFrame()
            frame.evaluateJavaScript(f.read())

    def addPoints(self):
        self.onGpsUpdate(self.lat,self.lng, self.locked)

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
        

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = MapviewWidget()
    app.exec_()
    
