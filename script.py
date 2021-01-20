import ctypes


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
	print("Injected successfully")
	COM_Printf(b"Successfully Injected Your code\n")


if __name__ == '__main__':
	print('this script must be injected')
elif __name__ == '__mayhem__':
	mayhem()

