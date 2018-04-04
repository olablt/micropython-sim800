import uasyncio as asyncio
from class_sim800 import sim_uart
from class_log import log

async def app_loop():

	log.info("sim_uart.init...")
	sim = sim_uart()
	
	log.info("sim.command...")
	await sim.command("ATZ", "OK") # reset to default
	await sim.command('AT+CMEE=2', "OK") # enable error strings
	await sim.command("AT+CBC", "+CBC") # battery status
	
	apn = "internet.tele2.lt"
	url = 'http://exploreembedded.com/wiki/images/1/15/Hello.txt'
	
	await sim.command('AT+CREG?') # Check the Network Registration
	await sim.command('AT+SAPBR=3,1,"Contype","GPRS"', 'OK') # connection type
	await sim.command('AT+SAPBR=3,1,"APN","{}"'.format(apn), 'OK') # GPRS APN
	await sim.command('AT+SAPBR=2,1') # Get current bearer
	
	await sim.command('AT+SAPBR=1,1', 'OK') # Open GPRS connection on profile 1
	await sim.command('AT+HTTPINIT', 'OK') # Init HTTP service
	await sim.command('AT+HTTPPARA="CID",1', 'OK') # Choose profile 1 as HTTP channel
	await sim.command('AT+HTTPPARA="URL","{}"'.format(url), 'OK')
	# await sim.command('AT+HTTPSSL=1') # Enable HTTPS function
	# await sim.command('AT+HTTPPARA="REDIR",1', 'OK')
	await sim.command('AT+HTTPACTION=0', '+HTTPACTION') # start GET session (may be long)
	await sim.command('AT+HTTPREAD') # Read the data of HTTP server
	await sim.command('AT+HTTPTERM', 'OK') # terminate HTTP task
	await sim.command('AT+SAPBR=0,1', 'OK') # close Bearer context
	
	log.info("done.")


def run():
	loop = asyncio.get_event_loop()
	loop.create_task(app_loop())
	log.info("loop.run_forever...")
	loop.run_forever()

