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
import time
from PyQt6 import QtWidgets
from PyQt6 import QtCore


ConfigurationVariables = {'Vstart': -1, 'Vend': 1, 'Vstep': 1, 'ts': 10, 'dt': 25E-6, 'VRest': 0, 'tRest': 1,
                          'Equipment': 'USB0::0x2A8D::0x9201::MY63320391::0::INSTR',
                          'Evaluation': 'Photodiode IV',
                          'Channel': 1, 'Mode': 'VOLT', 'Sense_Mode': 'CURR', 'Compliance': 100E-6, 'Func': 'DC', 'PLC': 0.01, 'FWire': False,
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
        self.PreviewLayout = QtWidgets.QStackedLayout()
        ConfigLayout = QtWidgets.QVBoxLayout()


        self.init_Layout(PageLayout, self.PreviewLayout, ConfigLayout)
        self.setLayout(PageLayout)
        self.EventProcess()

        self.Handler = None

    def init_Layout(self, PageLayout, PreviewLayout, ConfigLayout):
        PageLayout.addLayout(PreviewLayout)
        PageLayout.addLayout(ConfigLayout)

        self.PreviewWidget_PD = UI.PreviewWidget_PD(ConfigurationVariables)
        self.PreviewWidget_MOS = UI.PreviewWidget_MOS(ConfigurationVariables)

        self.PreviewLayout.addWidget(self.PreviewWidget_PD)
        self.PreviewLayout.addWidget(self.PreviewWidget_MOS)

        self.PreviewLayout.setCurrentIndex(0)
        self.PreviewWidget = self.PreviewWidget_PD

        self.init_Tab(ConfigLayout)

    # Define Configuration Tab Define
    def init_Tab(self, ConfigLayout):

        # Make Each Widget
        self.TabHolder = QtWidgets.QTabWidget()
        self.DeviceConfigTab = UI.DeviceConfigWidget(ConfigurationVariables)
        self.EvaluationConfigTab = UI.PhotodiodeIV_EvaluationConfigWidget(ConfigurationVariables)
        self.EvaluationConfigTab2 = UI.MOSFET_IVg_EvaluationConfigWidget(ConfigurationVariables)

        # Make Tabs
        self.TabHolder.addTab(self.DeviceConfigTab, "Connection Settings")
        self.TabHolder.addTab(self.EvaluationConfigTab, "Photodiode")
        self.TabHolder.addTab(self.EvaluationConfigTab2, "MOSFET")
        self.TabHolder.setTabEnabled(2, False)

        # Add Tabs to Main Window
        ConfigLayout.addWidget(self.TabHolder)

        # Define Tab Clicked Event
        self.TabHolder.tabBarClicked.connect(lambda checked=False: UU.WidgetFunction.tabClicked(self.DeviceConfigTab))
        self.TabHolder.tabBarClicked.connect(lambda checked=False: UU.WidgetFunction.tabClicked(self.EvaluationConfigTab))
        self.TabHolder.tabBarClicked.connect(lambda checked=False: UU.WidgetFunction.tabClicked(self.EvaluationConfigTab2))
        self.TabHolder.tabBarClicked.connect(lambda checked=False: self.SMUThreadInit(self.DeviceConfigTab.EvaluationItemList_Combobox.currentText()))

    def EventProcess(self):

        # Connect Pyqtsignal to this class
        self.DeviceConfigTab.VarList.connect(self.UpdateConfigureVariable)
        self.DeviceConfigTab.Handler.connect(self.UpdateHandler)
        self.EvaluationConfigTab.VarList.connect(self.UpdateConfigureVariable)
        self.EvaluationConfigTab2.VarList.connect(self.UpdateConfigureVariable)

        # Device Configuration Tab Event Process
        self.DeviceConfigTab.Connection_Button.clicked.connect(lambda checked=False:
                                                             self.DeviceConfigTab.EquipmentConnect(self.DeviceConfigTab.IDN,
                                                                                                   self.DeviceConfigTab.Status_Label))
        # Evaluation Tab Event Process
        self.EvaluationConfigTab.PauseResume_Button.clicked.connect(lambda checked=False: self.StartButtonEvent(self.EvaluationConfigTab.PauseResume_Button))
        self.EvaluationConfigTab.Stop_Button.clicked.connect(lambda checked=False: self.StopButtonEvent(self.EvaluationConfigTab.PauseResume_Button))
        self.EvaluationConfigTab.Save_Button.clicked.connect(lambda checked=False: self.SaveButtonEvent())

        self.EvaluationConfigTab2.PauseResume_Button.clicked.connect(lambda checked=False: self.StartButtonEvent(self.EvaluationConfigTab2.PauseResume_Button))
        self.EvaluationConfigTab2.Stop_Button.clicked.connect(lambda checked=False: self.StopButtonEvent(self.EvaluationConfigTab2.PauseResume_Button))
        self.EvaluationConfigTab2.Save_Button.clicked.connect(lambda checked=False: self.SaveButtonEvent())

        # Select Evaluation Mode
        self.DeviceConfigTab.EvaluationItemList_Combobox.currentIndexChanged.connect(lambda checked=False: self.UpdateEvaluationTab(self.DeviceConfigTab.EvaluationItemList_Combobox.currentText()))

    def UpdateConfigureVariable(self, VarList):
        for k in VarList:
            ConfigurationVariables[k] = VarList[k]

    def UpdateHandler(self, Handler):
        self.Handler = Handler
        self.EvaluationConfigTab.Handler = self.Handler
        self.EvaluationConfigTab2.Handler = self.Handler

    def SMUThreadInit(self, item):

        if item == 'Photodiode IV':
            QtCore.QCoreApplication.processEvents()
            self.SMUThread = Measurement.PhotodiodeIV(ConfigurationVariables, self.Handler)
            self.EvaluationConfigTab.PauseResume_Button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
            QtCore.QCoreApplication.processEvents()
            self.SMUThread.Data.connect(self.UpdateSensedValue)
            self.SMUThread.Time.connect(self.UpdateSensedValue)
            self.SMUThread.Bias.connect(self.UpdateSensedValue)
            # self.SMUThread.start()

        if item == 'MOSFET I-Vg':
            QtCore.QCoreApplication.processEvents()
            self.SMUThread = Measurement.MOSFET_IVg(ConfigurationVariables, self.Handler)
            self.EvaluationConfigTab2.PauseResume_Button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
            QtCore.QCoreApplication.processEvents()
            self.SMUThread.Data.connect(self.UpdateSensedValue)
            self.SMUThread.Vg.connect(self.UpdateSensedValue)
            self.SMUThread.Vd.connect(self.UpdateSensedValue)
            # self.SMUThread.start()

    def UpdateSensedValue(self, value):
        QtCore.QCoreApplication.processEvents()
        self.PreviewWidget.UpdateValue(value)

    def StartButtonEvent(self, BTN):
        QtCore.QCoreApplication.processEvents()
        if self.SMUThread.running == False:
            BTN.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
            self.SMUThread.start_measurement()
            self.PreviewWidget.pg_settings(self.PreviewWidget.PreviewCanvas)

            if self.SMUThread.isRunning() == False:
                self.SMUThread.start()

        elif self.SMUThread.running == True:
            BTN.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
            self.SMUThread.Pause()

    def StopButtonEvent(self, BTN):
        QtCore.QCoreApplication.processEvents()
        # if self.SMUThread.isFinished():
        self.Handler.clear()
        time.sleep(0.1)
        FU.SMUControl.Stop(self.Handler, ConfigurationVariables['Channel'])
        self.SMUThread.exit()
        self.SMUThreadInit(self.DeviceConfigTab.EvaluationItemList_Combobox.currentText())
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

    def UpdateEvaluationTab(self, item):
        if item == 'Photodiode IV':
            self.TabHolder.setTabEnabled(2, False)
            self.TabHolder.setTabEnabled(1, True)
            self.Updeate_RB_Enable(True)
            self.PreviewLayout.setCurrentIndex(0)
            self.PreviewWidget = self.PreviewWidget_PD
            self.SMUThreadInit(item)

        if item == 'MOSFET I-Vg':
            self.TabHolder.setTabEnabled(1, False)
            self.TabHolder.setTabEnabled(2, True)
            self.Updeate_RB_Enable(False)
            self.PreviewLayout.setCurrentIndex(1)
            self.PreviewWidget = self.PreviewWidget_MOS
            self.SMUThreadInit(item)

    def Updeate_RB_Enable(self, state):
            self.DeviceConfigTab.Channel_RB_1.setEnabled(state)
            self.DeviceConfigTab.Channel_RB_2.setEnabled(state)
            self.DeviceConfigTab.Mode_RB_VOLT.setEnabled(state)
            self.DeviceConfigTab.Mode_RB_CURR.setEnabled(state)
            self.DeviceConfigTab.Sen_Mode_RB_VOLT.setEnabled(state)
            self.DeviceConfigTab.Sen_Mode_RB_CURR.setEnabled(state)
            self.DeviceConfigTab.Func_RB_DC.setEnabled(state)
            self.DeviceConfigTab.Func_RB_PULS.setEnabled(state)
            self.DeviceConfigTab.FWire_RB_OFF.setEnabled(state)
            self.DeviceConfigTab.FWire_RB_ON.setEnabled(state)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = App()
    app.exec()

