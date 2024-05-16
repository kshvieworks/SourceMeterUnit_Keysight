from PyQt6 import QtWidgets
from PyQt6 import QtCore
import numpy as np
import pyqtgraph as pg
from pyvisa import *
import UI_Utility as UU


class PreviewWidget(QtWidgets.QWidget):
    def __init__(self, ConfigVar, parent=None):
        super(PreviewWidget, self).__init__(parent)

        self.ConfigVar = ConfigVar
        self.axinfo = []

        PreviewLayout = QtWidgets.QVBoxLayout()

        self.initUI(PreviewLayout)
        self.setLayout(PreviewLayout)

    def initUI(self, Layout):

        self.UI_Component()
        self.UI_Layout(Layout)

    def UI_Layout(self, Layout):
        PreviewStackLayout = QtWidgets.QVBoxLayout()
        PreviewStackLayout.addWidget(self.PreviewCanvas)
        Layout.addLayout(PreviewStackLayout)

    def UI_Component(self):

        self.PreviewCanvas = pg.PlotWidget()
        self.legend = self.PreviewCanvas.addLegend()

        self.pg_settings(self.PreviewCanvas)

    def pg_settings(self, plotinfo) -> None:

        plotinfo.clear()
        n = 1+int((np.abs(self.ConfigVar['Vend']-self.ConfigVar['Vstart'])/self.ConfigVar['Vstep']))
        self.color = iter([(255*(1-k/n), k*255/n, k*255/n) for k in range(n)])
        plotinfo.plotItem.setLabels(bottom='Time [s]', left='Current [A]')
        plotinfo.setBackground('w')
        plotinfo.showGrid(x = True, y = True, alpha = 0.3)
        for k in list(self.axinfo):
            k.clear()
        self.axinfo = []
        try:
            del self.tempX, self.tempY
        except AttributeError:
            pass

    def newplot(self, plotinfo, legend, color) -> object:
        return plotinfo.plot(name=f'{legend} V', pen=pg.mkPen(color=color))

    def UpdateValue(self, value, intervals=2) -> None:

        if value[:2] == 'V=':
            if not hasattr(self, 'tempX'):
                self.tempX = np.empty(0, dtype=np.float64)
                self.tempY = np.empty(0, dtype=np.float64)
                self.x = []
                self.y = []
                self.V = []

            else:
                self.x.append(self.tempX)
                self.y.append(self.tempY)
                self.tempX = np.empty(0, dtype=np.float64)
                self.tempY = np.empty(0, dtype=np.float64)

            self.V.append(value)
            self.c = next(self.color)
            self.axinfo.append(self.newplot(self.PreviewCanvas, value, self.c))
            self.t = 0
            print(value)
        elif value == 'Bias':
            self.t = self.tempX[-1] + self.tempX[1]
            print(self.t)
        elif value == 'Finished':
            self.x.append(self.tempX)
            self.y.append(self.tempY)

        # elif value[-1] == '\n':
        #     data = float(value.strip("\n"))
        #     self.tempY = np.append(self.tempY, data)
        #
        #     if self.tempX.__len__() == self.tempY.__len__():
        #         self.UpdatePlot(self.PreviewCanvas, self.axinfo[-1], self.tempX, self.tempY)
        #
        # else:
        #     time = float(value)
        #     self.tempX = np.append(self.tempX, self.t + time)

        else:
            data = np.array(value.strip("\n").split(','), dtype=np.float64)
            self.tempX = np.append(self.tempX, self.t + data[1::2])
            self.tempY = np.append(self.tempY, data[::2])
            # if self.tempX.__len__() == self.tempY.__len__():
            self.UpdatePlot(self.PreviewCanvas, self.axinfo[-1], self.tempX, self.tempY)

    def UpdatePlot(self, plotinfo, axinfo, x, y) -> None:
        axinfo.setData(x[::2], y[::2])


class DeviceConfigWidget(QtWidgets.QWidget):
    VarList = QtCore.pyqtSignal(dict)
    Handler = QtCore.pyqtSignal(object)

    def __init__(self, ConfigVar, parent=None):
        super(DeviceConfigWidget, self).__init__(parent)

        Layout = QtWidgets.QVBoxLayout()

        self.IDN = ResourceManager().list_resources()[0]
        # self.Handler
        self.initUI(Layout)
        self.setLayout(Layout)

    def initUI(self, Layout):

        self.UI_Component()
        self.UI_Layout(Layout)

    def UI_Layout(self, Layout):

        Mid_Layout = QtWidgets.QVBoxLayout()
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.EquipmentName_Label, self.EquipmentName_Entry), 'Horizontal'))
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Connection_Button, self.Status_Label), 'Horizontal'))
        # Mid_Layout.addWidget(self.ConnectedEquipment_Label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        UU.WidgetDesign.Layout_Frame_Layout(Layout, Mid_Layout, 'Equipment Connection')

        Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.EvaluationItemList_Label, self.EvaluationItemList_Combobox), 'Horizontal'))

        Mid_Layout = QtWidgets.QVBoxLayout()

        grp_Layout = QtWidgets.QHBoxLayout()
        grp_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Channel_Label, self.Channel_RB_1, self.Channel_RB_2), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Mid_Layout, grp_Layout, '')

        grp_Layout = QtWidgets.QHBoxLayout()
        grp_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Mode_Label, self.Mode_RB_VOLT, self.Mode_RB_CURR), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Mid_Layout, grp_Layout, '')

        grp_Layout = QtWidgets.QHBoxLayout()
        grp_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Sen_Mode_Label, self.Sen_Mode_RB_VOLT, self.Sen_Mode_RB_CURR), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Mid_Layout, grp_Layout, '')

        grp_Layout = QtWidgets.QHBoxLayout()
        grp_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Compliance_Label, self.Compliance_Entry), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Mid_Layout, grp_Layout, '')

        grp_Layout = QtWidgets.QHBoxLayout()
        grp_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Func_Label, self.Func_RB_DC, self.Func_RB_PULS), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Mid_Layout, grp_Layout, '')

        grp_Layout = QtWidgets.QHBoxLayout()
        grp_Layout.addLayout(
            UU.WidgetDesign.Layout_Widget((self.PLC_Label, self.PLC_RB_001, self.PLC_RB_01, self.PLC_RB_1, self.PLC_RB_10), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Mid_Layout, grp_Layout, '')

        grp_Layout = QtWidgets.QHBoxLayout()
        grp_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.FWire_Label, self.FWire_RB_OFF, self.FWire_RB_ON), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Mid_Layout, grp_Layout, '')

        UU.WidgetDesign.Layout_Frame_Layout(Layout, Mid_Layout, 'Equipment Configuration')

    def UI_Component(self):

        LabelSize = (150, 30)
        EntrySize = (200, 30)

        self.EquipmentName_Label = QtWidgets.QLabel("Equipment Port")
        self.EquipmentName_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.EquipmentName_Entry = QtWidgets.QLineEdit(placeholderText='Find Port with ResourceManager().list_resources()', clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.EquipmentName_Entry,self.IDN, EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)
        self.EquipmentName_Entry.textChanged.connect(lambda checked=False: self.UpdateIDN())

        self.Connection_Button = QtWidgets.QPushButton("Connection")
        self.Connection_Button.setFixedSize(LabelSize[0], LabelSize[1])
        self.Status_Label = QtWidgets.QLabel("DisConnected")
        self.Status_Label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.Status_Label.setFixedSize(EntrySize[0], EntrySize[1])
        self.Status_Label.setStyleSheet('background-color: red')

        # self.ConnectedEquipment_Label = QtWidgets.QLabel("IDN: ")
        # self.ConnectedEquipment_Label.setFixedSize(1.5*LabelSize[0], LabelSize[1])

        self.EvaluationItemList_Label = QtWidgets.QLabel("Evaluation Item")
        self.EvaluationItemList_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.EvaluationItemList_Combobox = QtWidgets.QComboBox()
        self.EvaluationItemList_Combobox.addItems(['Photodiode IV', 'MOSFET I-Vg'])

        self.Channel_Label = QtWidgets.QLabel("Channel")
        self.Channel_Label.setFixedSize(LabelSize[0], int(LabelSize[1]/3))
        self.Channel_RB_1 = QtWidgets.QRadioButton('CH 1')
        self.Channel_RB_2 = QtWidgets.QRadioButton('CH 2')

        self.Mode_Label = QtWidgets.QLabel("Source")
        self.Mode_Label.setFixedSize(LabelSize[0], int(LabelSize[1]/3))
        self.Mode_RB_VOLT = QtWidgets.QRadioButton('Voltage')
        self.Mode_RB_CURR = QtWidgets.QRadioButton('Current')

        self.Sen_Mode_Label = QtWidgets.QLabel("Sense")
        self.Sen_Mode_Label.setFixedSize(LabelSize[0], int(LabelSize[1]/3))
        self.Sen_Mode_RB_VOLT = QtWidgets.QRadioButton('Voltage')
        self.Sen_Mode_RB_CURR = QtWidgets.QRadioButton('Current')

        self.Sen_Mode_RB_CURR.toggled.connect(lambda checked=False: self.UpdateComplianceLabel())
        self.Sen_Mode_RB_VOLT.toggled.connect(lambda chekced=False: self.UpdateComplianceLabel())

        self.Compliance_Label = QtWidgets.QLabel("Compliance [A]")
        self.Compliance_Label.setFixedSize(LabelSize[0], int(LabelSize[1]/2))
        self.Compliance_Entry = QtWidgets.QLineEdit(placeholderText='Write Sensing Limit', clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Compliance_Entry, '100E-6', EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.Func_Label = QtWidgets.QLabel("Wave Form")
        self.Func_Label.setFixedSize(LabelSize[0], int(LabelSize[1]/3))
        self.Func_RB_DC = QtWidgets.QRadioButton('DC')
        self.Func_RB_PULS = QtWidgets.QRadioButton('Pulse')

        self.PLC_Label = QtWidgets.QLabel("PLC")
        self.PLC_Label.setFixedSize(LabelSize[0], int(LabelSize[1]/3))
        self.PLC_RB_001 = QtWidgets.QRadioButton('0.01')
        self.PLC_RB_01 = QtWidgets.QRadioButton('0.1')
        self.PLC_RB_1 = QtWidgets.QRadioButton('1')
        self.PLC_RB_10 = QtWidgets.QRadioButton('10')

        self.FWire_Label = QtWidgets.QLabel("Four Wire Mode")
        self.FWire_Label.setFixedSize(LabelSize[0], int(LabelSize[1]/3))
        self.FWire_RB_OFF = QtWidgets.QRadioButton('OFF')
        self.FWire_RB_ON = QtWidgets.QRadioButton('ON')

        self.UI_Default()
    def UI_Default(self):
        self.Channel_RB_1.setChecked(True)
        self.Mode_RB_VOLT.setChecked(True)
        self.Sen_Mode_RB_CURR.setChecked(True)
        self.Func_RB_DC.setChecked(True)
        self.PLC_RB_001.setChecked(True)
        self.FWire_RB_OFF.setChecked(True)

    def BindConfigurationVariables(self):
        Vars = {
                'Equipment': self.EquipmentName_Entry.text(),
                'Evaluation': self.EvaluationItemList_Combobox.currentText(),
                'Channel': 1 if self.Channel_RB_1.isChecked() else 2,
                'Mode': 'VOLT' if self.Mode_RB_VOLT.isChecked() else 'CURR',
                'Sense_Mode': 'CURR' if self.Sen_Mode_RB_CURR.isChecked() else 'VOLT',
                'Compliance': float(self.Compliance_Entry.text()),
                'Func': 'DC' if self.Func_RB_DC.isChecked() else 'PULS',
                'PLC': 0.01 if self.PLC_RB_001.isChecked() else (0.1 if self.PLC_RB_01.isChecked() else (1 if self.PLC_RB_1.isChecked() else 10)),
                'FWire': False if self.FWire_RB_OFF.isChecked() else True
                }
        self.VarList.emit(Vars)

    def UpdateIDN(self):
        self.IDN = self.EquipmentName_Entry.text()
        self.BindConfigurationVariables()

    def UpdateComplianceLabel(self):
        rb = self.sender()

        if rb.text() == 'Current':
            self.Compliance_Label.setText('Compliance [A]')

        else:
            self.Compliance_Label.setText('Compliance [V]')

    def EquipmentConnect(self, IDN, Label):
        try:
            Equipment = ResourceManager().open_resource(IDN)
            Label.setText(f"{Equipment.manufacturer_name} {Equipment.model_name}")
            Label.setStyleSheet('background-color: lightgreen')
            # self.ConnectedEquipment_Label.setText(f"IDN: ")
        except VisaIOError:
            Equipment = None
            Label.setText("DisConnected")
            Label.setStyleSheet('background-color: red')
            # self.ConnectedEquipment_Label.setText(f"IDN: {Equipment}")

        self.Handler.emit(Equipment)

    # def UpdateCH(self):
    #     rb = self.sender()
    #     if rb.isChecked():
    #         print(rb.text())


class PhotodiodeIV_EvaluationConfigWidget(QtWidgets.QWidget):
    VarList = QtCore.pyqtSignal(dict)

    def __init__(self, ConfigVar, parent=None):
        super(PhotodiodeIV_EvaluationConfigWidget, self).__init__(parent)

        Layout = QtWidgets.QVBoxLayout()

        self.initUI(Layout, ConfigVar)
        self.setLayout(Layout)
        self.Handler = None

    def initUI(self, Layout, ConfigVar):
        self.UI_Component(ConfigVar)
        self.UI_Layout(Layout)

    def UI_Layout(self, Layout):

        Mid_Layout = QtWidgets.QVBoxLayout()
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Bias_Range_Label, self.Bias_Start_Entry, self.Bias_End_Entry), 'Horizontal'))
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Bias_Step_Label, self.Bias_Step_Entry), 'Horizontal'))
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Time_Settling_Label, self.Time_Settling_Entry), 'Horizontal'))
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Time_Sampling_Label, self.Time_Sampling_Entry), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Layout, Mid_Layout, 'Necessary Parameters')

        Mid_Layout = QtWidgets.QVBoxLayout()
        Mid_Layout.addWidget(self.Activate_Rest_Button)
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Bias_Rest_Label, self.Bias_Rest_Entry), 'Horizontal'))
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Time_Rest_Label, self.Time_Rest_Entry), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Layout, Mid_Layout, 'Optional Parameters')

        Mid_Layout = QtWidgets.QVBoxLayout()
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.PauseResume_Button, self.Stop_Button, self. Save_Button), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Layout, Mid_Layout, 'Measurement')

    def UI_Component(self, ConfigVar):

        LabelSize = (150, 30)
        EntrySize = (200, 30)

        self.Bias_Range_Label = QtWidgets.QLabel("Bias Range [V]")
        self.Bias_Range_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Bias_Start_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Bias_Start_Entry, ConfigVar['Vstart'], (EntrySize[0]/2, EntrySize[1]), QtCore.Qt.AlignmentFlag.AlignRight)
        self.Bias_End_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Bias_End_Entry, ConfigVar['Vend'], (EntrySize[0]/2, EntrySize[1]), QtCore.Qt.AlignmentFlag.AlignRight)

        self.Bias_Step_Label = QtWidgets.QLabel("Bias Step [V]")
        self.Bias_Step_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Bias_Step_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Bias_Step_Entry, ConfigVar['Vstep'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.Time_Settling_Label = QtWidgets.QLabel("Settling Time [s]")
        self.Time_Settling_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Time_Settling_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Time_Settling_Entry, ConfigVar['ts'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.Time_Sampling_Label = QtWidgets.QLabel("Sampling Time [s]")
        self.Time_Sampling_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Time_Sampling_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Time_Sampling_Entry, ConfigVar['dt'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.Activate_Rest_Button = QtWidgets.QCheckBox("Activate Resting Operation")
        self.Activate_Rest_Button.setChecked(True)

        self.Bias_Rest_Label = QtWidgets.QLabel("Resting Bias [V]")
        self.Bias_Rest_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Bias_Rest_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Bias_Rest_Entry, ConfigVar['VRest'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.Time_Rest_Label = QtWidgets.QLabel("Resting Time [s]")
        self.Time_Rest_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Time_Rest_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Time_Rest_Entry, ConfigVar['tRest'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.PauseResume_Button = QtWidgets.QPushButton()
        self.PauseResume_Button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        self.PauseResume_Button.setFixedSize(int((EntrySize[0]+LabelSize[0])/3), int((EntrySize[1]+LabelSize[1])/3))

        self.Stop_Button = QtWidgets.QPushButton()
        self.Stop_Button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaStop))
        self.Stop_Button.setFixedSize(int((EntrySize[0]+LabelSize[0])/3), int((EntrySize[1]+LabelSize[1])/3))

        self.Save_Button = QtWidgets.QPushButton()
        self.Save_Button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton))
        self.Save_Button.setFixedSize(int((EntrySize[0]+LabelSize[0])/3), int((EntrySize[1]+LabelSize[1])/3))

        self.Bias_Start_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Bias_End_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Bias_Step_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Time_Settling_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Time_Sampling_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Bias_Rest_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Time_Rest_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Activate_Rest_Button.toggled.connect(lambda checked=False: self.UpdateOptionGroup(self.Activate_Rest_Button, self.Bias_Rest_Entry, self.Time_Rest_Entry))
        self.Activate_Rest_Button.toggled.connect(lambda checked=False: self.BindConfigurationVariables())

    def BindConfigurationVariables(self):
        try:
            Vars = {'Vstart': float(self.Bias_Start_Entry.text()),
                    'Vend': float(self.Bias_End_Entry.text()),
                    'Vstep': float(self.Bias_Step_Entry.text()),
                    'ts': float(self.Time_Settling_Entry.text()),
                    'dt': float(self.Time_Sampling_Entry.text()),
                    'Rest': self.Activate_Rest_Button.isChecked(),
                    'VRest': float(self.Bias_Rest_Entry.text()),
                    'tRest': float(self.Time_Rest_Entry.text())}
            self.VarList.emit(Vars)
        except ValueError:
            pass

    def UpdateOptionGroup(self, BTN, Entry1, Entry2):

        if BTN.isChecked():
            Entry1.setEnabled(True)
            Entry2.setEnabled(True)
        else:
            Entry1.setDisabled(True)
            Entry2.setDisabled(True)


class MOSFET_IVg_EvaluationConfigWidget(QtWidgets.QWidget):
    VarList = QtCore.pyqtSignal(dict)

    def __init__(self, ConfigVar, parent=None):
        super(MOSFET_IVg_EvaluationConfigWidget, self).__init__(parent)

        Layout = QtWidgets.QVBoxLayout()

        self.initUI(Layout, ConfigVar)
        self.setLayout(Layout)
        self.Handler = None

    def initUI(self, Layout, ConfigVar):
        self.UI_Component(ConfigVar)
        self.UI_Layout(Layout)

    def UI_Layout(self, Layout):

        Mid_Layout = QtWidgets.QVBoxLayout()
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Bias_Range_Label, self.Bias_Start_Entry, self.Bias_End_Entry), 'Horizontal'))
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Bias_Step_Label, self.Bias_Step_Entry), 'Horizontal'))
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Time_Sampling_Label, self.Time_Sampling_Entry), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Layout, Mid_Layout, 'Gate Channel Settings')

        Mid_Layout = QtWidgets.QVBoxLayout()
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Vd_Label, self.Vd_Start_Entry_VRest, self.Vd_End_Entry_ts), 'Horizontal'))
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.Vd_Step_Label, self.Vd_Step_Entry_tRest), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Layout, Mid_Layout, 'Drain Channel Settings')

        Mid_Layout = QtWidgets.QVBoxLayout()
        Mid_Layout.addLayout(UU.WidgetDesign.Layout_Widget((self.PauseResume_Button, self.Stop_Button, self. Save_Button), 'Horizontal'))
        UU.WidgetDesign.Layout_Frame_Layout(Layout, Mid_Layout, 'Measurement')

    def UI_Component(self, ConfigVar):

        LabelSize = (150, 30)
        EntrySize = (200, 30)

        self.Bias_Range_Label = QtWidgets.QLabel("Bias Range [V]")
        self.Bias_Range_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Bias_Start_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Bias_Start_Entry, ConfigVar['Vstart'], (EntrySize[0]/2, EntrySize[1]), QtCore.Qt.AlignmentFlag.AlignRight)
        self.Bias_End_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Bias_End_Entry, ConfigVar['Vend'], (EntrySize[0]/2, EntrySize[1]), QtCore.Qt.AlignmentFlag.AlignRight)

        self.Bias_Step_Label = QtWidgets.QLabel("Bias Step [V]")
        self.Bias_Step_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Bias_Step_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Bias_Step_Entry, ConfigVar['Vstep'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.Time_Sampling_Label = QtWidgets.QLabel("Sampling Time [s]")
        self.Time_Sampling_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Time_Sampling_Entry = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Time_Sampling_Entry, ConfigVar['dt'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.Vd_Label = QtWidgets.QLabel("Drain Bias Range [V]")
        self.Vd_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Vd_Start_Entry_VRest = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Vd_Start_Entry_VRest, ConfigVar['VRest'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)
        self.Vd_End_Entry_ts = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Vd_End_Entry_ts, ConfigVar['ts'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.Vd_Step_Label = QtWidgets.QLabel("Drain Bias Step [V]")
        self.Vd_Step_Label.setFixedSize(LabelSize[0], LabelSize[1])
        self.Vd_Step_Entry_tRest = QtWidgets.QLineEdit(clearButtonEnabled=True)
        UU.WidgetDesign.Init_Entry(self.Vd_Step_Entry_tRest, ConfigVar['tRest'], EntrySize, QtCore.Qt.AlignmentFlag.AlignRight)

        self.PauseResume_Button = QtWidgets.QPushButton()
        self.PauseResume_Button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        self.PauseResume_Button.setFixedSize(int((EntrySize[0]+LabelSize[0])/3), int((EntrySize[1]+LabelSize[1])/3))

        self.Stop_Button = QtWidgets.QPushButton()
        self.Stop_Button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaStop))
        self.Stop_Button.setFixedSize(int((EntrySize[0]+LabelSize[0])/3), int((EntrySize[1]+LabelSize[1])/3))

        self.Save_Button = QtWidgets.QPushButton()
        self.Save_Button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton))
        self.Save_Button.setFixedSize(int((EntrySize[0]+LabelSize[0])/3), int((EntrySize[1]+LabelSize[1])/3))

        self.Bias_Start_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Bias_End_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Bias_Step_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Time_Sampling_Entry.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Vd_Start_Entry_VRest.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Vd_End_Entry_ts.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())
        self.Vd_Step_Entry_tRest.textChanged.connect(lambda checked=False: self.BindConfigurationVariables())

    def BindConfigurationVariables(self):
        try:
            Vars = {'Vstart': float(self.Bias_Start_Entry.text()),
                    'Vend': float(self.Bias_End_Entry.text()),
                    'Vstep': float(self.Bias_Step_Entry.text()),
                    'dt': float(self.Time_Sampling_Entry.text()),
                    'VRest': float(self.Vd_Start_Entry_VRest.text()),
                    'ts': float(self.Vd_End_Entry_ts.text()),
                    'tRest': float(self.Vd_Step_Entry_tRest.text())}
            self.VarList.emit(Vars)
        except ValueError:
            pass

