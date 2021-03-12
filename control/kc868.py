#!/usr/bin/python
# --*-- coding:utf-8 --*--
import atexit
import socket  
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(levelname)s] (%(threadName)-9s) %(message)s',)


#-------------------------------------------------------
class KC868:
    '''
    #SET
    # Sets only port #1 on/off
        RELAY-SET-255,1,1
        RELAY-SET-255,1,0

    # Sets all ports on
        RELAY-SET_ALL-255,255,255,255,255

    # Sets all odd ports on
        RELAY-SET_ALL-255,85,85,85,85

    # Sets all even ports on 
        RELAY-SET_ALL-255,170,170,170,170

    # Sets all ports off
        RELAY-SET_ALL-255,0,0,0,0


    #READ
    # Reads port #1
        RELAY-READ-255,1    Reply On: RELAY-READ-255,1,1,OK
                            Reply Off: RELAY-READ-255,1,0,OK

    # Reads all states
        RELAY-STATE-255     Reply: RELAY-STATE-255,0,0,0,0,OK

    #INPUTS
    #Query the status of Inputs 
        RELAY-GET_INPUT-255     Reply: RELAY-GET_INPUT-255,254,OK   254:11111110------
                                                                    Means input 1 was triggered

                                                                    255:11111111------
                                                                    No inputs triggered


    '''
    class relay:
        def __init__(self, name, state):
            self.name = name
            self.state = state

            #Sets the current state of the channel ON/OFF    
        def __set_state__(self, blockState):
            if 1 << self.name - 1 == blockState:
                self.state = True
            else:
                self.state = False


    #Get the type of device we are connected to
    def __device__(self):
        cmd = 'RELAY-SCAN_DEVICE-NOW'
        responce = self.__send__(cmd)
      
        status = 'OK'
        message = 'Device scan started.'

        if 'ERROR' in responce:
            status = 'ERROR'
            message = 'Device failed to scan.'

        if 'CHANNEL_32' in responce:
            message = "32_CHANNEL"
        elif 'CHANNEL_16' in responce:
            message = "16_CHANNEL"
        elif 'CHANNEL_8' in responce:
            message = "8_CHANNEL"
        elif 'CHANNEL_4' in responce:
            message = "4_CHANNEL"
        elif 'CHANNEL_2' in responce:
            message = "2_CHANNEL"
        else:
            message = 'UNKNOWN'    
 
        return status, message

    #Initialize
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        
        #Create socket
        try:
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            logging.info("Created socket")
        except socket.error as e:  
            logging.debug("Socket creation failed with error %s" % (e)) 
        #TODO: raise an exception when this fails to the caller

        #Connect to resource
        try:
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            logging.info("Created connection.")
        except socket.error as e:  
            logging.debug("Socket connection failed with error %s" % (e)) 
        else:
            s, self.device = self.__device__()
            logging.debug("Object creation status:%s" % s)
            logging.info("Device repored itself as: %s" % self.device)
        #TODO: raise an exception when this fails to the caller

        #Determine the number of relays
        numRelays = int((self.device).replace('_CHANNEL', ''))

        #Create objects to represent each relay
        self.relays = []
        for i in range(1, numRelays+1):
            self.relays.append(self.relay(i, False))
            logging.debug("Relay %s created." % i)

        logging.info("Getting relay state.")
        status = self.GetRelayState()
        logging.info("Status: %s" % status)

        #Clean up resources when we close
        atexit.register(self.socket.close())


    #Send a command to the device
    def __send__(self, cmd):
        try:
            logging.info("Sending command:%s" % cmd)
            self.socket.sendto(cmd.encode(),(self.host, self.port))
            responce = self.socket.recv(1024).decode()  # receive response
        except:
            logging.info("Failed to send command.")
        else:
            logging.info("Command succeeded:\n Responce:%s" % (responce))
            return responce


    def ReadRelay(self, port):
        cmd = 'RELAY-READ-255,%s'% port
        responce = self.__send__(cmd)

        responce = responce.replace('%s,'% cmd, '').replace(',OK', '')
        if int((responce[0:-1])):
            state = 'ON'
            self.relays[port-1].state = True
        else:
            state = 'OFF'
            self.relays[port-1].state = False

        status = 'OK'
        message = 'Relay #%s was read.'% port

        if 'ERROR' in responce:
            status = 'ERROR'
            message = 'Relay #%s failed to respond.'% port
  
        return status, message, state


    def RelayOn(self, port):
        cmd = 'RELAY-SET-1,%s,1'% port
        responce = self.__send__(cmd)
    
        status = 'OK'
        message = 'Relay #%s was turned ON.'% port

        if 'ERROR' in responce:
            status = 'ERROR'
            message = 'Relay #%s failed to turn ON.'% port
  
        return status, message


    def RelayOff(self, port):
        cmd = 'RELAY-SET-1,%s,0'% port
        responce = self.__send__(cmd)

        status = 'OK'
        message = 'Relay #%s was turned OFF.'% port

        if 'ERROR' in responce:
            status = 'ERROR'
            message = 'Relay #%s failed to turn OFF.'% port
        
        return status, message


    def AllOn(self):
        cmd = 'RELAY-SET_ALL-255,255,255,255,255'
        responce = self.__send__(cmd)
        status = 'OK'
        message = 'All relay ports turned ON.'

        if 'ERROR' in responce:
            status = 'ERROR'
            message = 'All relay ports failed to turn ON.'
        
        return status, message


    def AllOff(self):
        cmd = 'RELAY-SET_ALL-255,0,0,0,0'
        responce = self.__send__(cmd)
        status = 'OK'
        message = 'All relay ports turned OFF.'

        if 'ERROR' in responce:
            status = 'ERROR'
            message = 'All relay ports failed to turn OFF.'
        
        return status, message


    def GetRelayState(self):
        cmd = 'RELAY-STATE-255'
        responce = self.__send__(cmd)
        status = 'OK'
        
        responce = responce.replace('%s,'% cmd, '').replace(',OK', '')
        
        blockStatus = responce[-1]
        blocks = (responce[0:-1]).split(',')
        oneToEight = int(blocks[3])
        nineToSixteen = int(blocks[2])
        seventeenToTwentyfour = int(blocks[1])
        twentyfiveToThirtytwo = int(blocks[0])

        for i in range(8):
            self.relays[i].__set_state__(oneToEight)
        for i in range(8, 16):
            self.relays[i].__set_state__(nineToSixteen)
        for i in range(16, 24):
            self.relays[i].__set_state__(seventeenToTwentyfour)
        for i in range(24, 32):
            self.relays[i].__set_state__(twentyfiveToThirtytwo)

        if 'ERROR' in responce:
            status = 'ERROR'
            
        return status


    #Self test the device
    def SelfTest(self):
        cmd = 'RELAY-TEST-NOW'
        responce = self.__send__(cmd)
      
        status = 'START'
        message = 'Self test started.'

        if 'ERROR' in responce:
            status = 'ERROR'
            message = 'Device failed to test.'
 
        return status, message

    