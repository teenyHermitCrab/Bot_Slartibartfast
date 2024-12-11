# import configparser  lol there is no configparser in circuitpython
import json
import os
# Adafruit imports below
import adafruit_scd4x
import board

'''
This wrapper intended to keep command constraints, settings from robot level. 
Extending the class would be less code, but then all those methods would be available to bot
I'll keep it this way for now, but revisit this in future tense and decide if you made the right choice


 TODO: could make another layer on top of this that is an interface for different sensors
       
       
       
       even better might be dynamically import wrapper modules (my own wrappers) so this could load up sensors
       without any rewrite?
            make this module an interface?
            
            check out importlib
            
    TODO:         
         
'''

class AirSensorSCD4x:
    # there are no Enums in CircuitPython.
    class MeasurementMode:
        IDLE = 0,  # Only SCD41 allows single-shot mode.  use for manual measurement cycles longer than 30 seconds
                   # or if you only need humidity/temperature at manual cycle rates up to 0.05 seconds
                   # For SCD40, this is used to reduce power consumption
        SLOW = 1,  # measurement approx every 30 seconds
        FAST = 2   # measurement approx every 5  seconds
                   
    class SensorModel:
        SCD40 = 1,
        SCD41 = 2,
        
    CONFIG_PATH = 'scd4x.ini'
    
    
    def __init__(self, sensor_model: SensorModel = SensorModel.SCD41, 
                       measurement_mode: MeasurementMode = MeasurementMode.SLOW, 
                       load_settings_file: bool = True):
        """Initialize SCD40 or SCD41 using default I2C address 0x62
                
        Args:
            sensor_model: SensorModel.SCD40 or SensorModel.SCD41.  Only SCD41 allow single-shot measurements
            measurement_mode: 
            load_settings_file: Set to True to utilize local settings file for altitude, temp-offset, and cal-enable.
                                This will override any on-board settings stored in chip EEPROM
                                False: On-board settings are used.
        """
        i2c = board.STEMMA_I2C()   # use built-in STEMMA QT connector
        # We can specify I2C address in this constructor, but there is not a way to change address from default 0x62
        # I.e., there are no address pins on Sensirion SCD4x, therefore only 1 of these devices on I2C bus
        self._scd4x = adafruit_scd4x.SCD4X(i2c)
        self._sensor_model = sensor_model
        # settings from on-chip are loaded automatically when sensor is powered up.
        self._scd4x.stop_periodic_measurement()
        if load_settings_file:
            self._load_settings_from_file()  
        self.measurement_mode = measurement_mode
        
        
    def _load_settings_from_file(self) -> None:
        """ Load settings from local file.  

        This will override settings loaded from on-board EEPROM. 
        Call .stop_periodic_measurement() prior
        
        """
        # TODO:  try/except here? that way the file doesnt need to exist
        #        or just test for file existence
        
        # config = configparser.ConfigParser()
        # config.read(CONFIG_PATH)
        # altitude = int(config['sensor_offsets']['altitude'])
        # temperature_offset = float(config['sensor_offset']['temperature_offset'])
        # self_calibration_enabled = bool(config['calibration']['self_calibration_enabled'])
        altitude = os.getenv("scd4x_altitude_offset")
        temperature_offset = os.getenv("scd4x_temperature_offset")
        self_calibration_enabled = os.getenv("scd4x_self_cal_enabled")
                
        self._scd4x.self_calibration_enabled = bool(self_calibration_enabled)
        self._scd4x.altitude = altitude
        self._scd4x.temperature_offset = temperature_offset
    
    
    def _start_measurement_mode(self) -> None:
        
        self._scd4x.stop_periodic_measurement()
        
        
        # CircuitPython does not currently support match/case syntax
        #match self._measurement_mode:
        #    case MeasurementMode.SLOW:
        #        self._scd4x.start_low_periodic_measurement()
        #    case MeasurementMode.FAST:
        #        self._scd4x.start_periodic_measurement()
        #    case MeasurementMode.IDLE:
        #        pass
        #    case _:
        #        raise ValueError(f'Invalid measurement mode: {measurement_mode}')
        
        if self.measurement_mode == AirSensorSCD4x.MeasurementMode.SLOW:
            self._scd4x.start_low_periodic_measurement()
        elif self.measurement_mode == AirSensorSCD4x.MeasurementMode.FAST:
            self._scd4x.start_periodic_measurement()
            
                
    @property
    def measurement_mode(self) -> MeasurementMode:
        return self._measurement_mode
        
    @measurement_mode.setter
    def measurement_mode(self, mode: MeasurementMode) -> None:
        self._measurement_mode = mode
        self._start_measurement_mode()
        

    @property
    def sensor_model(self):
        return self._sensor_model
        
    # no setter.  it doesn't make sense to change this after initialization.  Code creating this class instance
    #             should know which sensor it is initializing
    #             
    
         
    @property        
    def altitude(self) -> int:
        """Returns current altitude setting in meters

        Note: This command cannot be used during fast, slow measurement modes. Stops measurement mode, then returns sensor to measurement mode after altitude set
        """
        # NOTE : may need to be in IDLE mode to retrieve value
        self._scd4x.stop_periodic_measurement()  # SCD4X must be in idle mode to get value
        altitude = self._scd4x.altitude
        self._start_measurement_mode()  # resumes measurement mode
        return altitude
        
    @altitude.setter
    def altitude(self, height: int) -> None:
        """Set altitude in meters.  Setting this value adjusts CO2 measurement calculations to account for the air pressure's effect.

        Note: This command cannot be used during fast, slow measurement modes. Stops measurement mode, then returns sensor to measurement mode after altitude set

        NOTE: Setting an ambient pressure using set_ambient_pressure overrides any pressure compensation based
        on a previously set sensor altitude.
        """
        self._scd4x.stop_periodic_measurement()  # SCD4X must be in idle mode to set value
        self._scd4x.altitude = height
        self._start_measurement_mode()  # resumes measurement mode
            
            
    @property
    def temperature_offset(self) -> float:
        # NOTE : may need to be in IDLE mode to retrieve value, datasheet suggests this on page 8, but not on page 11
        self._scd4x.stop_periodic_measurement()
        offset = self._scd4x.temperature_offset
        self._start_measurement_mode()  # resumes measurement mode
        return offset
    
    @temperature_offset.setter
    def temperature_offset(self, offset: int | float) -> None:
        self._scd4x.stop_periodic_measurement()  # SCD4X must be in idle mode to set value
        self._scd4x.temperature_offset = offset
        self._start_measurement_mode()  # resumes measurement mode
        
        
    @property
    def auto_calibration(self) -> bool:
        # NOTE : may need to be in IDLE mode to retrieve value
        self._scd4x.stop_periodic_measurement()
        cal = self._scd4x.self_calibration_enabled
        self._start_measurement_mode()  # resumes measurement mode
        return cal
        
    @auto_calibration.setter
    def auto_calibration(self, enabled: bool) -> None:
        self._scd4x.stop_periodic_measurement()  # SCD4X must be in idle mode to set value
        self._scd4x.self_calibration_enabled = offset
        self._start_measurement_mode()  # resumes measurement mode
        
       
    ###### use these 3 methods when in a a periodic measurement mode
    @property
    def data_ready(self) -> bool:
        return self._scd4x.data_ready
        
    @property
    def CO2(self) -> int:
        return self._scd4x.CO2
        
    @property
    def temperature(self) -> float:
        return self._scd4x.temperature
        
    @property
    def relative_humidity(self) -> float:
        return self._scd4x.relative_humidity
        
    
        
    ########################################################################    
    # for single-shot mode (SCD41 only) may want to have this be wrapped up in a method that
    # triggers measurement and returns values
    
    def measure_single_shot_all(self) -> None:
        """On-demand measurement of CO2 concentration, relative humidity, and temperature for SCD41 only
        
           This does not return values, 
        """
        if self._measurement_mode != AirSensorSCD4x.MeasurementMode.IDLE:
            raise Exception(f'Must not be in periodic measurement modes when triggering single-shot measurement. Current mode {self._measurement_mode}')
        
        if self._sensor_model == AirSensorSCD4x.SensorModel.SCD41:
            self._scd4x.measure_single_shot_all()
        else: 
            # we are a SCD40, which does not have this capability
            # we could throw an exception, or allow Adafruit code to throw error (will it?)
            # 
            # but we could just fake a single-shot, by: 
            # * if data_ready, get that data and discard.
            # * startup periodic measurement mode
            # * then wait for next data.
            # * get that data,
            # * set mode back to IDLE
            
            raise Exception(f'This sensor model {self.sensor_model} does not have single-shot measurement capability')
            

    def measure_single_shot_rht_only(self) -> None:
        """On-demand measurement of relative humidity and temperature for SCD41 only   
        """
        if self._measurement_mode != AirSensorSCD4x.MeasurementMode.IDLE:
            raise Exception(f'Must not be in periodic measurement modes when triggering single-shot measurement. Current mode {self._measurement_mode}')
        
        
        if self._sensor_model == AirSensorSCD4x.SensorModel.SCD41:
            self._scd4x.measure_single_shot_rht_only()
        else: 
            # we are a SCD40, which does not have this capability
            # we could throw an exception, or allow Adafruit code to throw error (will it?)
            # 
            # but we could just fake a single-shot, by: 
            # * if data_ready, get that data and discard.
            # * startup periodic measurement mode
            # * then wait for next data.
            # * get that data,
            # * set mode back to IDLE
            
            raise Exception(f'This sensor model {self.sensor_model} does not have single-shot measurement capability')


    """
    def persist_settings(self, on_file: bool = True, on_chip: bool  = False) -> None:
        '''Saves temperature_offset, altitude, and self-calibration-enabled to local file and/or on-chip storage

        Args:
            save_to_file: Enable saving settings to local file.
            save_on_chip: Enable saving settings to actual sensor chip.  Use this sparingly.
                          The EEPROM chip for settings persist is only rated for 2000 writes.
        '''
        
        # Saving to file requires boot.py and a way to physically toggle ability to write to file.
        # normally CircuitPython will not allow code to write to file system.
        
        if on_file:
            self._scd4x.stop_periodic_measurement()
            config = configparser.ConfigParser()
            config.read(CONFIG_PATH)
            altitude = self._scd4x.altitude
            temp_offset = self._scd4x.termperature_offset
            cal_enable = self._scd4x.self._calibration_enabled
            
            config.set('sensor_offsets', 'altitude',           str(altitude))
            config.set('sensor_offsets', 'temperature_offset', str(temp_offset))
            config.set('calibration',    'cal_enable',         str(cal_enable))
            
            with open(CONFIG_PATH, 'w') as f:
                config.write(f)
            self._start_measurement_mode()
            
        if on_chip:
            self._scd4x.stop_periodic_measurement()
            self._scd4x.persist_settings()
            self._start_measurement_mode()
    """