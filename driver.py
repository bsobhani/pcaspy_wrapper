import pvaccess
import pcaspy
import pvapy
import time


server = pvaccess.PvaServer()

class SimplePV(pcaspy.driver.SimplePV):
	def get_reason(self):
		return self.info.reason
	def create_pv(self):
		t_num = self.info.type
		_ait_d = pcaspy.driver._ait_d
		if t_num == _ait_d["str"]:
			self.pv = pvapy.PvString()
		elif t_num == _ait_d["float"]:
			self.pv = pvapy.PvFloat()
		elif t_num == _ait_d["char"]:
			#self.pv = pvapy.PvScalarArray(pvapy.INT)
			self.pv = pvapy.PvString()
		elif t_num == _ait_d["int"]:
			self.pv = pvapy.PvInt()
		elif t_num == _ait_d["short"]:
			self.pv = pvapy.PvInt()
		elif t_num == _ait_d["enum"]:
			self.pv = pvapy.PvInt()
		def cb(pv):
			driver = pcaspy.driver.manager.driver.get(self.info.port)
			driver.write(self.get_reason(), pv["value"])
		server.addRecord(self.name, self.pv, cb)
	
	def __init__(self, name, info):
		super().__init__(name, info)
		self.name = name
		self.info = info
		self.create_pv()
	def scan(self):
		print("SCANNING")
		pass
	def updateValue(self, dbValue):
		print("dbvalue", dbValue)

pcaspy.driver.SimplePV = SimplePV

#from pcaspy import Driver
class Driver(pcaspy.driver.Driver):
	def setParam(self, reason, value, timestamp=None):
		super().setParam(reason, value, timestamp)
		value = self.pvDB[reason].value
		pvs = pcaspy.driver.manager.pvs[self.port]
		pvs[reason].pv.set(value)

class SimpleServer(pcaspy.driver.SimpleServer):
	def process(self, val):
		time.sleep(val)
		pass
