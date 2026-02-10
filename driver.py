import pvaccess
import pcaspy
import pvapy
import time


server = pvaccess.PvaServer()

class SimplePV(pcaspy.driver.SimplePV):
	def get_reason(self):
		return self.info.reason
	def create_array(self, t):
		return pvapy.PvObject({'value': [t], 'size': pvapy.UINT})
	def set_array(self, L):
		self.pv.set({'value': list(L), 'size': len(L)})
	def create_pv(self):
		t_num = self.info.type
		count = self.info.count
		_ait_d = pcaspy.driver._ait_d
		if t_num == _ait_d["str"]:
			self.pv = pvapy.PvString()
		elif t_num == _ait_d["float"]:
			if count > 1:
				self.pv = self.create_array(pvapy.FLOAT)
			else:
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
		self.create_pv()
	def updateValue(self, dbValue):
		super().updateValue(dbValue)
		value = dbValue.value
		if type(value)!=str and hasattr(value, "__len__"):
			self.set_array(value)
		else:
			self.pv.set(value)

pcaspy.driver.SimplePV = SimplePV

class Driver(pcaspy.driver.Driver):
	pass

class SimpleServer(pcaspy.driver.SimpleServer):
	pass
