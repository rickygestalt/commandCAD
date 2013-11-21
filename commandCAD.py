import pifacecad

import subprocess
cad = pifacecad.PiFaceCAD()
import sys, tty, termios
scrollOffset = 0
commandOffset = 0
workingDirectory = ""
output = ""

f = open('previousCommands','r')
previousCommands = []
for line in f:
	previousCommands.append(line.replace("\n",""))
print(previousCommands)
f.close()
# while not cad.switches[4]:
	# x = 
	# cad.LCD.write()

def scrollRight(event):
	cad.lcd.cursor_off()
	cad.lcd.blink_off()
	global scrollOffset
	global output
	print("Scroll Right")
	if len(output) > 16 and scrollOffset < len(output)-17:
		scrollOffset +=1
		cad.lcd.set_cursor(0,1)
		cad.lcd.write(output[0+scrollOffset:15+scrollOffset])

def scrollLeft(event):
	cad.lcd.cursor_off()
	cad.lcd.blink_off()
	global scrollOffset
	global output
	print("Scroll Left")
	if scrollOffset > 0:
		scrollOffset -= 1
		cad.lcd.set_cursor(0,1)
		cad.lcd.write(output[0+scrollOffset:15+scrollOffset])		

def enter(event):
	global scrollOffset
	global commandIndex
	global previousCommands
	global output
	global command
	global workingDirectory
	scrollOffset = 0
	commandIndex = 0
	print(command)
	previousCommands.append(command)
	print(previousCommands)

	try:
		tempCommand = "cd " + workingDirectory + "; " + command
		if command[0] == 'c' and command[1] == 'd':
			print("cd command")
			tempCommand += "; pwd"
		output = subprocess.check_output(tempCommand,shell=True)
		output = output.decode("utf-8")
		if command[0] == 'c' and command[1] == 'd':
			output = output.replace("\n"," ")
			workingDirectory = output
			print("New workingDirectory = ({})".format(workingDirectory))
			output = " "
		else:
			output = output.replace("\n"," ")

	except subprocess.CalledProcessError as e:
		output = "Wrong command ({})".format(e)
		print(output)


	print(output)
	command = ""
	cad.lcd.clear()
	cad.lcd.set_cursor(0,1)
	cad.lcd.write(output[0+scrollOffset:15+scrollOffset])
	cad.lcd.set_cursor(0,0)
	cad.lcd.write("$")
	cad.lcd.cursor_on()
	cad.lcd.blink_on()


def backward(event):
	global commandIndex
	global previousCommands
	global command
	global commandOffset
	commandOffset = 0
	try:
		commandIndex-=1
		command = previousCommands[commandIndex]
	except:
		commandIndex+=1
	cad.lcd.cursor_on()
	cad.lcd.blink_on()
	cad.lcd.clear()
	cad.lcd.write("$")
	cad.lcd.write(command)
	print(command)

def forward(event):
	global commandIndex
	global previousCommands
	global command
	global commandOffset
	commandOffset = 0
	cad.lcd.cursor_on()
	cad.lcd.blink_on()
	try:
		if commandIndex < -1:
			commandIndex+=1
			command = previousCommands[commandIndex]
			cad.lcd.clear()
			cad.lcd.write("$")
			cad.lcd.write(command)
			print(command)
		else:
			cad.lcd.clear()
			cad.lcd.write("$")
			command=""
	except:
		pass


def saveCommand(event):
	f = open('previousCommands','a')
	f.write(command+"\n")
	f.close()
# def exit(event):
	# global listener
	# print("Quiting")
	# listener.deactivate()
	# sys.exit()


listener = pifacecad.SwitchEventListener()
listener.register(6, pifacecad.IODIR_FALLING_EDGE, backward)
listener.register(7, pifacecad.IODIR_FALLING_EDGE, forward)
listener.register(4, pifacecad.IODIR_FALLING_EDGE, exit)
listener.register(0, pifacecad.IODIR_FALLING_EDGE, scrollLeft)
listener.register(1, pifacecad.IODIR_FALLING_EDGE, scrollRight)
listener.register(2, pifacecad.IODIR_FALLING_EDGE, saveCommand)
listener.register(3, pifacecad.IODIR_FALLING_EDGE, enter)
listener.activate()





class _Getch:
	# Gets a single character from standard input.  Does not echo to the screen.
    def __init__(self):
        self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


count = 1
print(cad.switches[4].value)
cad.lcd.write("$")
commandIndex = 0
command = ""
while not cad.switches[4].value:
	print(command)
	# print ("Here1")
	getch = _Getch()
	# print ("here2")
	character = getch()
	# print ("here 3")
	print(character)
	if character == '\r':
		if len(command):
			# print ("Newline")
			# command += character
			scrollOffset = 0
			commandOffset = 0
			commandIndex = 0
			print(command)
			previousCommands.append(command)
			print(previousCommands)

			try:
				tempCommand = "cd " + workingDirectory + "; " + command
				if command[0] == 'c' and command[1] == 'd':
					print("cd command")
					tempCommand += "; pwd"
				output = subprocess.check_output(tempCommand,shell=True)
				output = output.decode("utf-8")
				if command[0] == 'c' and command[1] == 'd':
					output = output.replace("\n"," ")
					workingDirectory = output
					print("New workingDirectory = ({})".format(workingDirectory))
					output = " "
				else:
					output = output.replace("\n"," ")

			except subprocess.CalledProcessError as e:
				output = "Wrong command ({})".format(e)
				print(output)


			print(output)
			command = ""
			cad.lcd.clear()
			cad.lcd.set_cursor(0,1)
			cad.lcd.write(output[0+scrollOffset:15+scrollOffset])
			cad.lcd.set_cursor(0,0)
			cad.lcd.write("$")
			cad.lcd.cursor_on()
			cad.lcd.blink_on()

	elif character == '\x7F':
		print("Backspace!")
		if command != "":
			command = command[:-1]

			if len(command) >= 14:
				commandOffset -= 1
				cad.lcd.set_cursor(1,0)
				cad.lcd.write(command[commandOffset:commandOffset+14])

			else:
				cursor = cad.lcd.get_cursor()
				col, row = cursor
				col-=1
				cad.lcd.set_cursor(col,row)
				cad.lcd.write(" ")
				cad.lcd.set_cursor(col,row)
				cad.lcd.cursor_on()
				cad.lcd.blink_on()



	else:
		command += character
		if len(command) >= 15:
			commandOffset +=1
			cad.lcd.set_cursor(1,0)
			cad.lcd.write(command[commandOffset:commandOffset+14])
		else:
			cad.lcd.write(character)
