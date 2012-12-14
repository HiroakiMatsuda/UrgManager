#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 \file UrgManager.py
 \brief This module communicates with the sensor according to the SCIP2
 \date $Date$


"""
import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# Import URG
import pyurg
import ConfigParser as Conf
import time

# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
urgmanager_spec = ["implementation_id", "UrgManager", 
		 "type_name",         "UrgManager", 
		 "description",       "This module communicates with the sensor according to the SCIP2", 
		 "version",           "1.0.0", 
		 "vendor",            "Matsuda Hiroaki", 
		 "category",          "SENSOR", 
		 "activity_type",     "STATIC", 
		 "max_instance",      "1", 
		 "language",          "Python", 
		 "lang_type",         "SCRIPT",
		 ""]
# </rtc-template>

class UrgManager(OpenRTM_aist.DataFlowComponentBase):
	
	"""
	\class UrgManager
	\brief This module communicates with the sensor according to the SCIP2
	
	"""
	def __init__(self, manager):
		"""
		\brief constructor
		\param manager Maneger Object
		"""
		OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

		self._d_command = RTC.TimedLongSeq(RTC.Time(0,0),[])
		"""
		"""
		self._commandIn = OpenRTM_aist.InPort("command", self._d_command)
		self._d_data = RTC.TimedLongSeq(RTC.Time(0,0),[])
		"""
		"""
		self._dataOut = OpenRTM_aist.OutPort("data", self._d_data)


		


		# initialize of configuration-data.
		# <rtc-template block="init_conf_param">
		
		# </rtc-template>


		 
	def onInitialize(self):
		"""
		
		The initialize action (on CREATED->ALIVE transition)
		formaer rtc_init_entry() 
		
		\return RTC::ReturnCode_t
		
		"""
		# Bind variables and configuration variable
		
		# Set InPort buffers
		self.addInPort("command",self._commandIn)
		
		# Set OutPort buffers
		self.addOutPort("data",self._dataOut)
		
		# Set service provider to Ports
		
		# Set service consumers to Ports
		
		# Set CORBA Service Ports

		print('onInitialize')
		
		return RTC.RTC_OK
		
	def onActivated(self, ec_id):
		"""
	
		The activated action (Active state entry action)
		former rtc_active_entry()
	
		\param ec_id target ExecutionContext Id
	
		\return RTC::ReturnCode_t
	
		"""
		# Read ini file
		self.conf = Conf.SafeConfigParser()
                self.conf.read('ini/urg.ini')
		
                self.port = self.conf.get('PORT', 'port')
                self.baudrate = int(self.conf.get('PORT', 'baudrate'))
                
		self.dist_flag = self.conf.get('DATA', 'dist') 
		self.intens_flag = self.conf.get('DATA', 'intens')
		#self.vewer = self.conf.get('DATA', 'viewer')
		self.command = self.conf.get('DATA', 'command')
        	self.amin = int(self.conf.get('DATA', 'amin'))
		self.amax = int(self.conf.get('DATA', 'amax'))
		self.num = int(self.conf.get('DATA', 'num'))

		# Open serial port
                self.urg = pyurg.Urg()
		self.urg.open_port(self.port, self.baudrate)

		# Request
		if self.intens_flag == 'OFF':
                        status = self.urg.request_md(self.amin, self.amax, num = self.num)

                else:
                        status = self.urg.request_me(self.amin, self.amax, num = self.num)

                self.urg.check_status(status)

                self.loop_count = 0
                self.command_flag = 0
                self.reset_flag = 0

		print('onActivated')
	
		return RTC.RTC_OK
	
	def onDeactivated(self, ec_id):
		"""
	
		The deactivated action (Active state exit action)
		former rtc_active_exit()
	
		\param ec_id target ExecutionContext Id
	
		\return RTC::ReturnCode_t
	
		"""
		self.urg.turn_off_laser()
		self.urg.close_port()
		print('onDeactivated')
	
		return RTC.RTC_OK
	
	def onExecute(self, ec_id):
		"""
	
		The execution action that is invoked periodically
		former rtc_active_do()
	
		\param ec_id target ExecutionContext Id
	
		\return RTC::ReturnCode_t
	
		"""
		if self.command == 'OFF':
                        if self.loop_count != num:
                                if self.intens_flag == 'OFF':
                                        dist, timestamp = self.urg.get_distance()
                                        self._d_data.data = [timestamp, 1, len(dist)] + dist
                                        OpenRTM_aist.setTimestamp(self._d_data)
                                        self._dataOut.write()

                                else:
                                        dist, intens, timestamp = self.urg.get_distance_and_intensity()
                                        self._d_data.data = [timestamp, 2, len(dist), len(intens)] + dist + intens
                                        OpenRTM_aist.setTimestamp(self._d_data)
                                        self._dataOut.write()

                                self.loop_count += 1
                        
		elif self.command == 'ON':
                        if self._commandIn.isNew():
                                self._d_command = self._commandIn.read()

                                if self.reset_flag == 1:
                                        if self.intens_flag == 'OFF':
                                                status = self.urg.request_md(self.amin, self.amax, num = self.num)

                                        else:
                                                status = self.urg.request_me(self.amin, self.amax, num = self.num)

                                        self.urg.check_status(status)

                                        self.reset_flag = 0
                                        

                                if self._d_command.data[0] == 0:
                                        time.sleep(0.5)

                                        self.urg.flush_outport()
                                        self.urg.flush_inport()

                                        time.sleep(0.5)

                                        self.command_flag = 0
                                        self.urg.turn_off_laser()

                                        time.sleep(0.5)
                                        
                                        self.urg.flush_inport()

                                        self.reset_flag = 1

                                elif self._d_command.data[0] == 1:
                                        self.command_flag = 1
                                        
                                        if self.intens_flag == 'OFF':
                                                dist, timestamp = self.urg.get_distance()
                                                self._d_data.data = [timestamp, 1, len(dist)] + dist
                                                OpenRTM_aist.setTimestamp(self._d_data)
                                                self._dataOut.write()

                                        else:
                                                dist, intens, timestamp = self.urg.get_distance_and_intensity()
                                                self._d_data.data = [timestamp, 2, len(dist), len(intens)] + dist + intens
                                                OpenRTM_aist.setTimestamp(self._d_data)
                                                self._dataOut.write()
                        else:
                                if self.command_flag == 1:
                                        if self.intens_flag == 'OFF':
                                                dist, timestamp = self.urg.get_distance()
                                                self._d_data.data = [timestamp, 1, len(dist)] + dist
                                                OpenRTM_aist.setTimestamp(self._d_data)
                                                self._dataOut.write()

                                        else:
                                                dist, intens, timestamp = self.urg.get_distance_and_intensity()
                                                self._d_data.data = [timestamp, 2, len(dist), len(intens)] + dist + intens
                                                OpenRTM_aist.setTimestamp(self._d_data)
                                                self._dataOut.write()

		return RTC.RTC_OK
	
def UrgManagerInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=urgmanager_spec)
    manager.registerFactory(profile,
                            UrgManager,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    UrgManagerInit(manager)

    # Create a component
    comp = manager.createComponent("UrgManager")

def main():
	mgr = OpenRTM_aist.Manager.init(sys.argv)
	mgr.setModuleInitProc(MyModuleInit)
	mgr.activateManager()
	mgr.runManager()

if __name__ == "__main__":
	main()

