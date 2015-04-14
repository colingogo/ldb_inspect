#!/usr/bin/python

'''
    Use this tool to inspect the images+labels saved in a levelDB for Caffe
    Ver 1.0 assumes float[0.0-1.0] grayscale images are stored in levelDB
    Author: Mosalam Ebrahimi <m.ebrahimi@ieee.org> 2015
'''

import sys, getopt, copy
import plyvel # levelDB library
import ConfigParser # used to read the caffe location from a config file
from PySide import QtCore, QtGui, QtUiTools # pyside+qt for gui
import numpy as np
import cv2

class Inspector:
    def __init__(self):
        self.dbIT = None # leveldb iterator
        self.inputDB = None
        self.magnify = 3 # enlarge images
        self.MainWindow = None
        self.app = None # qt app

    # import caffe
    def importCaffe(self):
        configGeneral = ConfigParser.ConfigParser()
        configGeneral.readfp(open('./resources/general.ini'))
        caffe_root = configGeneral.get('caffe', 'caffe_root')
        sys.path.insert(0, caffe_root + 'python/caffe/proto')
        sys.path.insert(0, caffe_root + 'python')
        global caffe_pb2, caffe
        import caffe_pb2
        import caffe

    # pass the leveldb name as an argument to this script,
    # with i <db> or input=<db>
    def parseArgs(self, argv):
        self.inputDB = False
        try:
            opts, args = getopt.getopt(argv,"i:",["input="])
        except getopt.GetoptError:
            print 'inspector.py -i <inputDB>'
            return False

        for opt, arg in opts:
            if opt in ("-i", "--input"):
                self.inputDB = arg
        if self.inputDB == False:
            print 'inspector.py -i <inputDB>'
            return False
        return True

    # load the levelDB
    def loadDB(self):
        db = plyvel.DB(self.inputDB, create_if_missing=False,
                       error_if_exists=False)
        self.dbIT = db.raw_iterator()
        self.dbIT.seek_to_first()

    # load the qt widget from the given .ui file
    def loadUiWidget(self, uifilename, parent=None):
        loader = QtUiTools.QUiLoader()
        uifile = QtCore.QFile(uifilename)
        uifile.open(QtCore.QFile.ReadOnly)
        ui = loader.load(uifile, parent)
        uifile.close()
        return ui

    # the callback of the 'Next' button
    def on_nextButton_clicked(self):
        try:
            self.dbIT.next()
            self.showImg()
        except:
            self.dbIT.seek_to_last()
            return

    # the callback of the 'Previous' button
    def on_prevButton_clicked(self):
        try:
            self.dbIT.prev()
            self.showImg()
        except:
            self.dbIT.seek_to_first()
            return

    # show the currently selected image
    def showImg(self):
        value = self.dbIT.value()
        key = self.dbIT.key()

        datum = caffe_pb2.Datum.FromString(value)
        arr = caffe.io.datum_to_array(datum)
        arr = np.array(arr) * 255.0
        arr = arr.astype(np.uint8)
        colorImg = cv2.cvtColor(arr[0], cv2.COLOR_GRAY2RGB)
        colorImg = cv2.resize(colorImg, None, fx=self.magnify, fy=self.magnify,
                              interpolation = cv2.INTER_NEAREST)

        height, width, bytesPerComponent = colorImg.shape
        bytesPerLine = bytesPerComponent * width
        qImg = QtGui.QImage(colorImg.data, width, height, bytesPerLine,
                            QtGui.QImage.Format_RGB888)
        self.MainWindow.label.setPixmap(QtGui.QPixmap.fromImage(qImg))
        self.MainWindow.lineEdit.setText(str(datum.label))
        self.MainWindow.label.show()
        self.MainWindow.setWindowTitle(key)

    # create the gui from the .ui file
    def createGUI(self):
        self.app = QtGui.QApplication('')
        self.MainWindow = self.loadUiWidget("./resources/inspector.ui")
        self.MainWindow.nextButton.clicked.connect(self.on_nextButton_clicked)
        self.MainWindow.prevButton.clicked.connect(self.on_prevButton_clicked)
        self.MainWindow.show()

    # run the main qt loop
    def main(self):
        sys.exit(self.app.exec_())

def main(argv):
    app = Inspector()
    if not app.parseArgs(argv):
        sys.exit(2)
    app.importCaffe()
    app.loadDB()
    app.createGUI()
    app.showImg()
    app.main()

if __name__ == "__main__":
    main(sys.argv[1:])