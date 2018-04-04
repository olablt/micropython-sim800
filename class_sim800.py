
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
