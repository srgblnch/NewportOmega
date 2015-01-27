#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        NewportInfinityMeter.py
## 
## Project :     NewportInfinityMeter
##
## $Author :      sblanch$
##
## $Revision :    $
##
## $Date :        $
##
## $HeadUrl :     $
##============================================================================
##            This file is generated by POGO
##    (Program Obviously used to Generate tango Object)
##
##        (c) - Software Engineering Group - ESRF
##############################################################################

"""Device server to show the INFinity meter Strain gage from Newport, in a tango system."""

__all__ = ["NewportInfinityMeter", "NewportInfinityMeterClass", "main"]

__docformat__ = 'restructuredtext'

import PyTango
import sys
# Add additional import
#----- PROTECTED REGION ID(NewportInfinityMeter.additionnal_import) ENABLED START -----#
from types import StringType #used for Exec()
import pprint #used for Exec()
from infs import InfinityMeter
import time
import functools
import traceback
from taurus import Logger

def AttrExc(function):
    '''Decorates commands so that the exception is logged and also raised.
    '''
    #TODO: who has self._trace?
    def nestedMethod(self, attr, *args, **kwargs):
        inst = self #< for pychecker
        try:
            return function(inst, attr, *args, **kwargs)
        except Exception, exc:
            traceback.print_exc(exc)
            #self._trace = traceback.format_exc(exc)
            raise
    functools.update_wrapper(nestedMethod,function)
    return nestedMethod

def latin1(x):
  return x.decode('utf-8').replace(u'\u2070', u'\u00b0').\
      replace(u'\u03bc',u'\u00b5').encode('latin1')

CHANGING_THRESHOLD_DEFAULT = 0.01
CHANGING_THRESHOLD_NAME = "ChangingThreshold"
CHANGING_THRESHOLD_LABEL = "Quality changing threshold"

#----- PROTECTED REGION END -----#	//	NewportInfinityMeter.additionnal_import

##############################################################################
## Device States Description
##
## INIT : Starting the device agent.
## ON : Well made connetion to the instrument.
## OFF : Not build connection to the instrument.
## ALARM : Something is not working properly.
## FAULT : There is something that cannot be recovered.
##############################################################################

class NewportInfinityMeter (PyTango.Device_4Impl):

#--------- Add you global variables here --------------------------
#----- PROTECTED REGION ID(NewportInfinityMeter.global_variables) ENABLED START -----#
    #####
    #---- #state segment
    def change_state(self,newstate,cleanImportantLogs=False):
        '''This method is like an overload of the set_state, but includes
           a push event of this attribute.
        '''
        self.debug_stream("In change_state(%s)"%(str(newstate)))
        if newstate != self.get_state():
            self.set_state(newstate)
            self.push_change_event('State',newstate)
            if cleanImportantLogs:
                self.cleanAllImportantLogs()
    def addStatusMsg(self,text=None,important=False):
        '''The tango Status shall be a human readable message of the behaviour 
           of the device. With this method, text messages can be set in the 
           status attribute, with the extra feature to allow the device to
           remember (and maintain in the status message) some part messages,
           in order to merge them in one output.
        '''
        self.debug_stream("In %s::addStatusMsg()"%self.get_name())
        if text == None or len(text) == 0:
            status = "The device is in %s state.\n"%(self.get_state())
        else:
            if not text in self._important_logs:
                status = "%s\n"%(text)
            else:
                status = ""
        if not hasattr(self,'_infs') or self._infs == None:
            status = "%sThere is not connection to the instrument!\n"%(status)
        elif self._infs.usesTango():
            try:
                status = "%sThe PySerial is in %s state.\n"\
                %(status,self._infs._proxy.State())
            except Exception,e:
                status = "%sThe PySerial is not available...\n"%(status)
                self.error_stream("Error getting information about the "\
                                  "state of the underlever device proxy: "\
                                  "%s"%(e))
        for ilog in self._important_logs:
            status = "%s%s\n"%(status,ilog)
        self.set_status(status)
        self.push_change_event('Status',status)
        if important and not text in self._important_logs:
            self._important_logs.append(text)
    def cleanAllImportantLogs(self):
        '''With the feature of remember past messages to the status text 
           collection, it shall be also a way to clean up them.
        '''
        self.debug_stream("In %s::cleanAllImportantLogs()"%self.get_name())
        self._important_logs = []
        self.addStatusMsg("")
        
    def statusCallback(self,msgType,msgText):
        '''Used from the instance of the instrument to report a communication 
           issue with the instrument.
           Message types are from Logger:
           - Error: fault state, clean important logs and place the new one,
           - Warning: alarm state and important log in the status,
           - Info: add as non important the text in the status.
        '''
        if msgType == Logger.Error:
            self.change_state(PyTango.DevState.FAULT,cleanImportantLogs=True)
            important = True
        elif msgType == Logger.Warning:
            self.change_state(PyTango.DevState.ALARM)
            important = True
        else:
            important = False
        self.addStatusMsg(msgText,important)
    #---- done state segment
    
    #####
    #---- #dynattrs segment
    def addDynAttribute(self,attrName):
        '''Based on the elements listed in the property Measures, each of them
           will pass throw this method to build dynamic tango attributes for
           this device and configure them in the same way with events.
        '''
        try:
            #Prepare a previous value record
            self._measuredValues[attrName] = None
            #Prepare the tango attribute
            attr = PyTango.Attr(attrName,PyTango.DevDouble,PyTango.READ)
            readmethod = AttrExc(getattr(self,'read_attr'))
            aprop = PyTango.UserDefaultAttrProp()
            aprop.set_format("%6.3f")
            attr.set_default_properties(aprop)
            #Insert this new attribute to the current device
            self.add_attribute(attr,r_meth=readmethod)
            #Stablish events for this attribute
            self.set_change_event(attrName,True,False)
            #subscribe it to have periodic readings and event emission.
            self._infs.subscribe(attrName,self.InfsCallback)
            self.info_stream("Added Dynamic attribute %s"%(attrName))
        except Exception,e:
            self.error_stream("The dynamic attribute %s cannot be created "\
                              "due to: %s"%(attrName,e))
    
    def addExpertDynAttributes(self):
        '''The dynamic attributes that would be created may have different 
           unitsor value stability. Due to that, two expert attributes will 
           cometo allow the definition of the string to be set as unit and 
           the threshold of difference to set quality changing.
        '''
        try:
            threshold = self.addExpertAttribute(CHANGING_THRESHOLD_NAME,
                                                PyTango.DevDouble,
                                                CHANGING_THRESHOLD_LABEL)
            self._expertAttrs[CHANGING_THRESHOLD_NAME] = None
            self.info_stream("Added Dynamic expert attribute %s"
                             %(CHANGING_THRESHOLD_NAME))
        except Exception,e:
            self.error_stream("The expert dynamic attributes cannot be "\
                              "created due to: %s"%(e))
    def addExpertAttribute(self,name,type,label=None):
        '''builder of expert memorized attributes.
        '''
        attr = PyTango.Attr(name,type, PyTango.READ_WRITE)
        attr.set_memorized()
        attr.set_disp_level(PyTango.DispLevel.EXPERT)
        readmethod = AttrExc(getattr(self,'read_expert_attr'))
        writemethod = AttrExc(getattr(self,'write_expert_attr'))
        aprop = PyTango.UserDefaultAttrProp()
        if type == PyTango.DevDouble:
            aprop.set_format("%6.3f")
        if label != None:
            aprop.set_label(latin1(label))
        attr.set_default_properties(aprop)
        self.add_attribute(attr,r_meth=readmethod,w_meth=writemethod)
        return attr
    
    def fireEvent(self,attrName,value,quality=PyTango.AttrQuality.ATTR_VALID):
        '''Like overload the push_change_event to have logging of it.
        '''
        timestamp = time.time()
        self.debug_stream("fireEvent for %s: %g (%s)"%(attrName,value,quality))
        self.push_change_event(attrName,value,timestamp,quality)
    
    def InfsCallback(self,attrName,newValue):
        '''This method is used as a callback for the instance this device has
           of the object that manages the communications with the instrument.
        '''
        oldValue = self._measuredValues[attrName]
        quality = self.getAttrQuality(attrName,oldValue,newValue)
        self.fireEvent(attrName,newValue,quality)
    
    def getAttrQuality(self,attrName,oldValue,newValue):
        '''Given two values (old and new) this method will decide the quality
           that the attribute shall have to send with the new value.
        '''
        if hasattr(self,"_expertAttrs") and \
                       self._expertAttrs.has_key(CHANGING_THRESHOLD_NAME) and \
                            self._expertAttrs[CHANGING_THRESHOLD_NAME] != None:
            threshold = self._expertAttrs[CHANGING_THRESHOLD_NAME]
        else:
            threshold = CHANGING_THRESHOLD_DEFAULT
        if oldValue != None and abs(oldValue-newValue) > threshold:
            quality = PyTango.AttrQuality.ATTR_CHANGING
        else:
            quality = PyTango.AttrQuality.ATTR_VALID
        return quality
    
    @AttrExc
    def read_attr(self, attr):
        '''Generic method for dynamic attributes to read each of them. Based on
           the attribute name, information is requested to the object that
           manages the communications to the instrument.
        '''
        attrName = attr.get_name()
        if not self.get_state() in [PyTango.DevState.ON,
                                    PyTango.DevState.ALARM]:
            attr.set_value_date_quality(float('inf'),time.time(),
                                    PyTango.AttrQuality.ATTR_INVALID)
            return
        self.debug_stream("read_%s_attr()"%(attrName))
        try:
            #TODO: introduce periodic readings (to emit events) and set value here 
            #from the cached value.
            #TODO: last todo may have problems if the period is too long. If the 
            #requesting is not stressed it may introduce a new real reading and 
            #push event.
            oldValue = self._measuredValues[attrName]
            newValue = self._infs.getValue(attrName)
            quality = self.getAttrQuality(attrName,oldValue,newValue)
            value = self._measuredValues[attrName] = newValue
            attr.set_value_date_quality(value,time.time(),quality)
        except ValueError,e:
            self.change_state(PyTango.DevState.ALARM)
            self.addStatusMsg("%s: %s"%(attrName,e),important=True)
            self.warn_stream("On %s read, ValueError exception: %s"
                             %(attrName,e))
        except Exception,e:
#            self.change_state(PyTango.DevState.FAULT)
#            self.addStatusMsg("Critical error accessing the instrument!")
            self.error_stream("On %s read, exception: %s"%(attrName,e))
    
    @AttrExc
    def read_expert_attr(self,attr):
        '''Generic Get method for the expert attributes.
        '''
        attrName = attr.get_name()
        if not self._expertAttrs.has_key(attrName):
            if attr.get_type() == PyTango.DevDouble:
                value = float('inf')
            elif attr.get_type() == PyTango.DevString:
                value = ""
            else:
                value = None
            quality = PyTango.AttrQuality.ATTR_INVALID
        else:
            value = self._expertAttrs[attrName]
            quality = PyTango.AttrQuality.ATTR_VALID
        attr.set_value_date_quality(value,time.time(),quality)
    
    @AttrExc
    def write_expert_attr(self,attr):
        '''Generic Set method for the expert attributes.
        '''
        attrName = attr.get_name()
        if not self._expertAttrs.has_key(attrName):
            self._expertAttrs[attrName] = None
        data=[]
        attr.get_write_value(data)
        self._expertAttrs[attrName] = data[0]
    #---- done dynattrs segment
            
#----- PROTECTED REGION END -----#	//	NewportInfinityMeter.global_variables
#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        self.debug_stream("In " + self.get_name() + ".__init__()")
        NewportInfinityMeter.init_device(self)

#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    def delete_device(self):
        self.debug_stream("In " + self.get_name() + ".delete_device()")
        #----- PROTECTED REGION ID(NewportInfinityMeter.delete_device) ENABLED START -----#
        if self.get_state() == PyTango.DevState.ON:
            self.Close()
            #del self._infs
            self._infs = None
        #----- PROTECTED REGION END -----#	//	NewportInfinityMeter.delete_device

#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------
    def init_device(self):
        self.debug_stream("In " + self.get_name() + ".init_device()")
        self.get_device_properties(self.get_device_class())
        #----- PROTECTED REGION ID(NewportInfinityMeter.init_device) ENABLED START -----#
        self._infs = None
        self._important_logs = []
        try:
            self.set_change_event('State',True,False)
            self.set_change_event('Status',True,False)
            self.change_state(PyTango.DevState.INIT)
            self.addStatusMsg("Initialising the device...")
            # for the Exec command
            self._locals = { 'self' : self }
            self._globals = globals()
            
            self.change_state(PyTango.DevState.OFF)
            self.addStatusMsg("Ready to connect to the instrument.")
            # prepare the requestor object
            self.debug_stream("Channel for serial line communications: %s"
                              %(self.Serial))
            self.debug_stream("Instrument addres in the serial line: %s"
                              %(self.Address))
            self._infs = None
            self._infs = InfinityMeter(self.Serial,self.Address,
                                       logLevel=Logger.Debug)
            self.Open()
            # prepare the dynamic attributes for the requested measures
            self.debug_stream("Preparing the measures: %s"%(self.Measures))
            self._measuredValues = {}
            for measure in self.Measures:
                self.addDynAttribute(measure)
            self._expertAttrs = {}
            self.addExpertDynAttributes()
        except Exception,e:
            msg = "Device cannot be initialised!"
            self.error_stream(msg)
            self.change_state(PyTango.DevState.FAULT)
            self.addStatusMsg(msg+" Check the traces.")
            traceback.print_exc()
            
        #----- PROTECTED REGION END -----#	//	NewportInfinityMeter.init_device

#------------------------------------------------------------------
#    Always excuted hook method
#------------------------------------------------------------------
    def always_executed_hook(self):
        self.debug_stream("In " + self.get_name() + ".always_excuted_hook()")
        #----- PROTECTED REGION ID(NewportInfinityMeter.always_executed_hook) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	NewportInfinityMeter.always_executed_hook

#==================================================================
#
#    NewportInfinityMeter read/write attribute methods
#
#==================================================================




#------------------------------------------------------------------
#    Read Attribute Hardware
#------------------------------------------------------------------
    def read_attr_hardware(self, data):
        self.debug_stream("In " + self.get_name() + ".read_attr_hardware()")
        #----- PROTECTED REGION ID(NewportInfinityMeter.read_attr_hardware) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	NewportInfinityMeter.read_attr_hardware


#==================================================================
#
#    NewportInfinityMeter command methods
#
#==================================================================

#------------------------------------------------------------------
#    Exec command:
#------------------------------------------------------------------
    def Exec(self, argin):
        """ Expert attribute to execute python code inside the device. Use it extremelly carefully.
        
        :param argin: 
        :type: PyTango.DevString
        :return: 
        :rtype: PyTango.DevString """
        self.debug_stream("In " + self.get_name() +  ".Exec()")
        argout = ''
        #----- PROTECTED REGION ID(NewportInfinityMeter.Exec) ENABLED START -----#
        cmd = argin
        L = self._locals
        G = self._globals
        try:
            try:
                # interpretation as expression
                result = eval(cmd, G, L)
            except SyntaxError:
                # interpretation as statement
                exec cmd in G, L
                result = L.get("y")

        except Exception, exc:
            # handles errors on both eval and exec level
            result = exc

        if type(result)==StringType:
            return result
        elif isinstance(result, BaseException):
            return "%s!\n%s" % (result.__class__.__name__, str(result))
        else:
            return pprint.pformat(result)
        #----- PROTECTED REGION END -----#	//	NewportInfinityMeter.Exec
        return argout
        
#------------------------------------------------------------------
#    Open command:
#------------------------------------------------------------------
    def Open(self):
        """ Open the communications with the lower level serial line.
        
        :param : 
        :type: PyTango.DevVoid
        :return: 
        :rtype: PyTango.DevVoid """
        self.debug_stream("In " + self.get_name() +  ".Open()")
        #----- PROTECTED REGION ID(NewportInfinityMeter.Open) ENABLED START -----#
        self._infs.open()
        self.change_state(PyTango.DevState.ON)
        self.addStatusMsg("Connected to the instrument.")
        #----- PROTECTED REGION END -----#	//	NewportInfinityMeter.Open
        
#------------------------------------------------------------------
#    Is Open command allowed
#------------------------------------------------------------------
    def is_Open_allowed(self):
        self.debug_stream("In " + self.get_name() + ".is_Open_allowed()")
        return not(self.get_state() in [PyTango.DevState.INIT,
            PyTango.DevState.ON,
            PyTango.DevState.FAULT])
#------------------------------------------------------------------
#    Close command:
#------------------------------------------------------------------
    def Close(self):
        """ Close the communications with the lower level serial line.
        
        :param : 
        :type: PyTango.DevVoid
        :return: 
        :rtype: PyTango.DevVoid """
        self.debug_stream("In " + self.get_name() +  ".Close()")
        #----- PROTECTED REGION ID(NewportInfinityMeter.Close) ENABLED START -----#
        self._infs.close()
        self.change_state(PyTango.DevState.OFF)
        self.addStatusMsg("NOT connected to the instrument.")
        #----- PROTECTED REGION END -----#	//	NewportInfinityMeter.Close
        
#------------------------------------------------------------------
#    Is Close command allowed
#------------------------------------------------------------------
    def is_Close_allowed(self):
        self.debug_stream("In " + self.get_name() + ".is_Close_allowed()")
        return not(self.get_state() in [PyTango.DevState.INIT,
            PyTango.DevState.OFF,
            PyTango.DevState.FAULT])

#==================================================================
#
#    NewportInfinityMeterClass class definition
#
#==================================================================
class NewportInfinityMeterClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        'Serial':
            [PyTango.DevString,
            "Device name for serial line, or a local tty file path",
            [] ],
        'Address':
            [PyTango.DevString,
            "Some of this instruments can be connected in a shared bus like 485, having each an identifier.",
            [] ],
        'Measures':
            [PyTango.DevVarStringArray,
            "List of elements to read from the instrument: UnfilteredValue, FilteredValue, PeakValue, ValleyValue.",
            [] ],
        }


    #    Command definitions
    cmd_list = {
        'Exec':
            [[PyTango.DevString, "none"],
            [PyTango.DevString, "none"],
            {
                'Display level': PyTango.DispLevel.EXPERT,
            } ],
        'Open':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'Close':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        }


    #    Attribute definitions
    attr_list = {
        }


#------------------------------------------------------------------
#    NewportInfinityMeterClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name);
        print "In NewportInfinityMeter Class  constructor"

#==================================================================
#
#    NewportInfinityMeter class main method
#
#==================================================================
def main():
    try:
        py = PyTango.Util(sys.argv)
        py.add_class(NewportInfinityMeterClass,NewportInfinityMeter,'NewportInfinityMeter')

        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed,e:
        print '-------> Received a DevFailed exception:',e
    except Exception,e:
        print '-------> An unforeseen exception occured....',e

if __name__ == '__main__':
    main()
