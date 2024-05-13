"""
Laser Scanning Graphic User Interface by PyQt
"""
import pandas as pd

try:
    from AddLibraryPath import configure_path
    configure_path()
except ImportError:
    configure_path = None

import UI_Widgets as UI
import UI_Utility as UU
import Function_Utility as FU
import Measurement
import sys
import numpy as np
from PyQt6 import QtGui
from PyQt6 import QtWidgets
from PyQt6 import QtCore
import cv2
from operator import itemgetter

ConfigurationVariables = {'Vstart': -1, 'Vend': 1, 'Vstep': 1, 'ts': 10, 'dt': 25E-6, 'VRest': 0, 'tRest': 1,
                          'Equipment': 'USB0::0x2A8D::0x9201::MY63320391::0::INSTR',
                          'Evaluation': 'Photodiode IV',
                          'Channel': 1, 'Mode': 'VOLT', 'Sense_Mode': 'CURR', 'Compliance': 100E-6, 'Func': 'DC', 'Limit': 100E-6, 'PLC': 0.01, 'FWire': False,
                          'FPS': 5}


class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.window = MainWindow(self)
        self.setCentralWidget(self.window)
        self.setWindowTitle("Device Evaluation")
        self.show()

    def closeEvent(self, event):

        FU.SMUControl.Stop(self.window.Handler, '1')
        FU.SMUControl.close(self.window.Handler)

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MainWindow, self).__init__(parent)

    # Define Layout
        PageLayout = QtWidgets.QHBoxLayout()
        PreviewLayout = QtWidgets.QVBoxLayout()
        ConfigLayout = QtWidgets.QVBoxLayout()

        self.init_Layout(PageLayout, PreviewLayout, ConfigLayout)
        self.setLayout(PageLayout)
        self.EventProcess()

        self.Handler = None

    def init_Layout(self, PageLayout, PreviewLayout, ConfigLayout):
        PageLayout.addLayout(PreviewLayout)
        PageLayout.addLayout(ConfigLayout)

        self.PreviewWidget = UI.PreviewWidget(ConfigurationVariables)

        PreviewLayout.addWidget(self.PreviewWidget)

        self.init_Tab(ConfigLayout)

    # Define Configuration Tab Define
    def init_Tab(self, ConfigLayout):

        # Make Each Widget
        TabHolder = QtWidgets.QTabWidget()
        self.DeviceConfigTab = UI.DeviceConfigWidget(ConfigurationVariables)
        self.EvaluationConfigTab = UI.PhotodiodeIV_EvaluationConfigWidget(ConfigurationVariables)

        # Make Tabs
        TabHolder.addTab(self.DeviceConfigTab, "Connection Settings")
        TabHolder.addTab(self.EvaluationConfigTab, "Evaluation Parameters")

        # Add Tabs to Main Window
        ConfigLayout.addWidget(TabHolder)

        # Define Tab Clicked Event
        TabHolder.tabBarClicked.connect(lambda checked=False: UU.WidgetFunction.tabClicked(self.DeviceConfigTab))
        TabHolder.tabBarClicked.connect(lambda checked=False: UU.WidgetFunction.tabClicked(self.EvaluationConfigTab))
        TabHolder.tabBarClicked.connect(lambda checked=False: self.SMUThreadInit(self.EvaluationConfigTab.PauseResume_Button))


    def EventProcess(self):

        # Connect Pyqtsignal to this class
        self.DeviceConfigTab.VarList.connect(self.UpdateConfigureVariable)
        self.DeviceConfigTab.Handler.connect(self.UpdateHandler)
        self.EvaluationConfigTab.VarList.connect(self.UpdateConfigureVariable)

        # Device Configuration Tab Event Process
        self.DeviceConfigTab.Connection_Button.clicked.connect(lambda checked=False:
                                                             self.DeviceConfigTab.EquipmentConnect(self.DeviceConfigTab.IDN,
                                                                                                   self.DeviceConfigTab.Status_Label))
        # Evaluation Tab Event Process
        self.EvaluationConfigTab.PauseResume_Button.clicked.connect(lambda checked=False: self.StartButtonEvent(self.EvaluationConfigTab.PauseResume_Button))
        self.EvaluationConfigTab.Stop_Button.clicked.connect(lambda checked=False: self.StopButtonEvent(self.EvaluationConfigTab.PauseResume_Button))
        self.EvaluationConfigTab.Save_Button.clicked.connect(lambda checked=False: self.SaveButtonEvent())

    def UpdateConfigureVariable(self, VarList):
        for k in VarList:
            ConfigurationVariables[k] = VarList[k]

    def UpdateHandler(self, Handler):
        self.Handler = Handler
        self.EvaluationConfigTab.Handler = self.Handler

    def SMUThreadInit(self, BTN):

        QtCore.QCoreApplication.processEvents()
        self.SMUThread = Measurement.PhotodiodeIV(ConfigurationVariables, self.Handler)
        BTN.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        QtCore.QCoreApplication.processEvents()
        self.SMUThread.Data.connect(self.UpdateSensedValue)
        self.SMUThread.Bias.connect(self.UpdateSensedValue)
        # self.SMUThread.start()

    def UpdateSensedValue(self, value):
        QtCore.QCoreApplication.processEvents()
        self.PreviewWidget.UpdateValue(value)

                # self.plotinfo, = self.PreviewWidget.PreviewCanvas.axes.plot(self.tempX, self.tempY)
                # if self.tempX.__len__() == self.tempY.__len__():
                #     if self.tempX.__len__() % int(1/ConfigurationVariables['FPS']/ConfigurationVariables['dt']) == 1:
                        # self.plotinfo.set_xdata(self.tempX[::5])
                        # self.plotinfo.set_ydata(self.tempY[::5])
                        # self.PreviewWidget.PreviewCanvas.axes.relim()
                        # plt.pause(ConfigurationVariables['dt'] / 10)
                        # self.PreviewWidget.PreviewCanvas.draw()

    def StartButtonEvent(self, BTN):
        QtCore.QCoreApplication.processEvents()
        if self.SMUThread.running == False:
            BTN.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
            self.SMUThread.start_measurement()

            if self.SMUThread.isRunning() == False:
                self.SMUThread.start()

        elif self.SMUThread.running == True:
            BTN.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
            self.SMUThread.Pause()

    def StopButtonEvent(self, BTN):
        QtCore.QCoreApplication.processEvents()
        self.SMUThread.exit()
        # if self.SMUThread.isFinished():
        FU.SMUControl.Stop(self.Handler, ConfigurationVariables['Channel'])
        self.SMUThreadInit(self.EvaluationConfigTab.PauseResume_Button)
        # self.PreviewWidget.PreviewCanvas.scene().removeItem(self.PreviewWidget.legend)
        self.PreviewWidget.pg_settings(self.PreviewWidget.PreviewCanvas)

    def SaveButtonEvent(self):
        filepath = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "", "csv Files(*.csv);;text Files(*.txt);;All Files(*)")
        data = list(map(list, zip(*self.PreviewWidget.y)))
        df = pd.DataFrame(index = self.PreviewWidget.x[0], columns = self.PreviewWidget.V, data = data)

        if filepath[1][-4:-1] == 'csv':
            df.to_csv(f"{filepath[0]}", index = True)
        elif filepath[1][-4:-1] == 'txt':
            df.to_csv(f"{filepath[0]}", sep= '\t', index =True)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = App()
    app.exec()
