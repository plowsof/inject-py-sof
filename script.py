"""
Developed with 32-bit python on Windows 7. Might work in other environments,
but some of these APIs might not exist before Vista.

Much credit to Eric Blade for this:
https://mail.python.org/pipermail/python-win32/2009-July/009381.html
and David Heffernan:
http://stackoverflow.com/a/15898768/9585
"""
import win32con

import sys
import ctypes
import ctypes.wintypes

import time
from win32 import win32gui
import pywintypes
from win32api import GetSystemMetrics, ChangeDisplaySettings
import platform
import os
user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32

userdir = "C:/Users/Human/Desktop/Raven/SOF PLATINUM/user"

loc_mm_res = os.path.join(userdir,"sofplus/data/mm_res")
loc_mm_desktop = os.path.join(userdir,"sofplus/data/mm_desktop_res")

# force aware so can get accurate measurements of taskbar height
if platform.release() == '10':
	ctypes.windll.shcore.SetProcessDpiAwareness(2)
elif platform.release() == '7':
	ctypes.windll.user32.SetProcessDPIAware()
else:
	sys.exit(1)


WinEventProcType = ctypes.WINFUNCTYPE(
	None,
	ctypes.wintypes.HANDLE,
	ctypes.wintypes.DWORD,
	ctypes.wintypes.HWND,
	ctypes.wintypes.LONG,
	ctypes.wintypes.LONG,
	ctypes.wintypes.DWORD,
	ctypes.wintypes.DWORD
)


# The types of events we want to listen for, and the names we'll use for
# them in the log output. Pick from
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd318066(v=vs.85).aspx
processFlag = getattr(win32con, 'PROCESS_QUERY_LIMITED_INFORMATION',
					  win32con.PROCESS_QUERY_INFORMATION)

threadFlag = getattr(win32con, 'THREAD_QUERY_LIMITED_INFORMATION',
					 win32con.THREAD_QUERY_INFORMATION)
sofId = ""
resizedDesktop = 0



# store last event time for displaying time between events

def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread,
			 dwmsEventTime):
	try:
		global lastTime
		global sofId
		#minimise a minimised window = bad?
		global sofMini
		global sofFull
		global resizedDesktop
		global origResDesktop
		global origResSof


		if event == win32con.EVENT_OBJECT_FOCUS:

			normal = False
			#sof stuff
			fgWindow = win32gui.GetForegroundWindow()
			#print("SoFid = "+str(sofId)+"\n")
			#print("fgwindow"+str(fgWindow)+"\n")

			while True:
				try:
					tup = win32gui.GetWindowPlacement(sofId)
					break
				except Exception as e:
					if e == KeyboardInterrupt:
						raise
					searchForSoFWindow()

			minimized = True
			if tup[1] == win32con.SW_SHOWMAXIMIZED:
				# print("mini false")
				minimized = False
			elif tup[1] == win32con.SW_SHOWMINIMIZED:
				# print("mini true")
				minimized = True
			elif tup[1] == win32con.SW_SHOWNORMAL:
				# print("normal true")
				normal = True

			if fgWindow != sofId:
				print("fg!=sof")
				#focused window != sof
				if normal or not minimized:
					#force minimise when not in focus
					win32gui.ShowWindow(sofId, win32con.SW_MINIMIZE)

				#if we resized desktop already
				#lost focus of sof
				# print("Desktop Active.")
				if origResDesktop != getDesktop():
					if resizedDesktop == 0:
						if ChangeDisplaySettings(None, 0) == win32con.DISP_CHANGE_SUCCESSFUL:
							resizedDesktop = 1
							print("Change res to original")
						else:
							print("Change res to original failed")

			else:
				#what if we fail these checks and 'origResSof is never set?'
				#shouldnt we wait while until set?
				while True:
					if normal:
						print("sof = normal")
						origResSof = getSoFRes(sofId)
						print(f"Getting Sof Resolution : {origResSof[0]} , {origResSof[1]}")
						resizedDesktop = 0
						break
					else:
						print("DEBUG**************not normal and minimised")         
						while True:
							try:
								tup = win32gui.GetWindowPlacement(sofId)
								print(tup[1])
								if tup[1] == win32con.SW_SHOWNORMAL:
									# print("mini false")
									normal = True
									print("DEBUg- maximised")
								break
							except Exception as e:
								if e == KeyboardInterrupt:
									raise
								searchForSoFWindow()

				#we have focus of sof
				# print("Sof Active.")
				# print(f"What it SHOULD be : {origResSof[0]} , {origResSof[1]}")
				# print(f"What it IS : {resDesktop[0]} , {resDesktop[1]}")
				#if the current res of desktop != current res of sof
				if getDesktop() != origResSof:
						print("resize desktop to sof res")
						if not setRes(origResSof[0],origResSof[1]):
							print("failed setting sof resolution")
						#mini then max seems to fix the LALT bug... hm
						win32gui.ShowWindow(sofId, win32con.SW_MINIMIZE)
						win32gui.ShowWindow(sofId, win32con.SW_MAXIMIZE)
						#Fix the sound bug
						print("sound fix here")
						#cbuf_addText (b"snd_restart\n")
						#COM_Printf(b"Sound fixed, sorry for spam cant help it\n")

				else:
					print("desktop == sof apparently")
		elif event == win32con.EVENT_OBJECT_SHOW:
			# getSoFRes(sofId)
			# print(f"LOCRESX : {origResSof[0]} LOCRESY : {origResSof[1]}")
			pass
			
	except KeyboardInterrupt:
		sys.exit(1)

#def fgWindowNotSof():
#def fgWindowSof():

def setHook(WinEventProc, eventType):
	return user32.SetWinEventHook(
		eventType,
		eventType,
		0,
		WinEventProc,
		0,
		0,
		win32con.WINEVENT_OUTOFCONTEXT
	)

def sofWinEnumHandler( hwnd, ctx ):
	global sofId
	#if win32gui.IsWindowVisible( hwnd ):
	#print (hex(hwnd), win32gui.GetWindowText( hwnd ))
	if win32gui.GetWindowText( hwnd ) == "SoF":
		sofId = hwnd
		return False
	return True

def searchForSoFWindow():
	global sofId

	sofId = ""
	while sofId == "":
		# print("cant find SoF,,, ill keep looking")
		try:
			win32gui.EnumWindows( sofWinEnumHandler, None )
		except Exception as e:
			if e == KeyboardInterrupt:
				raise
			pass
		if sofId == "":
			time.sleep(2)
	# win32gui.ShowWindow(sofId, win32con.SW_MINIMIZE)
	# win32gui.ShowWindow(sofId, win32con.SW_MAXIMIZE)
	print("Found the SoF window")
	return sofId



def setRes(x,y):
	
	devmode = pywintypes.DEVMODEType()

	devmode.PelsWidth = x
	devmode.PelsHeight = y
	print("Set the desktop res to:"+str(x)+"x"+str(y))

	devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

   
	if ChangeDisplaySettings(devmode, 0) != win32con.DISP_CHANGE_SUCCESSFUL:
		return False
	return True

def getSoFRes(hwnd):
	#get res from SoFplus generated .cfg file
	#rect can not be trusted
	global loc_mm_res
	while True:
		try:
			with open(loc_mm_res, "r") as f:
				x = f.readlines()
			break
			pass
		except Exception as e:
			print("Error, please make sure you're running the SoFplus script and there is file called mm_res in sofplus/data")
			time.sleep(1)
	data = x[1].split()
	data = data[2][1:-1]
	print("RES from file"+ str(data))
	res = data.split("x")
	retRes={}
	retRes[0]=int(res[0])
	retRes[1]=int(res[1])
	'''
	while True:
		try:
			rect = win32gui.GetWindowRect(hwnd)
			break
		except Exception as e:
			if e == KeyboardInterrupt:
				raise
			hwnd = searchForSoFWindow()
	x = rect[0]
	y = rect[1]
	w = rect[2] - x
	h = rect[3] - y
	retRes[0] = w
	retRes[1] = h
	'''
	return retRes
def getDesktop():
	global resDesktop
	#print("Width =", GetSystemMetrics(0))
	#print("Height =", GetSystemMetrics(1))
	resDesktop={}
	resDesktop[0]=GetSystemMetrics(0)
	resDesktop[1]=GetSystemMetrics(1)
	return resDesktop

def main():
	global COM_Printf
	global cbuf_addText
	global sofId
	global origResDesktop
	global loc_mm_desktop
	standardStrInput = ctypes.CFUNCTYPE (
	None,
	ctypes.c_char_p
	)
	#wait for SoF id to be set first
	#then continue 
	origResDesktop={}
	#origResDesktop = getDesktop()
	with open(loc_mm_desktop, "r+") as f:
		x = f.readlines()
		val = x[0].split("x")
		origResDesktop[0] =int(val[0])
		origResDesktop[1] =int(val[1])
	#strip the "\n" from res values


	#pipe = open(r'\\.\\pipe\mayhem', 'rb', 0)
	# do normal read operatino in python
	#with pipe:
	#	indata =pipe.read()
	#print(indata)
	# something like this, fix it lol
	# turn it into a while loop lol.

	print(origResDesktop)
	searchForSoFWindow()
	print("SoF found")
	print("Attatching to console input")
	#COM_Printf = standardStrInput(0x2001C6E0)
	#print("%s is %d years old." % (name, age))
	#cbuf_addText = standardStrInput(0x20018180)
	print("Attatched")
	
	print("Adding hooks")

	ole32.CoInitialize(0)

	WinEventProc = WinEventProcType(callback)
	user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE

	focusHook = setHook(WinEventProc,win32con.EVENT_OBJECT_FOCUS)
	if not focusHook:
		print('SetWinEventHook failed')
		sys.exit(1)

	sizeMoveHook = setHook(WinEventProc,win32con.EVENT_OBJECT_SHOW)
	if not sizeMoveHook:
		print('SetWinEventHook failed')
		sys.exit(1)

	msg = ctypes.wintypes.MSG()
	while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
		user32.TranslateMessageW(msg)
		user32.DispatchMessageW(msg)
		# time.sleep(0.1)

	user32.UnhookWinEvent(focusHook)
	user32.UnhookWinEvent(sizeMoveHook)
	ole32.CoUninitialize()


if __name__ == '__main__':
	print('this script must be injected')
	main()
elif __name__ == '__mayhem__':
	try:
		print("We where injected gj")
		main()
	except KeyboardInterrupt:
		sys.exit(1)
#/////////////////////////////////////////////////////////////////////////
