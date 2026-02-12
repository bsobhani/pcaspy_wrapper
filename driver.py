import pcaspy
import time
try:
	import pvaccess
	import pvapy
except:
	None
try:
	from p4p.server import StaticProvider
	from p4p.server import Server as ServerP4P
	from p4p.server.thread import SharedPV
	from p4p.nt import NTScalar
except:
	None



server = None
_ait_d = pcaspy.driver._ait_d

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
		if t_num == _ait_d["str"]:
			self.pv = pvapy.PvString()
		elif t_num == _ait_d["float"]:
			if count > 1:
				self.pv = self.create_array(pvapy.FLOAT)
			else:
				self.pv = pvapy.PvFloat()
		elif t_num == _ait_d["char"]:
			if count > 1:
				self.pv = self.create_array(pvapy.BYTE)
			else:
				#self.pv = pvapy.PvString()
				self.pv = pvapy.PvInt()
		elif t_num == _ait_d["int"]:
			self.pv = pvapy.PvInt()
		elif t_num == _ait_d["short"]:
			self.pv = pvapy.PvInt()
		elif t_num == _ait_d["enum"]:
			#self.pv = pvapy.PvInt()
			self.pv = pvapy.PvEnum()
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
		#if type(value)!=str and hasattr(value, "__len__"):
		if self.info.type!=_ait_d["str"] and hasattr(value, "__len__"):
			self.set_array(value)
		elif self.info.type == _ait_d["enum"]:
			print("setting choices to ", self.info.enums)
			self.pv.setChoices(self.info.enums)
			self.pv.setIndex(value)
		else:
			self.pv.set(value)


class SimplePVP4P(pcaspy.driver.SimplePV):

	def get_reason(self):
		return self.info.reason

	def _make_nt(self):
		t_num = self.info.type
		count = self.info.count
		_ait_d = pcaspy.driver._ait_d

		# Scalars
		if t_num == _ait_d["str"]:
			return NTScalar('s')
		elif t_num == _ait_d["float"]:
			if count > 1:
				#return NTScalarArray('f')
				return NTScalar('af')
			return NTScalar('f')
		elif t_num == _ait_d["char"]:
			#return NTScalar('s')
			return NTScalar('aB')
		elif t_num == _ait_d["int"]:
			return NTScalar('i')
		elif t_num == _ait_d["short"]:
			return NTScalar('i')
		elif t_num == _ait_d["enum"]:
			return NTScalar('i')

		raise ValueError("Unsupported type")

	def create_pv(self):
		_ait_d = pcaspy.driver._ait_d
		nt = self._make_nt()
		self.nt = nt
		print(self.info.name, self.info.type, self.info.count, _ait_d)
		if self.info.type == _ait_d["str"]:
			initial = self.nt.wrap("")
		elif self.info.count > 1:
			initial = self.nt.wrap([])
		else:
			initial = self.nt.wrap(0)
			


		def on_put(pv, op):
			value = op.value()['value']
			driver = pcaspy.driver.manager.driver.get(self.info.port)
			driver.write(self.get_reason(), value)
			pv.post(op.value())
			op.done()

		#initial = nt.wrap(0)
		#self.pv = SharedPV(initial=initial, onPut=on_put)
		self.pv = SharedPV(initial=initial)
		#self.pv = SharedPV()
		self.pv._handler.put = on_put
		provider.add(self.name, self.pv)

	def __init__(self, name, info):
		super().__init__(name, info)
		self.create_pv()

	def updateValue(self, dbValue):
		super().updateValue(dbValue)
		value = dbValue.value

		#if type(value) != str and hasattr(value, "__len__"):
		if self.info.type!=_ait_d["str"] and hasattr(value, "__len__"):
			#self.pv.post(self.nt.wrap({'value': list(value)}))
			if type(value)==str:
				value = [ord(e) for e in value]
			wrapped_value = self.nt.wrap(list(value))
			self.pv.post(wrapped_value)
		else:
			wrapped_value = self.nt.wrap(value)
			self.pv.post(wrapped_value)

#pcaspy.driver.SimplePV = SimplePV
#pcaspy.driver.SimplePV = SimplePVP4P

def use_pvapy():
	global server
	server = pvaccess.PvaServer()
	pcaspy.driver.SimplePV = SimplePV
	print("using pvapy")

provider = None
def use_p4p():
	global server
	global provider
	provider = StaticProvider('simple')
	server = ServerP4P(providers=[provider])
	pcaspy.driver.SimplePV = SimplePVP4P
	print("using p4p")

try:
	use_p4p()
except:
	print("p4p not found, trying pvapy")
	use_pvapy()

class Driver(pcaspy.driver.Driver):
	pass

class SimpleServer(pcaspy.driver.SimpleServer):
	pass
