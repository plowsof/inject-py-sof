import ctypes
import win32pipe, win32file, pywintypes
import time
import os
import codecs
import sys

def enc(instr):
	return instr.encode("latin-1")

def mayhem():

	# As has been mentioned before, all Python types except integers, strings, and bytes objects have
	# to be wrapped in their corresponding ctypes type, so that they can be converted to the required C data type:
	# Set up prototype and parameters for the desired function call
	COM_Printf_type = ctypes.CFUNCTYPE (
		None,
		ctypes.c_char_p
		)

	# hllApiParams = (1, "p1", 0), (1, "p2", 0), (1, "p3",0), (1, "p4",0)

	# Actually map the DLL function to a Python name `hllApi`.
	COM_Printf = COM_Printf_type (0x2001C6E0)
	
	# pipe.write(b"Im Alive")
	# print("Injected successfully")
	COM_Printf(b"wAiting for message from inner..\n")
	try:
		handle = win32file.CreateFile(
			r'\\.\pipe\mayhem',
			win32file.GENERIC_READ | win32file.GENERIC_WRITE,
			0,
			None,
			win32file.OPEN_EXISTING,
			0,
			None
		)
		# handle = open(r'\\.\\pipe\mayhem', 'rb', 0)
		
		res = win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
		if res == 0:
			COM_Printf(f"SetNamedPipeHandleState return code: {res}".encode() )

		# while True:
		resp = win32file.ReadFile(handle, 4096)
		COM_Printf(f"message: {resp}\n".encode() )
			
			
	except pywintypes.error as e:
		COM_Printf(b"Somethign went wrong")
		if e.args[0] == 2:
			COM_Printf(b"no pipe, trying again in a sec")
			time.sleep(1)
		elif e.args[0] == 109:
			COM_Printf(b"broken pipe, bye bye")
			quit = True
	# print("Read a message from Outer")
	# data = b""
	# data =data.decode("latin-1")
	COM_Printf(bytes(f"Successfully Injected Your code \n",'latin-1'))
	

	# while True:
	# 	time.sleep(1)


if __name__ == '__main__':
	# mayhem()
	print('this script must be injected')
elif __name__ == '__mayhem__':
	# pipe = open(r'\\.\\pipe\mayhem', 'r+b', 0)
	mayhem()
	# pipe.close()
	# print("Reading!!!")
	# while True:
	# 	data = pipe.read()
	# 	orig_Com_Printf(data.encode("latin-1"))



