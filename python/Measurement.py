from pyvisa import *
from PyQt6 import QtCore
import time
import Function_Utility as FU

# Test Code
'''
inst.write(':sour1:func:mode VOLT')
inst.write(':sour1:func DC')
inst.write(':sour1:volt:mode swe')
inst.write(':sour1:volt:rang 10')
inst.write(':sour1:volt:star 1')
inst.write(':sour1:volt:stop 2')
inst.write(':sour1:volt:poin 11')

print(inst.query(':sour1:func:mode?'))
print(inst.query(':sour1:func?'))
print(inst.query(':sour1:volt:mode?'))
print(inst.query(':sour1:volt1:rang?'))
print(inst.query(':sour1:volt:star?'))
print(inst.query(':sour1:volt:stop?'))
print(inst.query(':sour1:volt:poin?'))

'''


class PhotodiodeIV(QtCore.QThread):
    Data = QtCore.pyqtSignal(str)
    Bias = QtCore.pyqtSignal(str)
    Time = QtCore.pyqtSignal(str)

    def __init__(self, ConfigVar, Handler, parent=None):
        QtCore.QThread.__init__(self)
        QtCore.QCoreApplication.processEvents()

        self.ConfigVar = ConfigVar
        self.Handler = Handler
        self.running = False
        self.program_run = True

        self.Handler.timeout = 1000*int(ConfigVar['dt'] + 2) if self.Handler.timeout < 1000*ConfigVar['dt'] else self.Handler.timeout

    def start_measurement(self):
        QtCore.QCoreApplication.processEvents()
        self.program_run = True
        self.running = True
        print("Start Measurement")

    def stop_measurement(self):
        self.running = False
        self.program_run = False
        print("Stop Measurement")

    def Pause(self):
        self.running = False
        print("Pause")

    def exit(self):
        self.stop_measurement()
        return

    def run(self):
        QtCore.QCoreApplication.processEvents()
        FU.SMUControl.Initialization(self.Handler)
        FU.SMUControl.Config(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], self.ConfigVar['Sense_Mode'], self.ConfigVar['Func'],
                          self.ConfigVar['Compliance'], self.ConfigVar['PLC'], self.ConfigVar['FWire'])
        FU.SMUControl.Config_Trig(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], self.ConfigVar['Vstart'],
                               'TIM', src_period = self.ConfigVar['dt'], src_point = '1', src_delay='0',
                               sen_period = self.ConfigVar['dt'], sen_point = int(self.ConfigVar['ts']/self.ConfigVar['dt'] + 1), sen_delay='0')

        # FU.SMUControl.Set_Trig_Data_Sen(self.Handler, f'{self.ConfigVar["Sense_Mode"]}')
        FU.SMUControl.Set_Trig_Data_Sen(self.Handler, f'TIME, {self.ConfigVar["Sense_Mode"]}')
        DataSize = max(int(1/self.ConfigVar['FPS']/self.ConfigVar['dt']), 1)

        self.Handler.write(':SENS1:CURR:NPLC:AUTO ON')

        'Trigger Method'

        if self.ConfigVar['Rest']:
            V_Now = self.ConfigVar['Vstart']
            Rest = True
            while self.program_run:
                tic = time.time()

                while self.running:
                    k = 0
                    if Rest:
                        self.Bias.emit(f'V={V_Now}')
                        FU.SMUControl.Start_Trig_srcFixed(self.Handler, self.ConfigVar['Channel'],
                                                          self.ConfigVar['Mode'], self.ConfigVar['VRest'],
                                                          int(self.ConfigVar['tRest'] / self.ConfigVar['dt'] + 1))
                    else:
                        self.Bias.emit(f'Bias')
                        FU.SMUControl.Start_Trig_srcFixed(self.Handler, self.ConfigVar['Channel'],
                                                          self.ConfigVar['Mode'], V_Now,
                                                          int(self.ConfigVar['ts'] / self.ConfigVar['dt'] + 1))

                    tictic = time.time()
                    while (time.time() - tictic) < DataSize * self.ConfigVar['dt']:
                        continue

                    while self.program_run and self.running:
                        try:
                            tictic = time.time()
                            data = FU.SMUControl.Get_Trig_Data_Sen(self.Handler, self.ConfigVar['Channel'], k*DataSize, DataSize)
                            self.Data.emit(data)
                            k = k + 1

                            # print(data[-14:])

                            if (~Rest and (time.time() - tic) > self.ConfigVar['ts']) or (Rest and (time.time() - tic) > self.ConfigVar['tRest']):
                                time.sleep(0.1)
                                tic = time.time()
                                break

                            while (time.time() - tictic) < DataSize*self.ConfigVar['dt']:
                                continue

                        except VisaIOError:
                            self.Handler.clear()
                            continue

                    if Rest:
                        Rest = False
                    else:
                        Rest = True
                        V_Now = V_Now + self.ConfigVar['Vstep']
                        if V_Now > self.ConfigVar['Vend']:
                            self.Handler.clear()
                            time.sleep(0.1)
                            self.stop_measurement()
                            FU.SMUControl.Stop(self.Handler, self.ConfigVar['Channel'])
                            self.Bias.emit(f'Finished')
                            break

                    time.sleep(0.1)



        else:
            V_Now = self.ConfigVar['Vstart']

            while self.program_run:
                tic = time.time()
                while self.running:

                    k = 0
                    self.Bias.emit(f'V={V_Now}')
                    FU.SMUControl.Start_Trig_srcFixed(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], V_Now, int(self.ConfigVar['ts'] / self.ConfigVar['dt'] + 1))

                    tictic = time.time()
                    while (time.time() - tictic) < DataSize * self.ConfigVar['dt']:
                        continue

                    while self.program_run and self.running:
                        try:
                            tictic = time.time()
                            data = FU.SMUControl.Get_Trig_Data_Sen(self.Handler, self.ConfigVar['Channel'], k*DataSize, DataSize)
                            self.Data.emit(data)
                            k = k+1

                            if (time.time() - tic) > self.ConfigVar['ts']:
                                time.sleep(0.1)
                                tic = time.time()
                                break

                            while (time.time() - tictic) < DataSize*self.ConfigVar['dt']:
                                continue

                        except VisaIOError:
                            self.Handler.clear()
                            continue

                    V_Now = V_Now + self.ConfigVar['Vstep']

                    if V_Now > self.ConfigVar['Vend']:
                        self.Handler.clear()
                        time.sleep(0.1)
                        self.stop_measurement()
                        FU.SMUControl.Stop(self.Handler, self.ConfigVar['Channel'])
                        self.Bias.emit(f'Finished')
                        break

                    time.sleep(0.1)

        'DC Sweep Method'

        # if self.ConfigVar['Rest']:
        #     V_Now = self.ConfigVar['Vstart']
        #     Rest = True
        #     FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], self.ConfigVar['VRest'])
        #     while self.program_run:
        #         tic = time.time()
        #         while self.running:
        #             self.Bias.emit(f'V={V_Now}') if Rest else self.Bias.emit(f'Bias')
        #
        #             while self.program_run and self.running:
        #                 try:
        #                     tictic = time.time()
        #                     self.Data.emit(FU.SMUControl.Get_Single_Data(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Sense_Mode']))
        #                     self.Time.emit(f'{time.time() - tic}')
        #
        #                     if (~Rest and (time.time() - tic) > self.ConfigVar['ts']) or (Rest and (time.time() - tic) > self.ConfigVar['tRest']):
        #                         time.sleep(0.1)
        #                         tic = time.time()
        #                         break
        #
        #                     while (time.time() - tictic) < self.ConfigVar['dt']:
        #                         continue
        #
        #                 except VisaIOError:
        #                     self.Handler.clear()
        #                     continue
        #
        #             if Rest:
        #                 Rest = False
        #                 FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], V_Now)
        #             else:
        #                 Rest = True
        #                 FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], self.ConfigVar['VRest'])
        #                 V_Now = V_Now + self.ConfigVar['Vstep']
        #                 if V_Now > self.ConfigVar['Vend']:
        #                     time.sleep(0.1)
        #                     self.stop_measurement()
        #                     FU.SMUControl.Stop(self.Handler, self.ConfigVar['Channel'])
        #                     self.Bias.emit(f'Finished')
        #                     break
        #
        #
        # else:
        #     V_Now = self.ConfigVar['Vstart']
        #     FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], V_Now)
        #     while self.program_run:
        #         tic = time.time()
        #         while self.running:
        #             self.Bias.emit(f'V={V_Now}')
        #             while self.program_run and self.running:
        #                 try:
        #                     self.Data.emit(FU.SMUControl.Get_Single_Data(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Sense_Mode']))
        #                     self.Time.emit(f'{time.time() - tic}')
        #
        #                     if time.time() - tic > self.ConfigVar['ts']:
        #                         tic = time.time()
        #                         break
        #                 except VisaIOError:
        #                     self.Handler.clear()
        #                     continue
        #
        #             V_Now = V_Now + self.ConfigVar['Vstep']
        #             if V_Now > self.ConfigVar['Vend']:
        #                 time.sleep(0.1)
        #                 self.stop_measurement()
        #                 FU.SMUControl.Stop(self.Handler, self.ConfigVar['Channel'])
        #                 self.Bias.emit(f'Finished')
        #                 break
        #
        #             FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], V_Now)
        #
        #             # SMUControl.Start_Trig_srcFixed(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], V_Now)
        #
        #


class MOSFET_IVg(QtCore.QThread):
    Data = QtCore.pyqtSignal(str)
    Bias = QtCore.pyqtSignal(str)

    def __init__(self, ConfigVar, Handler, parent=None):
        QtCore.QThread.__init__(self)
        QtCore.QCoreApplication.processEvents()

        self.ConfigVar = ConfigVar
        self.Handler = Handler
        self.running = False
        self.program_run = True

        self.Handler.timeout = 1000*int(ConfigVar['dt'] + 2) if self.Handler.timeout < 1000*ConfigVar['dt'] else self.Handler.timeout

    def start_measurement(self):
        QtCore.QCoreApplication.processEvents()
        self.program_run = True
        self.running = True
        print("Start Measurement")

    def stop_measurement(self):
        self.running = False
        self.program_run = False
        print("Stop Measurement")

    def Pause(self):
        self.running = False
        print("Pause")

    def exit(self):
        self.stop_measurement()
        return

    def run(self):
        QtCore.QCoreApplication.processEvents()
        FU.SMUControl.Initialization(self.Handler)
        FU.SMUControl.Config(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], self.ConfigVar['Sense_Mode'], self.ConfigVar['Func'],
                          self.ConfigVar['Compliance'], self.ConfigVar['PLC'], self.ConfigVar['FWire'])

        'DC Sweep Method'

        # if self.ConfigVar['Rest']:
        #     V_Now = self.ConfigVar['Vstart']
        #     Rest = True
        #     FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], self.ConfigVar['VRest'])
        #     while self.program_run:
        #         tic = time.time()
        #         while self.running:
        #             self.Bias.emit(f'V={V_Now}') if Rest else self.Bias.emit(f'Bias')
        #
        #             while self.program_run and self.running:
        #                 try:
        #                     tictic = time.time()
        #                     self.Data.emit(FU.SMUControl.Get_Single_Data(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Sense_Mode']))
        #                     self.Time.emit(f'{time.time() - tic}')
        #
        #                     if (~Rest and (time.time() - tic) > self.ConfigVar['ts']) or (Rest and (time.time() - tic) > self.ConfigVar['tRest']):
        #                         time.sleep(0.1)
        #                         tic = time.time()
        #                         break
        #
        #                     while (time.time() - tictic) < self.ConfigVar['dt']:
        #                         continue
        #
        #                 except VisaIOError:
        #                     self.Handler.clear()
        #                     continue
        #
        #             if Rest:
        #                 Rest = False
        #                 FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], V_Now)
        #             else:
        #                 Rest = True
        #                 FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], self.ConfigVar['VRest'])
        #                 V_Now = V_Now + self.ConfigVar['Vstep']
        #                 if V_Now > self.ConfigVar['Vend']:
        #                     time.sleep(0.1)
        #                     self.stop_measurement()
        #                     FU.SMUControl.Stop(self.Handler, self.ConfigVar['Channel'])
        #                     self.Bias.emit(f'Finished')
        #                     break
        #
        #
        V_Now = self.ConfigVar['Vstart']
        FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], V_Now)
        while self.program_run:
            tic = time.time()
            while self.running:
                self.Bias.emit(f'V={V_Now}')
                while self.program_run and self.running:
                    try:
                        self.Data.emit(FU.SMUControl.Get_Single_Data(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Sense_Mode']))
                        self.Time.emit(f'{time.time() - tic}')

                        if time.time() - tic > self.ConfigVar['ts']:
                            tic = time.time()
                            break
                    except VisaIOError:
                        self.Handler.clear()
                        continue

                V_Now = V_Now + self.ConfigVar['Vstep']
                if V_Now > self.ConfigVar['Vend']:
                    time.sleep(0.1)
                    self.stop_measurement()
                    FU.SMUControl.Stop(self.Handler, self.ConfigVar['Channel'])
                    self.Bias.emit(f'Finished')
                    break

                FU.SMUControl.Start(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], V_Now)

                # SMUControl.Start_Trig_srcFixed(self.Handler, self.ConfigVar['Channel'], self.ConfigVar['Mode'], V_Now)

        #
