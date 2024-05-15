
class SMUControl:
    @staticmethod
    def Initialization(inst):
        # inst.write("*CLS")
        inst.write("*RST")
    @staticmethod
    def CheckInstrument(inst):
        return inst.query("*IDN?")

    @staticmethod
    def Config(inst, channel, mode, sen_mode, func, limit, nplc, wire, v1 = 0, v2 = 0, src_mode = 'FIX', point = 0):
        # inst, '1', 'VOLT', 'CURR', 'DC', 1E-6, 0.01, False
        SMUControl._set_src(inst, channel, mode)
        SMUControl._set_src_func(inst, channel, func)
        SMUControl._set_src_mode(inst, channel, mode, src_mode)
        SMUControl._set_sense_limit(inst, channel, sen_mode, limit)
        SMUControl._set_sense_speed(inst, channel, nplc, sen_mode)
        SMUControl._set_sense_wiremode(inst, channel, wire)
        SMUControl._set_src_level_start(inst, channel, mode, v1)
        SMUControl._set_src_level_stop(inst, channel, mode, v2)
        SMUControl._set_src_point(inst, channel, mode, point)

    @staticmethod
    def Start(inst, channel, mode, value):
        SMUControl._set_src_level(inst, channel, mode, value)
        SMUControl._set_src_state(inst, channel, "ON")

    @staticmethod
    def Sweep(inst, channel, mode, value):
        SMUControl._set_src_level(inst, channel, mode, value)

    @staticmethod
    def Stop(inst, channel):
        SMUControl._set_src_state(inst, channel, "OFF")

    @staticmethod
    def Config_Trig(inst, channel, mode, level, trig_mode, src_period, src_point, src_delay, sen_period, sen_point, sen_delay):
        # inst, '1', 'VOLT', 1, 'TIM', 200E-6, 100000, 0, 200E-6, 100000, 0
        SMUControl._set_trig_src_level(inst, channel, mode, level)
        SMUControl._set_trig_src_mode(inst, channel, trig_mode)
        SMUControl._set_trig_src_period(inst, channel, src_period)
        SMUControl._set_trig_src_point(inst, channel, src_point)
        SMUControl._set_trig_src_delay(inst, channel, src_delay)
        SMUControl._set_trig_sense_peroid(inst, channel, sen_period)
        SMUControl._set_trig_sense_point(inst, channel, sen_point)
        SMUControl._set_trig_sense_delay(inst, channel, sen_delay)

    @staticmethod
    def Start_Trig_srcFixed(inst, channel, mode, level, sen_point):
        SMUControl._set_trig_src_level(inst, channel, mode, level)
        SMUControl._set_trig_sense_point(inst, channel, sen_point)
        SMUControl._start_trigger(inst, channel)

    @staticmethod
    def Get_Single_Data(inst, channel, item):
        return SMUControl._get_value(inst, channel, item)
    @staticmethod
    def Get_Trig_Data(inst, channel, item):
        return SMUControl._get_trigger_memory(inst, channel, item)

    @staticmethod
    def Set_Trig_Data_Sen(inst, item):
        SMUControl._set_trigger_memory_sens_data(inst, item)
    @staticmethod
    def Get_Trig_Data_Sen(inst, channel, offset, size):
        return SMUControl._get_trigger_memory_sens(inst, channel, offset, size)

    @staticmethod
    def close(inst):
        inst.close()
    @staticmethod
    def write(inst, command):
        inst.write(command)
    @staticmethod
    def query(inst, query):
        return inst.query(query)

    """Set Write Properties"""
    @staticmethod
    def _set_src(inst, channel, mode):
        # mode: VOLT, CURR
        cmd = f":SOUR{channel}:FUNC:MODE {mode}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_src_func(inst, channel, func):
        # func: DC, PULS
        cmd = f":SOUR{channel}:FUNC {func}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_src_mode(inst, channel, mode, src_mode):
        # src_mode: FIX, SWE
        cmd = f":SOUR{channel}:{mode}:MODE {src_mode}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_src_sweep_spacing(inst, channel, spacing):
        # src_mode: LIN, LOG
        cmd = f":SOUR{channel}:SWE:SPAC {spacing}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_src_range(inst, channel, mode, range):
        # range: number
        cmd = f":SOUR{channel}:{mode}:RANG {range}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_src_state(inst, channel, state):
        # state: ON, OFF
        cmd = f":OUTP{channel} {state}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_src_level(inst, channel, mode, value):
        # level: number within range
        cmd = f":SOUR{channel}:{mode} {value}"
        SMUControl.write(inst, cmd)

    @staticmethod
    def _set_src_level_start(inst, channel, mode, value):
        cmd = f":SOUR{channel}:{mode}:STAR {value}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_src_level_stop(inst, channel, mode, value):
        cmd = f":SOUR{channel}:{mode}:STOP {value}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_src_point(inst, channel, mode, value):
        cmd = f":SOUR{channel}:{mode}:POIN {value}"
        SMUControl.write(inst, cmd)

    """Set Sensing Properties"""
    @staticmethod
    def _set_sense(inst, channel, mode):
        cmd = f":SENS{channel}:FUNC {mode}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_sense_speed(inst, channel, speed, mode):
        # speed: 0.01, 0.1, 1, 10 in PLC
        cmd = f":SENS{channel}:{mode}:NPLC {speed}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_sense_limit(inst, channel, mode, value):
        cmd = f":SENS{channel}:{mode}:PROT {value}"
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_sense_wiremode(inst, channel, four_wire):
        # four_wire: True or False
        cmd = f':SENS{channel}:REM {four_wire}'
        SMUControl.write(inst, cmd)

    """Get Sensed Value"""
    @staticmethod
    def _get_value(inst, channel, mode):
        query = f":MEAS:{mode}? (@{channel})"
        # query = f":SENS{channel}:DATA:LAT?)"
        return SMUControl.query(inst, query)

    """Set Trigger Properties"""
    # point: number
    # period: time
    # delay: time
    @staticmethod
    def _set_trig_src_level(inst, channel, mode, value):
        cmd = f":SOUR{channel}:{mode}:TRIG {value}"
        SMUControl.write(inst, cmd)

    @staticmethod
    def _set_trig_src_mode(inst, channel, trig_mode):
        # trig_mode: TIM, AINT
        cmd = f':TRIG{channel}:SOUR {trig_mode}'
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_trig_src_period(inst, channel, period):
        cmd = f':TRIG{channel}:TRAN:TIM {period}'
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_trig_src_point(inst, channel, point):
        cmd = f':TRIG{channel}:TRAN:COUN {point}'
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_trig_src_delay(inst, channel, delay):
        cmd = f':TRIG{channel}:TRAN:DEL {delay}'
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_trig_sense_peroid(inst, channel, period):
        cmd = f':TRIG{channel}:ACQ:TIM {period}'
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_trig_sense_point(inst, channel, point):
        cmd = f':TRIG{channel}:ACQ:COUN {point}'
        SMUControl.write(inst, cmd)
    @staticmethod
    def _set_trig_sense_delay(inst, channel, delay):
        cmd = f':TRIG{channel}:ACQ:DEL {delay}'
        SMUControl.write(inst, cmd)
    @staticmethod
    def _start_trigger(inst, channel):
        cmd = f':INIT (@{channel})'
        SMUControl.write(inst, cmd)

    @staticmethod
    def _get_trigger_memory(inst, channel, item):
        #item: VOLT, CURR, TIME
        query = f':FETC:ARR:{item}? (@{channel})'
        return SMUControl.query(inst, query)

    @staticmethod
    def _set_trigger_memory_sens_data(inst, item):
        #item: SOUR,CURR,VOLT,RES,TIME,STAT
        cmd = f':FORM:ELEM:SENS {item}'
        SMUControl.write(inst, cmd)

    @staticmethod
    def _get_trigger_memory_sens(inst, channel, offset, size):
        query = f':SENS{channel}:DATA? {offset}, {size}'
        return SMUControl.query(inst, query)
