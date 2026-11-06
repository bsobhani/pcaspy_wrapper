from pcaspy import *
#from .driver import Driver, SimpleServer, use_pvapy, use_p4p
from .driver import use_pvapy, use_p4p
#from .driver import Driver, use_pvapy, use_p4p
#from .driver import Driver, use_pvapy, use_p4p
#from .severity import Severity
#from pcaspy import Severity

class SimpleServerNoCA(SimpleServer):
    def pvAttach(self, context, fullname):
        return cas.S_casApp_pvNotFound
