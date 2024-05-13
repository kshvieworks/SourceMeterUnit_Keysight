import numpy as np
from PyQt6 import QtGui
from PyQt6 import QtWidgets
from PyQt6 import QtCore
import cv2
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pyqtgraph as pg


class WidgetDesign:

    @staticmethod
    def Layout_Widget(Widgets, Orientation='Vertical'):
        Layout = QtWidgets.QVBoxLayout()
        if Orientation == 'Horizontal':
            Layout = QtWidgets.QHBoxLayout()
        elif Orientation == 'Stacked':
            Layout = QtWidgets.QStackedLayout()

        try:
            for Widget_k in Widgets:
                Layout.addWidget(Widget_k)
        except TypeError:
            Layout.addWidget(Widgets)

        return Layout

    @staticmethod
    def Layout_Frame_Layout(UpperLayout, LowerLayout, Title=''):
        GroupBox = QtWidgets.QGroupBox(Title)
        GroupBox.setLayout(LowerLayout)
        UpperLayout.addWidget(GroupBox)
        del LowerLayout

    @staticmethod
    def Init_Entry(Entry, DefaultVal, Size=(200, 30), AlignPos=QtCore.Qt.AlignmentFlag.AlignCenter):
        Entry.setAlignment(AlignPos)
        Entry.setText(str(DefaultVal))
        Entry.setFixedSize(Size[0], Size[1])


class WidgetFunction:
    @staticmethod
    def tabClicked(Tab):
        Tab.BindConfigurationVariables()

    @staticmethod
    def UpdateConfigureVariable(ConfigVar, VarList):
        for k in VarList:
            ConfigVar[k] = VarList[k]


class CustomFunction:

    @staticmethod
    def cv2qt(cvimage):
        """Convert from an opencv image to QPixmap"""
        cvimage = cv2.resize(cvimage, dsize=(0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        rgb_image = cv2.cvtColor(cvimage, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        p = convert_to_Qt_format
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

