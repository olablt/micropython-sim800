
from pyb import UART
import uasyncio as asyncio

import utime as time

class sim_uart():
	def __init__(self, uart_no = 2, timeout=4000):
		self.uart = UART(uart_no, 9600, timeout=timeout)
		self.loop = asyncio.get_event_loop()
		self.deadline = None
		self.result = ''
		
	async def writeline(self, command):
		self.uart.write("{}\r\n".format(command))
		print("<", command)
		
	async def write(self, command):
		self.uart.write("{}".format(command))
		print("<", command)
		
	
	
	def stop(self, in_advance=False):
		if not in_advance:
			print("no time left - deadline")
		else:
			print("stopped in advance - found expected string")
		self.deadline = None
		
	def running(self):
		return self.deadline is not None
	
	def postpone(self, duration = 1000):
		self.deadline = time.ticks_add(time.ticks_ms(), duration)
		
	def read(self, expect=None, duration=1000):
		self.result = ''
		self.postpone(duration)
		self.loop.create_task(self.read_killer(expect, duration))
	
	async def read_killer(self, expect=None, duration=1000):
		time_left = time.ticks_diff(self.deadline, time.ticks_ms())
		while time_left > 0:
			line = self.uart.readline()
			if line:
				line = convert_to_string(line)
				print(">", line)
				self.result += line
				if expect and line.find(expect)==0:
				# if expect and expect in line:
					self.stop(True)
					return True
				self.postpone(duration)
			time_left = time.ticks_diff(self.deadline, time.ticks_ms())
		self.stop()
		
		
	async def command(self, command, expect=None, duration=1000):
		await self.writeline(command)
		
		self.read(expect, duration)
		while self.running():
			await asyncio.sleep(0.2) # Pause 0.2s
			
		result = self.result
		return result


async def app_loop():
	
	print("sim = delay_uart.init...")
	sim = delay_uart()
	
	print("sim.command...")
	await sim.command("AT+CGMI")
	await sim.command("ATZ", "OK")
	# await sim.command("ATE0", "OK") # disable echo
	await sim.command('AT+CMEE=2', "OK") # enable error strings
	await sim.command("AT", "OK")
	await sim.command("AT+CBC", "+CBC")
	
	apn = "internet.tele2.lt"
	url = 'http://exploreembedded.com/wiki/images/1/15/Hello.txt'
	# res = await sim.command('AT+CREG?') # Check the Network Registration?
	
	res = await sim.command('AT+SAPBR=3,1,"Contype","GPRS"', 'OK') # connection type
	res = await sim.command('AT+SAPBR=3,1,"APN","{}"'.format(apn), 'OK') # GPRS APN
	
	res = await sim.command('AT+SAPBR=2,1') # Get current bearer
	# If bearer == 0,0,0,0 (not assigned) get a new bearer
	#  +SAPBR: 1,3,"0.0.0.0"
	
	res = await sim.command('AT+SAPBR=1,1', 'OK') # Open GPRS connection on profile 1
	res = await sim.command('AT+HTTPINIT', 'OK') # Init HTTP service
	res = await sim.command('AT+HTTPPARA="CID",1', 'OK') # Choose profile 1 as HTTP channel
	res = await sim.command('AT+HTTPPARA="URL","{}"'.format(url), 'OK')
	# res = await sim.command('AT+HTTPPARA="REDIR",1', 'OK')
	res = await sim.command('AT+HTTPACTION=0', '+HTTPACTION') # start GET session (may be long)
	res = await sim.command('AT+HTTPREAD') # Read the data of HTTP server
	res = await sim.command('AT+HTTPTERM', 'OK') # terminate HTTP task
	res = await sim.command('AT+SAPBR=0,1', 'OK') # close Bearer context
	
	print("done.")
	
	# while True:
	# 	# print( "battery: ", await get_battery() )
	# 	# print( "http: ", await get_http('http://exploreembedded.com/wiki/images/1/15/Hello.txt') )
	# 	await asyncio.sleep(5)


def run():
	print("loop.run_forever...")
	loop = asyncio.get_event_loop()
	loop.create_task(app_loop())
	loop.run_forever()






# async def get_battery():   
# 	result = await command('AT+CBC')
# 	if result:
# 		params=result[0].split(',')
# 		if not params[0] == '':
# 			params2 = params[0].split(':')
# 			if params2[0]=='+CBC':
# 				return int(params[1])
# 	return 0
	
# async def get_http(url, apn="internet.tele2.lt"): 








def convert_to_string(buf):
	try:
		tt =  buf.decode('utf-8').strip()
		return tt
	except UnicodeError:
		tmp = bytearray(buf)
		for i in range(len(tmp)):
			if tmp[i]>127:
				tmp[i] = ord('#')
		return bytes(tmp).decode('utf-8').strip()


