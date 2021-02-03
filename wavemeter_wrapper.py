import zmq
import time


from ctypes import *

import os
if __name__=='__main__':
    os.chdir("/home/labuser/Insync/electric.atoms@gmail.com/Google Drive/code/highfinesse_wavemeter")

# wlmData.dll related imports
import wlmData_client 
import wlmConst



class wmHandler:
    def __init__(self,port=9000):
        zmq_context = zmq.Context()
        self.port = port
        self.socket = zmq_context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s"%self.port)
        print("Handling requests on port %s"%(self.port))
        
        
        try:
           print('loading')
           self.dll = wlmData_client.LoadDLL()
           time.sleep(1)
        except Exception as e:
           print(e)
        
        
        while(True):
            self.handle()
        
    def handle(self):
        message = self.receive()
        
        returned = ""
        loc = {'self':self}
        
        try:
            exec('returned = self.dll.%s'%message,{},loc) #loc passes the dictionary of local variables. neccesary because exec() doesn't return anything
            returned = str(loc['returned'])
        except Exception as e:
            print(e)
        
        self.reply(returned)
        
    def receive(self):
        message = self.socket.recv()
        if isinstance(message,bytes): message = message.decode()
        return message #string

    def reply(self,message):
        if isinstance(message,str): message = message.encode()
        self.socket.send(message) #send as bytes
        
    def close(self):
        self.socket.close()
    


        
if __name__=='__main__':
    handle = wmHandler()