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
	from p4p.nt import NTScalar, NTEnum
except:
	None



server = None
_ait_d = pcaspy.driver._ait_d

class SimplePVBase(pcaspy.driver.SimplePV):
	def get_reason(self):
		return self.info.reason
	def create_pv(self):
		t_num = self.info.type
		count = self.info.count
		if t_num == _ait_d["str"]:
			self.pv = self.create_pv_str()
		elif t_num == _ait_d["float"]:
			if count > 1:
				self.pv = self.create_pv_float_array()
			else:
				self.pv = self.create_nt_float()
		elif t_num == _ait_d["char"]:
			if count > 1:
				self.pv = self.create_pv_char_array()
			else:
				self.pv = create_nt_int()
		elif t_num == _ait_d["int"]:
			self.pv = self.create_nt_int()
		elif t_num == _ait_d["short"]:
			self.pv = self.create_nt_int()
		elif t_num == _ait_d["enum"]:
			self.pv = self.create_nt_enum()
			#self.pv = self.create_pv_enum()
			#self.pv = self.create_nt_int()
		
		#server.addRecord(self.name, self.pv, cb)
		#self.add_record(cb)
		self.add_record()
	
	def __init__(self, name, info):
		super().__init__(name, info)
		self.create_pv()
	def updateValue(self, dbValue):
		super().updateValue(dbValue)
		value = dbValue.value
		#if type(value)!=str and hasattr(value, "__len__"):
		#if self.info.type!=_ait_d["str"] and hasattr(value, "__len__"):
		if self.info.type==_ait_d["str"]:
			#self.pv.set(value)
			self.set_pv(value)
		elif hasattr(value, "__len__"):
			self.set_array(value)
		elif 1==1 and self.info.type == _ait_d["enum"]:
			print("setting choices to ", self.info.enums)
			#pvenum = self.create_pv_enum()
			#pvenum.setChoices(self.info.enums)
			#pvenum.setIndex(value)
			#self.pv.set(pvenum)
			self.set_pv_enum(self.info.enums, value)
			print("AAA",type(self.pv))
			#self.pv.setValue(pvenum)
		else:
			#self.pv.set(value)
			#self.pv.set({"value":value})
			#print(dbValue.severity)
			self.set_pv({"value":value, "alarm.severity": dbValue.severity, "alarm.status": dbValue.alarm})
			#self.pv.setAlarm(pvapy.Alarm(1,1,"asdf"))
			#self.pv["alarm.severity"] = dbValue.severity
			#self.pv["alarm.status"] = dbValue.alarm

class SimplePVPVAPY(SimplePVBase):
	def set_array(self, L):
		self.pv.set({'value': list(L), 'size': len(L)})
	def create_nt_float(self):
		return pvapy.NtScalar(pvapy.FLOAT)
	def create_pv_str(self):
		return pvapy.PvString()
	def create_nt_int(self):
		return pvapy.NtScalar(pvapy.INT)
	def create_pv_array(self, t):
		return pvapy.PvObject({'value': [t], 'size': pvapy.UINT})
	def create_pv_char_array(self):
		return self.create_pv_array(pvapy.BYTE)
	def create_pv_float_array(self):
		return self.create_pv_array(pvapy.FLOAT)
	def create_nt_enum(self):
		return pvapy.NtEnum()
	def create_pv_enum(self):
		return pvapy.PvEnum()
	def add_record(self):
		def cb(pv):
			driver = pcaspy.driver.manager.driver.get(self.info.port)
			driver.write(self.get_reason(), pv["value"])
		server.addRecord(self.name, self.pv, cb)
	def set_pv(self, value):
		#self.pv.set({"value":value})
		self.pv.set(value)
	def set_pv_enum(self, choices, value):
		pvenum = self.create_pv_enum()
		pvenum.setChoices(self.info.enums)
		pvenum.setIndex(value)
		self.pv.setValue(pvenum)


class SimplePVP4P(SimplePVBase):
	def set_array(self, value):
		if type(value)==str:
			value = [ord(e) for e in value]
		self.set_pv(value)
	def create_nt_float(self):
		#return NTScalar('f')
		return NTScalar('d')
	def create_pv_str(self):
		return NTScalar('s')
	def create_nt_int(self):
		return NTScalar('i')
	def create_pv_char_array(self):
		return NTScalar('aB')
	def create_pv_float_array(self):
		#return NTScalar('af')
		return NTScalar('ad')
	def create_nt_enum(self):
		#return NTScalar('i')
		return NTEnum()
	def create_pv_enum(self):
		return NTScalar('i')
	def add_record(self):
		if self.info.type == _ait_d["str"]:
			initial = self.pv.wrap("")
		elif self.info.count > 1:
			initial = self.pv.wrap([])
		else:
			initial = self.pv.wrap(0)
		def on_put(pv, op):
			value = op.value()['value']
			driver = pcaspy.driver.manager.driver.get(self.info.port)
			driver.write(self.get_reason(), value)
			pv.post(op.value())
			op.done()
		self.shared_pv = SharedPV(initial=initial)
		self.shared_pv._handler.put = on_put
		provider.add(self.name, self.shared_pv)
	def set_pv(self, value):
		wrapped_value = self.pv.wrap(value)
		self.shared_pv.post(wrapped_value)
	def set_pv_enum(self, choices, value):
		wrapped_value = self.pv.wrap({"choices": choices, "index": value})
		self.shared_pv.post(wrapped_value)



		



"""
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
			if count > 1:
				return NTScalar('ai')
			return NTScalar('i')
		elif t_num == _ait_d["short"]:
			if count > 1:
				return NTScalar('ai')
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

"""

#pcaspy.driver.SimplePV = SimplePV
#pcaspy.driver.SimplePV = SimplePVP4P

def use_pvapy():
	global server
	server = pvaccess.PvaServer()
	pcaspy.driver.SimplePV = SimplePVPVAPY
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
