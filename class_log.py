
class log:
	@classmethod
	def info(cls, message):
		print("[INFO] {}".format(message))
		
	@classmethod
	def debug(cls, message):
		print("[DEBUG] {}".format(message))
		
	@classmethod
	def error(cls, message):
		print("[ERROR] {}".format(message))
		
	