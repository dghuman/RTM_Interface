import time
import pyvisa


class RTM3004:
    """
    This class creates an instance for the RTM3004 oscilloscope
    as a pyvisa instrument.

    Attributes:
        instrument: The instrument opened using pyvisa.ResourceManager.
        name: Device IP on the network.
        connected: Boolean stating connection is made.
        SimpleMeasurementSatus: Boolean stating that the "SimpleMeasurement" has been setup. Refer to "SimpleMeasurement" method.
        SimpleSetupStatus: Boolean stating that the "SimpleSetup" has been setup. Refer to "SimpleSetup" method.
        wavevolt: Float of the amplitude for the waveform generator output.
    """

    def __init__(self, device_ip):
        """
        Intialization of object.

        Args:
            device_ip: IP address of the oscilloscope on the network. \\
                Requires that the RTM3004 is connected to the network, and recommended to have either a static IP or hostname

        Return: RTM3004 instrument class instance/object.
        """
        print("Initializing RTM3004 oscilloscope...")
        ResourceManager = pyvisa.ResourceManager()
        self.instrument = ResourceManager.open_resource(device_ip)
        self.instrument.timeout = 60 * 1000
        self.name = device_ip
        self.connected = True
        self.SimpleMeasurementStatus = False
        self.SimpleSetupStatus = False
        self.wavevolt = 0
        self.reset()
        print("... done.\n")

    def write(self, message):
        '''
        Wrapper for writing message to the instrument via PyVisa.

        Args:
            message: String of the message being sent. Accepts the R&S RTM3004 protocol.

        Return: None
        '''
        self.instrument.write(message)
        time.sleep(0.01)
        return 

    def ask(self, message):
        '''
        Query the instrument using the PyVisa connection.

        Args: 
            message: String of the query. Accepts the R&S RTM3004 protocol.

        Return: String of returned message.
        '''
        response = self.instrument.query(message)
        return response

    def identify(self):
        '''
        Identify the instrument by returning it's ID.

        Args: 
            None

        Return: String of returned message.
        '''
        return self.ask("*IDN?")

    def reset(self):
        '''
        Reset the device to it's default boot-up state. 

        Args: 
            None

        Return: None
        '''
        self.write("*RST")

    def wait(self, dt=0.5):
        '''
        Sleep loop until the oscilloscope returns a ready status.

        Args: 
            dt: Float of the time to wait between oscilloscope queries.

        Return: None
        '''
        while True:
            done = self.ask("*OPC?")
            if done == "1\n":
                break
            time.sleep(dt)

    def getTermination(self, channel=1):
        '''
        Return termination impedance of channel queried.

        Args: 
            channel: Int of channel to be queried in range [1..4]

        Return: String of impedance.
        '''
        return self.ask("PROB%i:SET:IMP?" % (channel))

    def setBandwidth(self, channel=1, bw="FULL"):
        '''
        Set bandwidth of one of the channels.

        Args: 
            channel: Int of channel to be queried in range [1..4].
            bw: String of bandwidth setting, options of "FULL" or "B20".

        Return: None
        '''
        self.write("CHAN%i:BAND %s" % (channel, bw))

    def getBandwidth(self, channel=1):
        '''
        Return bandwidth of on of the channels.

        Args: 
            channel: Int of channel to be queried in range [1..4].

        Return: String of bandwidth setting.
        '''
        return self.ask("CHAN%i:BAND?" % (channel))

    ######################################################
    # HORIZONTAL
    ######################################################

    def setHorizontalScale(self, div=50e-4):
        '''
        Set the horizontal scale of the oscilloscope screen being viewed. 

        Args: 
            div: float for the division scaling. Scale of one div in [1e-6, ...] s/div.

        Return: None
        '''
        self.write("TIM:SCAL %.2e" % (div))

    def getHorizontalScale(self):
        '''
        Get the horizontal scale of the oscilloscope screen being viewed. 

        Args: 
            None

        Return: String of the set horizontal division in seconds.
        '''
        return self.ask("TIM:SCAL?")

    def setHorizontalPosition(self, t=0):
        '''
        Set the horizontal position of the trigger edge on the display.

        Args: 
            t: Float of time offset on the display.

        Return: None
        '''
        self.write("TIM:POS %.6f" % (t))

    def getHorizontalPosition(self):
        '''
        Get the horizontal position of the trigger edge on the display.

        Args: 
            None

        Return: String of horizontal time position.
        '''
        return self.ask("TIM:POS?")

    ######################################################
    # VERTICAL
    ######################################################

    def setVerticalScale(self, channel=1, div=5e-4):
        '''
        Set vertical scale of the display in a particular channel. 

        Args: 
            channel: Int of channel to be queried in range [1..4].
            div: Float setting of one div in the vertical scale, range in [1e-3..10] in Volts.

        Return: None
        '''
        self.write("CHAN%i:SCAL %.3f" % (channel, div))

    def getVerticalScale(self, channel=1):
        '''
        Get vertical scale of the display in a particular channel. 

        Args: 
            channel: Int of channel to be queried in range [1..4].

        Return: String of the channel vertical scaling of the display.
        '''
        return self.ask("CHAN%i:SCAL?" % (channel))

    def setVerticalPosition(self, channel=1, div=0):
        '''
        Set vertical position of the display in a particular channel. 

        Args: 
            channel: Int of channel to be queried in range [1..4].
            div: Float setting of the vertical position in Volts per division.

        Return: None
        '''
        self.write("CHAN%i:POS %.2f" % (channel, div))

    def getVerticalPosition(self, channel=1):
        '''
        Get vertical position of the display in a particular channel. 

        Args: 
            channel: Int of channel to be queried in range [1..4].

        Return: String of the channel vertical position of the display.
        '''
        return self.ask("CHAN%i:POS?" % (channel))

    def setVerticalOffset(self, channel=1, offset=0):
        '''
        Set vertical offset of the display in a particular channel. 

        Args: 
            channel: Int of channel to be queried in range [1..4].
            offset: Float setting of the vertical position in Volts. NOTE: different from setVerticalPosition as it sets in Volts rather than volts/div.

        Return: None
        '''
        self.write("CHAN%i:OFFS %.2f" % (channel, offset))

    def getVerticalOffset(self, channel=1):
        '''
        Get vertical offset of the display in a particular channel. 

        Args: 
            channel: Int of channel to be queried in range [1..4].

        Return: String of the channel vertical offset of the display.
        '''
        return self.ask("CHAN%i:OFFS?" % (channel))

    def checkClipping(self, index=1):
        '''
        Check if a particular index is clipping above the screen limits. Index is set as a measurement and should be set to measuring the Vpp.

        Args: 
            index: Int of the index. 

        Return: Boolean of whether the index is clipping. 
        '''
        status = self.getMeasurementResult(index) == "9.91E+37\n"
        return status

    def fixClipping(self, index=1, channel=1, scale=5e-3):
        '''
        Custom loop that attempts to fix the clipping channel by verifying through a particular index. 

        Args: 
            index: Int of the index. 
            channel: Int of channel to be queried in range [1..4].
            scale: Float starting vertical scale of display. Loop internally increases scale by 25% each time until clipping is resolved.

        Return: Float of final vertical scale that resolved clipping.
        '''
        self.setVerticalScale(channel=channel, div=scale)
        time.sleep(2)
        inscale = scale
        while self.checkClipping(index=index):
            inscale = self.getVerticalScale(channel=channel)
            inscale = 1.25 * float(inscale[:-1])
            self.setVerticalScale(channel=channel, div=inscale)
            time.sleep(3)
            self.wait(10)
        return inscale

    def fixMathClipping(self, index=1, channel=1, scale=5e-3):
        '''
        Custom loop that attempts to fix the clipping Math channel by verifying through a particular index. 

        Args: 
            index: Int of the index. 
            channel: Int of channel to be queried in range [1..4].
            scale: Float starting vertical scale of display. Loop internally increases scale by 25% each time until clipping is resolved.

        Return: Float of final vertical scale that resolved clipping.
        '''
        self.setMathScale(index=channel, scale=scale)
        time.sleep(2)
        while self.checkClipping(index=index):
            inscale = self.getMathScale(index=channel)
            inscale = 1.25 * float(inscale[:-1])
            self.setMathScale(index=channel, div=inscale)
            time.sleep(3)
            self.wait(10)

    ######################################################
    # ACQUISITION
    ######################################################

    def setAcquisitionType(self, mode="REF"):
        '''
        Set the acquisition type of the oscilloscope. 
        REFresh takes the whole waveform.
        AVERage takes and displays an average waveform. 
        ENVelope displays the envelope of the waveform.

        Args: 
            mode: String with options "REF", "AVER" and "ENV".

        Return: None
        '''
        self.write("ACQ:TYPE %s" % (mode))

    def getAcquisitionType(self):
        '''
        Get the acquisition type of the oscilloscope. 
        REFresh takes the whole waveform.
        AVERage takes and displays an average waveform. 
        ENVelope displays the envelope of the waveform.

        Args: 
            None

        Return: String of acquisition type.
        '''
        return self.ask("ACQ:TYPE?")

    def setAcquisitionAuto(self, mode="ON"):
        '''
        Auto set the acquisition mode. 

        Args: 
            mode: String of "ON" or "OFF".

        Return: None
        '''
        self.write("ACQ:POIN:AUT %s" % (mode))

    def getAcquisitionAuto(self):
        '''
        Check if acquisition mode is automatic.

        Args: 
            None

        Return: String of "ON" or "OFF".
        '''
        return self.ask("ACQ:POIN:AUT?")

    def setAcquisitionPoints(self, points=100e3):
        '''
        Set number of points in a waveform to record in a segment. Options are 5k samples to 80M samples.

        Args: 
            points: Float ranging from 5k to 80M.

        Return: None
        '''
        self.write("ACQ:POIN:VAL %.3f" % (points))

    def getAcquisitionPoints(self):
        '''
        Get number of points set in a waveform to record in a segment. 

        Args: 
            None

        Return: Float of number of points.
        '''
        return self.ask("ACQ:POIN:VAL?")

    def setAcquisitionMode(self, mode="AUT"):
        '''
        Set the acquisition mode of the oscilloscope, which determines how the record length is set.

        Args: 
            mode: "AUT", "DMEM" or "MAN".

        Return: None
        '''
        self.write("ACQ:MEM:MODE %s" % (mode))

    def getAcquisitionMode(self):
        '''
        Get the acquisition mode of the oscilloscope, which determines how the record length is set.

        Args: 
            None

        Return: String of acquisition mode. 
        '''
        return self.ask("ACQ:MEM:MODE?")

    ######################################################
    # TRIGGER
    ######################################################

    def setTriggerMode(self, src="A", mode="NORM"):
        '''
        Set the trigger mode for one of two sources. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".
            mode: String option for the trigger mode. "A" has "AUTO" or "NORM", while "B" has "DEL" or "EVENT". 

        Return: None
        '''
        self.write("TRIG:%s:MODE %s" % (src, mode))

    def getTriggerMode(self, src="A"):
        '''
        Get the trigger mode for one of two sources. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".

        Return: String of mode.
        '''
        return self.ask("TRIG:%s:MODE?" % (src))

    def setTriggerType(self, src="A", mode="EDGE"):
        '''
        Set trigger type of a particular source. Only source "A" is listed here. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".
            mode: String option for the trigger mode. Options are "EDGE", "WID", "TV", "RUNT", "LOG", "BUS", "RIS" and "LINE".

        Return: None
        '''
        self.write("TRIG:%s:TYPE %s" % (src, mode))

    def getTriggerType(self, src="A"):
        '''
        Get trigger type of a particular source. Only source "A" is listed here. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".

        Return: String of trigger type.
        '''
        return self.ask("TRIG:%s:TYPE?" % (src))

    def setTriggerSource(self, src="A", channel=1):
        '''
        Set trigger channel of a particular source. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".
            channel: Int of channel to be queried in range [1..4]

        Return: None
        '''
        self.write("TRIG:%s:SOUR CH%i" % (src, channel))

    def getTriggerSource(self, src="A"):
        '''
        Get trigger channel of a particular source. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".

        Return: String of channel set as trigger source.
        '''
        return self.ask("TRIG:%s:SOUR?" % (src))

    def setTriggerEdgeCoupling(self, src="A", mode="DC"):
        '''
        Set trigger edge coupling based on source. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".
            mode: String to set coupling. Options are "DC", "LFR" and "AC".

        Return: None
        '''
        self.write("TRIG:%s:EDGE:COUP %s" % (src, mode))

    def getTriggerEdgeCoupling(self, src="A"):
        '''
        Get trigger edge coupling based on source. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".

        Return: String of the mode.
        '''
        return self.ask("TRIG:%s:EDGE:COUP?" % (src))

    def setTriggerEdgeSlope(self, src="A", mode="RISE"):
        '''
        Set trigger edge slope mode. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".
            mode: String of the mode to set the trigger edge slope. Options are "POS" (positive), "NEG" (negative) and "EITH" (either). 

        Return: None
        '''
        self.write("TRIG:%s:EDGE:SLOP %s" % (src, mode))

    def getTriggerEdgeSlope(self, src="A"):
        '''
        Get trigger edge slope mode. 

        Args: 
            src: String determining the source of the trigger, options being "A" or "B".

        Return: String of the edge trigger mode.
        '''
        return self.ask("TRIG:%s:EDGE:SLOP?" % (src))

    def setTriggerEdgeLevel(self, channel=2, level=0):
        '''
        Set trigger edge level of a particular channel.

        Args: 
            channel: Int of channel to be queried in range [1..4].
            level: Float trigger edge level in volts.

        Return: None
        '''
        self.write("TRIG:A:LEV%i:VAL %.2f" % (channel, level))

    def getTriggerEdgeLevel(self, channel=2):
        '''
        Get trigger edge level of a particular channel.

        Args: 
            channel: Int of channel to be queried in range [1..4].

        Return: Float of trigger edge level.
        '''
        return self.ask("TRIG:A:LEV%i:VAL?" % (channel))

    def setTriggerAutoLevel(self):
        '''
        Set trigger edge level to be automatic.

        Args: 
            None

        Return: None
        '''
        self.write("TRIG:A:FIND")

    ######################################################
    # TRIGGER B
    ######################################################

    def setTriggerBDelayTime(self, time=100e-9):
        '''
        Set trigger B delay time. 

        Args: 
            time: Float delay time of B trigger.

        Return: None
        '''
        self.write("TRIG:B:DEL %.2e" % (time))

    def getTriggerBDelayTime(self):
        '''
        Get trigger B delay time. 

        Args: 
            None

        Return: Float delay time of B trigger.
        '''
        return self.ask("TRIG:B:DEL?")

    ######################################################
    # CURVE DATA
    ######################################################

    def setDataSource(self, channel=1):
        '''
        Set data source from a particular channel.

        Args: 
            channel: Int of channel to be set in range [1..4]

        Return: None
        '''
        self.write("EXP:WAV:SOUR CH%i" % (channel))

    def getDataSource(self):
        '''
        Get data source.

        Args: 
            None

        Return: String of channel set.
        '''
        return self.ask("EXP:WAV:SOUR?")

    def setDataDestination(self, dest="/USB_FRONT/WFM"):
        '''
        Set data destination for waveform. 

        Args: 
            dest: String pointing to the file accessible by the Oscilloscope for saving data.

        Return: None
        '''
        self.write("EXP:WAV:NAME %s" % (dest))

    def getDataDestination(self):
        '''
        Get data destination for waveform. 

        Args: 
            None

        Return: String pointing to the file where the current data is being saved. 
        '''
        return self.ask("EXP:WAV:NAME?")

    def saveWaveformData(self):
        '''
        Save the waveform data to the set destination from the set waveform.

        Args: 
            None

        Return: None
        '''
        self.write("EXP:WAV:SAVE")

    def setDataFormat(self, form="CSV", bitvalue=0):
        '''
        Set the data format in which the waveform data is saved. 

        Args: 
            form: String which sets the data format. Options are "ASC" (ascii), "REAL" (real), "UINT" (uinteger) and "CSV" (csv). 
            bitvalue: Int which determines the accuracy of the saved data in bits. Options are 0, 8, 16, 32.

        Return: None
        '''
        self.write("FORM %s,%i" % (form, bitvalue))

    def getDataFormat(self):
        '''
        Get the data format in which the waveform data is saved. 

        Args: 
            None

        Return: String of the data format being saved. 
        '''
        return self.ask("FORM?")
    
    def getWaveformSampleRate(self):
        '''
        Get the waveform sample rate.

        Args: 
            None

        Return: String of the waveform sample rate.
        '''
        return self.ask("ACQ:SRAT?")

    def getSampleRate(self):
        '''
        Get the sample rate.

        Args: 
            None

        Return: String of the sample rate.
        '''
        return self.ask("ACQ:POIN:ARAT?")

    ######################################################
    # MEASUREMENT
    ######################################################

    def startAcquisition(self):
        '''
        Start the acquisition of the measurement data.

        Args: 
            None

        Return: None
        '''
        self.write("START")

    def stopAcquisition(self):
        '''
        Stop the acquisition of the measurement data.

        Args: 
            None

        Return: None
        '''
        self.write("STOP")

    def setMeasurement(self, index=1, mode="FREQ"):
        '''
        Set the measurement tracked in a particular index. 

        Args: 
            index: int that determines which location the measurement being set is recorded/tracked.
            mode: String that determines the type of measurement recorded. Common modes include "FREQ" (frequency), "PER" (period), "PEAK" (peak), "AMP" (amplitude), and "MEAN" (mean). Refer to R&S Docs for full list.

        Return: None
        '''
        self.write("MEAS%i:MAIN %s" % (index, mode))

    def getMeasurement(self, index=1):
        '''
        Get the measurement tracked in a particular index. 

        Args: 
            index: int that determines which location the measurement being set is recorded/tracked.

        Return: String that refers to the measurement tracked in that particular index.
        '''
        return self.ask("MEAS%i:MAIN?" % (index))

    def toggleMeasurement(self, index=1, state="ON"):
        '''
        Turn the measurement on or off at a particular index.

        Args: 
            index: int that determines which location the measurement being set is recorded/tracked.
            state: String that turns the measurement "ON" or "OFF".

        Return: None
        '''
        self.write("MEAS%i %s" % (index, state))

    def setMeasurementSource(self, index=1, channel=1):
        '''
        Set the source channel for which the measurement of a particular index is recorded.

        Args: 
            index: int that determines which location the measurement being set is recorded/tracked.
            channel: Int of channel to be set in range [1..4]

        Return: None
        '''
        self.write("MEAS%i:SOUR CH%i" % (index, channel))

    def setArbitraryMeasurementSource(self, index, source):
        '''
        Set the measurement source at a particular index. 

        Args: 
            index: int that determines which location the measurement being set is recorded/tracked.
            source: String that determines arbitrary measurment source. Can be channel, math, reference or digital. 

        Return: None
        '''
        self.write(f"MEAS{index}:SOUR {source}")

    def getMeasurementSource(self, index=1):
        '''
        Get the measurement source at a particular index. 

        Args: 
            index: int that determines which location the measurement being set is recorded/tracked.

        Return: String of the measurement source. 
        '''
        return self.ask("MEAS%i:SOUR?" % (index, src))

    def toggleMeasurementStats(self, state="OFF"):
        '''
        Toggle statistics of the measurements being made.

        Args: 
            state: "ON" or "OFF".

        Return: None
        '''
        self.write("MEAS:STAT %s" % (state))

    def resetMeasurementStats(self, ch=1):
        '''
        Reset the meaurement stats being recorded for a particular channel.

        Args: 
            ch: Integar of the channel being set in the range [1..4]

        Return: None
        '''
        self.write("MEAS%i:STAT:RES" % (ch))

    def toggleAutoMeasureTScale(self, state="ON"):
        '''
        Set the auto measure of time scale.

        Args: 
            state: "ON" or "OFF"

        Return: None
        '''
        self.write("MEAS1:TIM:AUTO")

    def setMeasureTScale(self, dt=200e-6):
        '''
        Manually set the time to wait before a measurement is returned. 

        Args: 
            dt: Float of time to wait in seconds. Should be atleast 12*(horizontal scale) + (trigger period) in seconds.

        Return: None
        '''
        self.write("MEAS1:TIM %.3f" % (dt))

    def getMeasurementResult(self, index=1):
        '''
        Readout the measurement result at a particular index.

        Args: 
            index: integar for measurement result.

        Return: String of measurement result.
        '''
        return self.ask("MEAS%i:RES?" % (index))

    def getMeasurementAvg(self, index=1):
        '''
        Readout the measurement average at a particular index.

        Args: 
            index: integar for measurement result. 

        Return: String of measurement average.
        '''
        return self.ask("MEAS%i:RES:AVG?" % (index))

    def getMeasurementStd(self, index=1):
        '''
        Readout the measurement standard deviation at a particular index.

        Args: 
            index: integar for measurement result. 

        Return: String of measurement standard deviation.
        '''
        return self.ask("MEAS%i:RES:STDD?" % (index))

    ######################################################
    # ACQUISITION
    ######################################################

    def setAcquisitionType(self, aq="AVER"):
        '''
        Set the acquisition type of the readout.

        Args: 
            aq: String with options available in documentation. Defaults to "AVER" which is average.

        Return: None
        '''
        self.write(f"ACQ:TYPE {aq}")

    def getAcquisitionType(self):
        '''
        Get the acquisition type of the readout.

        Args: 
            None

        Return: String of acquisition type.
        '''
        return self.ask("ACQ:TYPE?")

    def setAverageCount(self, val=1000):
        '''
        Set the average count value. 

        Args: 
            val:Int that determines the value of of the average count.

        Return: None
        '''
        self.write(f"ACQ:AVER:COUN {val}")

    def getAverageCount(self):
        '''
        Get the average count value. 

        Args: 
            None

        Return: String of the average count value.
        '''
        return self.ask("ACQ:AVER:CURR?")

    def setSampleMode(self, mode="SAMP"):
        '''
        Set the sample mode of the acquisition.

        Args: 
            mode: String that sets the mode, defaults to "SAMP".

        Return: None
        '''
        self.write(f"CHAN:TYPE {mode}")

    def getSampleMode(self):
        '''
        Get the sample mode of the acquisition.

        Args: 
            None

        Return: String of the set sample mode.
        '''
        return self.ask("CHAN:TYPE?")

    def setSampleState(self, state="OFF"):
        '''
        Toggle whether the sample state is on or off.

        Args: 
            state: String of "ON" or "OFF".

        Return: None
        '''
        self.write(f"CHAN:ARIT {state}")

    ######################################################
    # CHANNEL SETUP
    ######################################################

    def toggleChannel(self, channel=1, status="ON"):
        '''
        Toggle whether a particular channel is on or off.

        Args: 
            channel: Int in the range [1..4] which corresponds with one of the four channels.
            status: String that sets the channel in question to "ON" or "OFF".

        Return: None
        '''
        self.write("CHAN%i:STAT %s" % (channel, status))

    def statusChannel(self, channel=1):
        '''
        Check whether a particular channel is on or off.

        Args: 
            channel: Int in the range [1..4] which corresponds with one of the four channels.

        Return: String of the status of that channel.
        '''
        return self.ask("CHAN%i:STAT?" % (channel))

    def setChanCoupling(self, channel=1, coup="DCLimit"):
        '''
        Set the coupling of a particular channel.

        Args: 
            channel: Int in the range [1..4] which corresponds with one of the four channels.
            coup: String which determines the coupling being set. Options are "DCL" (DCLimit), "ACL" (ACLimit), "GND" and "DC". 

        Return: None
        '''
        self.write("CHAN%i:COUP %s" % (channel, coup))

    def getChanCoupling(self, channel=1):
        '''
        Get the coupling of a particular channel.

        Args: 
            channel: Int in the range [1..4] which corresponds with one of the four channels.

        Return: String of the currently set coupling for that particular channel.
        '''
        self.ask("CHAN%i:COUP?" % (channel))

    ######################################################
    # WAVEFORM GENERATOR
    ######################################################

    def setWaveFunction(self, fun="SIN"):
        '''
        Sets the generated waveform to a particular shape.

        Args: 
            fun: String that determines the shape of the generated waveform. Options are: 
                "DC", "SIN" (sinusoid), "SQU" (square), "PULS" (pulse), "TRI" (triangle), "RAMP", "SINC", "ARB" (arbitrary), "EXP" (exponential).

        Return: None
        '''
        self.write("WGEN:FUNC %s" % (fun))

    def getWaveFunction(self):
        '''
        Get the generated waveform shape/function.
        
        Args: 
            None
        
        Return: String of the function setting for the generated waveform.
        '''
        return self.ask("WGEN:FUNC?")

    def setWaveVoltage(self, amp=2.5e-1):
        '''
        Set the amplitude for the generated waveform.
        
        Args: 
            amp: Float of the amplitude being set. 
        
        Return: None
        '''
        self.wavevolt = amp
        self.write("WGEN:VOLT %.2e" % (amp))

    def getWaveVoltage(self):
        '''
        Get the amplitude for the generated waveform.
        
        Args: 
            None
        
        Return: String of the amplitude set for the generated waveform.
        '''
        return self.ask("WGEN:VOLT?")

    def setWaveVoltOffset(self, offset=0):
        '''
        Set the offset of the generated waveform.
        
        Args: 
            offset: Float for setting voltage offset.
        
        Return: None
        '''
        self.write("WGEN:VOLT:OFFS %.2e" % (offset))

    def getWaveVoltOffset(self):
        '''
        Get the offset of the generated waveform.
        
        Args: 
            None
        
        Return: String of the voltage offset value.
        '''
        return self.ask("WGEN:VOLT:OFFS?")

    def setWaveVoltFrequency(self, freq=1e4):
        '''
        Set the waveform frequency in Hz.
        
        Args: 
            freq: Float of the frequency to be set, in Hz.
        
        Return: None
        '''
        self.write("WGEN:FREQ %.2e" % (freq))

    def getWaveVoltFrequency(self):
        '''
        Get the waveform frequency in Hz.
        
        Args: 
            None
        
        Return: String of the set waveform frequency.
        '''
        return self.ask("WGEN:FREQ?")

    def setWaveNoise(self, noise=0):
        '''
        Set the noise in the generated waveform in volts.
        
        Args: 
            noise: Float which determines the noise [V].
        
        Return: None
        '''
        self.write("WGEN:NOIS:ABS %.2e" % (noise))

    def getWaveNoise(self):
        '''
        Get the noise of the generated waveform in volts.
        
        Args: 
            None
        
        Return: String of the noise in volts.
        '''
        return self.ask("WGEN:NOIS:ABS?")

    def toggleWaveform(self, status="OFF"):
        '''
        Toggle if a waveform is enabled or not. 
        
        Args: 
            status: String to which can be set to "ON" or "OFF".
        
        Return: None
        '''
        self.write("WGEN:OUTP %s" % (status))

    def getWaveformStatus(self):
        '''
        Check if the waveform generator is on or off.
        
        Args: 
            None
        
        Return: String which informs the user if the waveform is on or off.
        '''
        return self.ask("WGEN:OUTP?")

    def toggleWaveformBurst(self, status="ON"):
        '''
        Toggle the generated waveform to be output as a burst.
        
        Args: 
            status: String that is "ON" or "OFF" 
        
        Return: None
        '''
        self.write("WGEN:BURS %s" % (status))

    def getWaveformBurst(self):
        '''
        Check if the generated waveform is output as a burst.
        
        Args: 
            None
        
        Return: String which informs if the generated waveform is in burst mode.
        '''
        return self.ask("WGEN:BURS?")

    def setWaveformBurstCount(self, cycles=10):
        '''
        Set the number of cycles that a single burst lasts for.
        
        Args: 
            cycles: Int that determines the number of cycles per burst.
        
        Return: None
        '''
        self.write("WGEN:BURS:NCYC %i" % (cycles))

    def getWaveformBurstCount(self):
        '''
        Get the number of cycles per burst.
        
        Args: 
            None
        
        Return: String containing the burst count information.
        '''
        return self.ask("WGEN:BURS:NCYC?")

    def setWaveformBurstIdle(self, time=1e-1):        
        '''
        Set the idle time between bursts.
        
        Args: 
            time: Float in seconds
        
        Return: None
        '''
        self.write("WGEN:BURS:ITIM %.2e" % (time))

    def getWaveformBurstIdle(self):
        '''
        Get the idle time between bursts.
        
        Args: 
            None
        
        Return: String of idle time between bursts.
        '''
        return self.ask("WGEN:BURS:ITIM?")

    def setStartFreqSweep(self, freq=10e3):
        '''
        Set which frequency the frequency sweep mode starts at.
        
        Args: 
            freq: Float in Hz where the sweep begins.
        
        Return: None
        '''
        self.write(f"WGEN:SWE:FST {freq}")

    def setEndFreqSweep(self, freq=10e4):
        '''
        Set which frequency the frequency sweep mode ends at.
        
        Args: 
            freq: Float in Hz where the sweep ends.
        
        Return: None
        '''
        self.write(f"WGEN:SWE:FEND {freq}")

    def setSweepTime(self, time=1):
        '''
        Set the time over which the frequency sweep takes place.
        
        Args: 
            time: Float which determines the sweep time in seconds.
        
        Return: None
        '''
        self.write(f"WGEN:SWE:TIME {time}")

    def setSweepType(self, style="LIN"):
        '''
        Set the type of frequency sweep. Assumed linear by default.
        
        Args: 
            style: String with options "LIN" (linear), "LOG" (logarithmic), "TRI" (triangle).
        
        Return: None
        '''
        self.write(f"WGEN:SWE:TYPE {style}")

    def toggleSweep(self, toggle="OFF"):
        '''
        Toggle if the frequency sweep is active.
        
        Args: 
            toggle: String of either "ON" or "OFF".
        
        Return: None
        '''
        self.write(f"WGEN:SWE:ENAB {toggle}")

    def getWaveInfo(self):
        '''
        Get the waveform generator information in one tuple.
        
        Args: 
            None
        
        Return: Tuple of strings in the order (wavefunction, amplitude, frequency).
        '''
        wavefunc = self.getWaveFunction()
        wavevolt = self.getWaveVoltage()
        wavefreq = self.getWaveVoltFrequency()
        return wavefunc, wavevolt, wavefreq

    def setWaveInfo(self, fun="SIN", amp=2.5e-1, offset=0, freq=1e4):
        '''
        Set the waveform generator information in one method.
        
        Args: 
            fun: String of the function type. 
            amp: Float of the waveform amplitude in volts. 
            offset: Float of the vertical waveform offset in volts. 
            freq: Float of the waveform frequency in Hz.
        
        Return: None
        '''
        self.setWaveFunction(fun)
        self.setWaveVoltage(amp)
        self.setWaveVoltOffset(offset)
        self.setWaveVoltFrequency(freq)

    ######################################################
    # FFT
    ######################################################

    def enableSpec(self):
        '''
        Enable the spectrogram view of the waveform.
        
        Args: 
            None

        Return: None
        '''
        self.write("SPEC:STAT ON")

    def disableSpec(self):
        '''
        Disable the spectrogram view of the waveform.
        
        Args: 
            None

        Return: None
        '''
        self.write("SPEC:STAT OFF")

    def setSpecChan(self, channel=1):
        '''
        Set the channel that is currently undergoing spectrogram analysis.
        
        Args: 
            channel: Int ranging in [1..4] referring to the channel being analyzed.

        Return: None
        '''
        self.write(f"SPEC:SOUR CH{channel}")

    def setSpecWindowType(self, win="HANN"):
        '''
        Set the spectrum window type of the fft analysis.
        
        Args: 
            win: String of the window setting. Options are "RECT" (rectangular), "HAMM" (hamming), "HANN" (hanning), "BLAC" (blackman-harris), and "FLAT" (flat top).

        Return: None
        '''
        self.write(f"SPEC:FREQ:WIND:TYPE {win}")

    def setSpecScaling(self, scale="DBM"):
        '''
        Set the spectrum scaling of the y-axis.
        
        Args: 
            scale: String that determines the scaling. Options are "LIN" (linear), "DBM", "DBV", "DBUV".

        Return: None
        '''
        self.write(f"SPEC:FREQ:MAGN:SCAL {scale}")

    def setSpecFreqCenter(self, center=25e3):
        '''
        Set the center of the frequency spectrum.
        
        Args: 
            center: Float of the center frequency displayed in Hz.

        Return: None
        '''
        self.write(f"SPEC:FREQ:CENT {int(center)}")

    def setSpecFreqSpan(self, span=50e3):
        '''
        Set the frequency span of the spectrum.
        
        Args: 
            span: Float of the frequency span in Hz. 

        Return: None
        '''
        self.write(f"SPEC:FREQ:SPAN {int(span)}")

    def setSpecFreqStart(self, start=1e3):
        '''
        Start of the frequency spectrum in the display window.
        
        Args: 
            start: Float of starting frequency in Hz.

        Return: None
        '''
        self.write(f"SPEC:FREQ:STAR {int(start)}")

    def getSpecWavData(self):
        '''
        Get the spectrum data.
        
        Args: 
            None

        Return: String of waveform data from the instrument.
        '''
        self.ask("SPEC:WAV:SPEC:DATA?")

    ######################################################
    # MATHEMATICS
    ######################################################

    def setMathScale(self, index=1, scale=1):
        '''
        Set the scale of the math waveform.
        
        Args: 
            index: Int referring to the particular math waveform. In the range [1..5].
            scale: Float setting the value to scale the waveform by.

        Return: None
        '''
        self.write(f"CALC:MATH{index}:SCAL {scale}")

    def getMathScale(self, index=1):
        '''
        Get the scale of the math waveform at that particular waveform.
        
        Args: 
            index: Int referring to the particular math waveform. In the range [1..5].

        Return: String of the scale by which the waveform is multiplied.
        '''
        return self.ask(f"CALC:MATH{index}:SCAL?")

    def subtractChannels(self, channel_one=1, channel_two=2, waveform=1):
        '''
        Subtract two channels and display them as a particular waveform.
        
        Args: 
            channel_one: Int referring to the first channel to be subtracted from.
            channel_two: Int referring to the second channel, which will be subtracted from the first.
            waveform: Int referring to the math waveform where the subtraction will be displayed.

        Return: None
        '''
        self.write(
            f'CALC:MATH{waveform}:EXPR:DEF "SUB(CH{channel_one},CH{channel_two}) in V"'
        )

    def addChannels(self, channel_one=1, channel_two=2, waveform=1):
        '''
        Add two channels and display them as a particular waveform.
        
        Args: 
            channel_one: Int referring to the first channel to be added to.
            channel_two: Int referring to the second channel, which will be added to the first.
            waveform: Int referring to the math waveform where the addition will be displayed.

        Return: None
        '''
        self.write(
            f'CALC:MATH{waveform}:EXPR:DEF "ADD(CH{channel_one},CH{channel_two}) in V"'
        )

    def filterLP(self, waveform=1, ref="M1", freq=10e4):
        '''
        Low-Pass filter to be applied to a particular math waveform.
        
        Args: 
            waveform: Int of the math waveform where the result will be displayed.
            ref: String of the reference waveform which is filtered. The format is "M<i>" where <i> is an integer referring to the math waveform number.
            freq: Float of the frequency where the Low-Pass filter is applied in Hz.

        Return: None
        '''
        self.write(f'CALC:MATH{waveform}:EXPR:DEF "LP({ref},{freq})"')

    def enableMath(self, index=1):
        '''
        Enable a particular math waveform.
        
        Args: 
            index: Integer referring to the math waveform to be enabled. In the range [1..5].

        Return: None
        '''
        self.write(f"CALC:MATH{index}:STAT ON")

    ######################################################
    # CUSTOM SEQUENCES
    ######################################################

    def simpleSetup(self, burst=True, trig=0):
        '''
        Custom sequence created for quick and easy data taking. The prepares the first two channels of the oscilloscope, an edge trigger and generating waveform. The trigger here is set to be on channel 2 and the waveform generator is set to the default values in the simpleWaveform method. 
        
        Args: 
            burst: Boolean which sets the burst functionality of the generating waveform. 
            trig: Float which sets the trigger level.

        Return: None
        '''
        channels = [1, 2]
        for channel in channels:
            self.toggleChannel(channel=channel, status="ON")
            if channel == 2:
                self.setChanCoupling(channel=channel, coup="DCLimit")
            else:
                self.setChanCoupling(channel=channel, coup="ACLimit")
        self.simpleEdgeTrigger(level=trig)
        self.simpleWaveform(cycles=100, burst=burst)
        self.SimpleSetupStatus = True

    def simpleEdgeTrigger(self, channel=2, level=0, coupl="DC", mode="RISE"):
        '''
        Simple trigger that is set on a channel of choice.
        
        Args: 
            channel: Int in the range [1..4] for which the trigger is set.
            level: Float value for the trigger level used.
            coupl: String to determine the coupling of the particular channel.
            mode: String to determine which type of edge trigger is implemented.

        Return: None
        '''
        self.setTriggerMode("A", "NORM")
        self.setTriggerType("A", "EDGE")
        self.setTriggerSource("A", channel)
        self.setTriggerEdgeCoupling("A", coupl)
        self.setTriggerEdgeSlope("A", mode)
        self.setTriggerEdgeLevel(channel, level)

    def simpleWaveform(
        self,
        fun="SIN",
        amp=1,
        offset=0,
        freq=1e4,
        delay=1e-1,
        cycles=5,
        burst=True,
        channel=2,
    ):
        '''
        Simple waveform generator setup. Combines a multitude of the previous waveform generator methods into one for ease-of-use. 
        
        Args: 
            fun: String referring to the function of the generating waveform.
            amp: Float referring to the amplitude of the generated waveform in volts.
            offset: Float referring to the voltage offset in volts.
            freq: Float which sets the frequency of the generated waveform in Hz.
            delay: Float of the time delay between burst waveforms in seconds.
            cycles: Int for the number of cycles that a burst setting would include.
            burst: Boolean which determines if burst mode is enabled.
            channel: Int in the range [1..4] for which the trigger is set.

        Return: None
        '''
        self.toggleWaveform("ON")
        self.setWaveInfo(fun, amp, offset, freq)
        self.setVerticalScale(channel=channel, div=amp / 3)
        self.setVerticalOffset(channel=channel, offset=0)
        if burst:
            self.toggleWaveformBurst("ON")
            self.setWaveformBurstCount(cycles)
            self.setWaveformBurstIdle(delay)

    def setSimpleMeasurements(self):
        '''
        Sets commonly used measurements of the two channels into 8 indices. \\
        In particular, assigns indices 1..4 to channel 1 and 5..8 to channel 2. The following are the recorded measurements: \\
        Measure | Indices
        Peak Amplitudes | 1, 5
        Frequency | 2, 6
        Mean | 3, 7
        
        
        Args: 
            None

        Return: None
        '''
        self.setMeasurementSource(index=1, channel=1)
        self.setMeasurementSource(index=2, channel=1)
        self.setMeasurementSource(index=3, channel=1)
        self.setMeasurementSource(index=4, channel=1)
        self.setMeasurementSource(index=5, channel=2)
        self.setMeasurementSource(index=6, channel=2)
        self.setMeasurementSource(index=7, channel=2)
        self.setMeasurementSource(index=8, channel=2)
        self.setMeasurement(index=1, mode="PEAK")
        self.setMeasurement(index=5, mode="PEAK")
        self.setMeasurement(index=2, mode="FREQ")
        self.setMeasurement(index=6, mode="FREQ")
        self.setMeasurement(index=3, mode="MEAN")
        self.setMeasurement(index=7, mode="MEAN")
        self.SimpleMeasurementStatus = True

    def getSimpleMeasurements(self):
        '''
        Returns the 6 measurements of the two channels set.
        Measure | Indices
        Peak Amplitudes | 1, 5
        Frequency | 2, 6
        Mean | 3, 7
        
        
        Args: 
            None

        Return: List of measurements in the order [peak_ch1, peak_ch2, freq_ch1, freq_ch2, mean_ch1, mean_ch2].
        '''
        peak1 = self.getMeasurementResult(index=1)
        peak2 = self.getMeasurementResult(index=5)
        freq1 = self.getMeasurementResult(index=2)
        freq2 = self.getMeasurementResult(index=6)
        mean1 = self.getMeasurementResult(index=3)
        mean2 = self.getMeasurementResult(index=7)
        return [peak1[:-1], peak2[:-1], freq1[:-1], freq2[:-1], mean1[:-1], mean2[:-1]]

    def getMeasurements(self, measures=8):        
        '''
        Returns some number of measurement slots as a list regardless of the current settings.
        
        Args: 
            measures: Int which determines the number of measurements to return. In the range [1..8].

        Return: List of measurements.
        '''
        data = []
        for i in range(measures):
            data.append(self.getMeasurementResult(index=i + 1)[:-1])
        return data

    def getSimpleMean(self):
        '''
        Returns the average measurement of the 6 measures, over whatever number of recorded waveforms is set.
        
        Args: 
            None

        Return: List of measurements.
        '''
        peak1 = self.getMeasurementAvg(index=1)
        peak2 = self.getMeasurementAvg(index=5)
        freq1 = self.getMeasurementAvg(index=2)
        freq2 = self.getMeasurementAvg(index=6)
        mean1 = self.getMeasurementAvg(index=3)
        mean2 = self.getMeasurementAvg(index=7)
        return [peak1[:-1], peak2[:-1], freq1[:-1], freq2[:-1], mean1[:-1], mean2[:-1]]

    def getSimpleSTD(self):
        '''
        Returns the standard deviation of the 6 measurements over whatever number of recorded waveforms are available at that time. 
        
        Args: 
            None

        Return: List of measurement standard deviations.
        '''
        peak1 = self.getMeasurementStd(index=1)
        peak2 = self.getMeasurementStd(index=5)
        freq1 = self.getMeasurementStd(index=2)
        freq2 = self.getMeasurementStd(index=6)
        mean1 = self.getMeasurementStd(index=3)
        mean2 = self.getMeasurementStd(index=7)
        return [peak1[:-1], peak2[:-1], freq1[:-1], freq2[:-1], mean1[:-1], mean2[:-1]]

    def setSimpleScale(self):
        '''
        Ensures that both channel 1 and channel 2 are not clipping by referring to the corresponding amplitude peak measurements. 
        
        Args: 
            None

        Return: Int of 1 when complete.
        '''
        if not self.SimpleSetupStatus:
            print("simpleSetup is not set and simple scaling can't be done.")
            return 0
        amp_scale = self.wavevolt
        self.fixClipping(index=5, channel=2, scale=amp_scale / 2)
        self.fixClipping(index=1, channel=1, scale=0.01)
        return 1

    def fullResetStats(self):
        '''
        Erases all previous recorded measurements.
        
        Args: 
            None

        Return: None
        '''
        for i in range(8):
            ch = i + 1
            self.resetMeasurementStats(ch=ch)
