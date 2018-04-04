from pyb import Pin, LED, ADC
class pcb:
	@classmethod
	def init(cls):
		cls._gps = Pin('X5', mode=Pin.OUT_PP, pull=Pin.PULL_DOWN)
		cls._gsm = Pin('X6', mode=Pin.OUT_PP, pull=Pin.PULL_DOWN)
		cls._gps.value(True)
		cls._gsm.value(True)
		
		cls._red = LED(1)
		cls._blue = LED(4)
		
		cls._batt = ADC('X7') # create an analog object from a pin
		
	@classmethod
	def red_on(cls):
		cls._red.on()
		
	@classmethod
	def red_off(cls):
		cls._red.off()
	
	
	@classmethod
	def get_voltage(cls):
		v = 4.13 / 2592 * cls._batt.read() # read an analog value
		return v