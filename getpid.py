import sys, os.path, ctypes, ctypes.wintypes

Psapi = ctypes.WinDLL('Psapi.dll')
EnumProcesses = Psapi.EnumProcesses
EnumProcesses.restype = ctypes.wintypes.BOOL
GetProcessImageFileName = Psapi.GetProcessImageFileNameA
GetProcessImageFileName.restype = ctypes.wintypes.DWORD

Kernel32 = ctypes.WinDLL('kernel32.dll')
OpenProcess = Kernel32.OpenProcess
OpenProcess.restype = ctypes.wintypes.HANDLE
TerminateProcess = Kernel32.TerminateProcess
TerminateProcess.restype = ctypes.wintypes.BOOL
CloseHandle = Kernel32.CloseHandle

MAX_PATH = 260
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400

def getpid(procname):
    count = 32
    while True:
        ProcessIds = (ctypes.wintypes.DWORD*count)()
        cb = ctypes.sizeof(ProcessIds)
        BytesReturned = ctypes.wintypes.DWORD()
        if EnumProcesses(ctypes.byref(ProcessIds), cb, ctypes.byref(BytesReturned)):
            if BytesReturned.value<cb:
                break
            else:
                count *= 2
        else:
            sys.exit("Call to EnumProcesses failed")

    # print( type(BytesReturned.value))
    # print ( type( ctypes.sizeof(ctypes.wintypes.DWORD) ))
    for index in range(int(BytesReturned.value / ctypes.sizeof(ctypes.wintypes.DWORD))):
        ProcessId = ProcessIds[index]
        hProcess = OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, ProcessId)
        if hProcess:
            ImageFileName = (ctypes.c_char*MAX_PATH)()
            if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH)>0:
                filename = os.path.basename(ImageFileName.value)
                # print(filename)
                # print(procname)
                if filename == bytearray(procname,'latin1'):
                    CloseHandle(hProcess)
                    return ProcessId
            CloseHandle(hProcess)
    return None