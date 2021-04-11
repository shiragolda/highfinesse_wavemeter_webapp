import zmq
import time
import socket

from ctypes import *

import os


from wavemeter import WM

from ast import literal_eval

##
def get_ip():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255',1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

    
##


class wmHandler:
    def __init__(self,port=9000):
        
        self.wm = WM(mode='server')
        
        zmq_context = zmq.Context()
        self.port = port
        

        self.socket = zmq_context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s"%self.port)
        self.ip = get_ip()

        print("Handling requests on %s:%s"%(self.ip,self.port))
        print('')
        
        go = True   
       	while(go):
            try:
            	self.handle()
            except(KeyboardInterrupt):
            	go=False
    
        
        
    def handle(self):
        msg = self.receive()
        lst = msg.split(';')
        func_name = lst[0]
        func_args = literal_eval(lst[1])
        func_kwargs = literal_eval(lst[2])
        #print(func_args)
        #print(func_kwargs)
        
        ret = ''
        try:
        	func = getattr(self.wm,func_name)
        	#print(func)

        	ret = func(*func_args,**func_kwargs)
        	#print(ret)

        except Exception as e:
        	print(e)

        self.reply(str(ret))
     
    
     
        
    def receive(self):
        message = self.socket.recv()
        if isinstance(message,bytes): message = message.decode()
        #print(message)
        return message #string

    def reply(self,message):
        #print(message)
        if isinstance(message,str): message = message.encode()
        self.socket.send(message) #send as bytes
        
    def close(self):
        self.socket.close()
    


        
if __name__=='__main__':
    handle = wmHandler()
