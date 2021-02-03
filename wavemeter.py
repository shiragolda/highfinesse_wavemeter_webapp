
import os
#os.chdir("C:\\Users\\labuser\\gdrive\\code\\highfinesse_wavemeter")

if __name__=='__main__':
    os.chdir("/home/labuser/Insync/electric.atoms@gmail.com/Google Drive/code/highfinesse_wavemeter")

import zmq
import time
from zmq_publisher import zmqPublisher


"""

WLM API error codes for Get functions:

ErrNoValue = 0
ErrNoSignal = -1
ErrBadSignal = -2
ErrLowSignal = -3
ErrBigSignal = -4
ErrWlmMissing = -5
ErrNotAvailable = -6
InfNothingChanged = -7
ErrNoPulse = -8
ErrChannelNotAvailable = -10
ErrDiv0 = -13
ErrOutOfRange = -14
ErrUnitNotAvailable = -15
ErrMaxErr = ErrUnitNotAvailable


WLM API error codes for Set functions:

ResERR_NoErr = 0
ResERR_WlmMissing = -1
ResERR_CouldNotSet = -2
ResERR_ParmOutOfRange = -3
ResERR_WlmOutOfResources = -4
ResERR_WlmInternalError = -5
ResERR_NotAvailable = -6
ResERR_WlmBusy = -7
ResERR_NotInMeasurementMode = -8
ResERR_OnlyInMeasurementMode = -9
ResERR_ChannelNotAvailable = -10
ResERR_ChannelTemporarilyNotAvailable = -11
ResERR_CalOptionNotAvailable = -12
ResERR_CalWavelengthOutOfRange = -13
ResERR_BadCalibrationSignal = -14
ResERR_UnitNotAvailable = -15
ResERR_FileNotFound = -16
ResERR_FileCreation = -17
ResERR_TriggerPending = -18
ResERR_TriggerWaiting = -19
ResERR_NoLegitimation = -20

"""
class WM:
    
    
    def __init__(self,control_port=9000,publish=False,stream_port=5563,auto_adjust_on_startup=True):


        self.port = control_port #zmq port for handling wavemeter requests
        self.publish = publish
        self.auto_adjust_on_startup=auto_adjust_on_startup

        zmq_context = zmq.Context()
        self.socket = zmq_context.socket(zmq.REQ)
        self.socket.connect("tcp://192.168.0.110:%s"%self.port)
        
    
        if publish:
            self.publisher = zmqPublisher(port=stream_port,topic='wavemeter')

        if self.auto_adjust_on_startup:
            print("Auto-adjusting exposure times for optimal wavemeter performance")
            self.auto_adjust()
            print("Finished auto-adjusting")

    def ask(self,message):
        """ Send request to zmq server to pass message to wavemeter client """
        if isinstance(message,str): message = message.encode()
        self.socket.send(message)
        
        reply = self.socket.recv()
        return reply.decode()

       
    def read_frequency(self,channel):
        """
        Return frequency of channel in GHz

        """
        frequency = self.ask('GetFrequencyNum(%i,0.0)'%channel)
        return 1e3*float(frequency)

    def read_wavelength(self,channel):
        """
        Return the wavelength of channel in nm
        """
        wavelength = self.ask('GetWavelengthNum(%i,0.0)'%channel)
        return float(wavelength)

    def stream_some_frequencies(self,channels=[3,4,5,7,8]):
        """
        Display a constant stream of frequency readings for selected channels. 
        If publishing is on, publish values to zmq port. 
        """
        go = True
        while go:
            for i in channels:
                try:
                    new_data = self.read_frequency(i)
                    if self.publish:
                        self.publisher.publish_data((i,round(new_data,6)),prnt=True)
                    else:
                        print(new_data)
                    sleep_time = 0.6/len(channels)
                    time.sleep(sleep_time)

                except(KeyboardInterrupt):
                    go=False
                    break

                except Exception as e:
                    print(e)


    def read_temperature(self):
        """ Read wavemeter temperaure in C """
        temperature = self.ask('GetTemperature(0.0)')
        return float(temperature)

    def read_pressure(self):
        """ Read wavemeter pressure in mbar """
        pressure = self.ask('GetPressure(0.0)')
        return float(pressure)

    def auto_adjust(self):
        """ Auto adjust all wavemeter channel exposure times """
        for channel in range (1,9):
            self.auto_adjust_channel(channel)
        
    def auto_adjust_channel(self,channel):
        """ 
        Sets exposure mode to automatic to find the lowest exposure times that result in good interferograms. Then sets the exposure back to manual so that if the signal is lost the exposure time does not ramp up to 500 ms. 
        
        Exposure times are in ms
        """
        adjust=False
        power = self.read_laser_power(channel)
        
        if power>0:
            adjust=True
            
        else:
            self.set_exposure_mode(channel,auto=False)
            self.set_exposure(channel,1,arr=1)
            self.set_exposure(channel,1,arr=2)
            
            if power==-4000.0: #overexposed
                adjust=True
                print("Channel %i: High signal")

            else:
                print("Channel %i: Low signal, exposure set to %i and %i"%(channel,self.read_exposure(channel,1),self.read_exposure(channel,2)))
        
        if adjust:
            self.set_exposure_mode(channel,auto=True)
            time.sleep(5)
            self.set_exposure_mode(channel,auto=False)
            print("Channel %i: exposure adjusted to %i and %i"%(channel,self.read_exposure(channel,1),self.read_exposure(channel,2)))

    def read_exposure(self,channel,arr=1):
        """
        Return the exposure setting of a specified channel and array

        Inputs:
        channel: 1-7
        array: 1 or 2
        exposure on array 1 is used to obtain the wide/coarse interferogram
        exposure on array 2 is used to obtain the fine interferogram
        actual exposure on array 2 is the sum of the exposure settings for arrays 1 and 2

        """
        exposure = self.ask('GetExposureNum(%i,%i,False)'%(channel,arr))
        return float(exposure)


    # these exposure functions don't work properly - needs investigation

    def read_exposure_mode(self,channel):
        """ Read exposure mode: 1==Auto, 0==Manual """
        expomode = self.ask('GetExposureModeNum(%i,0)'%channel)
        return int(expomode)

    def set_exposure(self,channel,exp,arr=1):
        """
        Set the exposure of a certain channel and array

        Inputs:
        set_exposure(channel,array,exposure), where

        channel: 1-7
        exposure: an integer time in ms
        array: 1 or 2 (1: exposure on array 1; 2: exposure on all  other arrays; total exposure is the sum)
        """

        # Read exposure of CCD arrays
        self.ask('SetExposureNum(%i,1,%i)'%(channel,exp))
        time.sleep(0.5)
        return self.read_exposure(channel)

    def set_exposure_mode(self,channel,auto):
        """
        Set the exposure of a certain channel to auto

        auto = True means automatic control
        auto = False means manual control
        
        returns exposure mode of channel

        """
        if auto:
            self.ask('SetExposureModeNum(%i,True)'%(channel))
        else:
            self.ask('SetExposureModeNum(%i,False)'%(channel))

        return self.read_exposure_mode(channel)


    def read_precision(self):
        """ Read Precision (Wide/Fine)
        0 == Fine
        1 == Wide
        """
        precision = self.ask('GetWideMode(0)')
        return int(precision)
        
        
    def read_laser_power(self,channel):
        """ Returns laser power of channel in uW """
        power = self.ask('GetPowerNum(%i,0)'%channel)
        return float(power)
        


    @property
    def wavelengths(self):
        return [self.read_wavelength(i+1) for i in range(8)]
        
    @property
    def frequencies(self):
        return [self.read_frequency(i+1) for i in range(8)]
        
    @property
    def powers(self):
        return [self.read_laser_power(i+1) for i in range(8)]
##
if __name__=='__main__':
    wm = WM(publish=True)

