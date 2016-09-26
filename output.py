#!/usr/bin/python3
#-*- coding: utf-8 -*-
# 
enc = "utf-8"

def main():
	print("This File shouldn't be run directly")

if __name__ == "__main__":
	main()

class Output:
	pink      = '\033[95m'
	blue      = '\033[94m'
	green     = '\033[92m'
	yellow    = '\033[93m'
	red       = '\033[91m'
	endcolor  = '\033[0m'
	white     = "\033[.37m"
	def __init__(self):
		pass

	def promptOK(self, message):
		print(self.green + '[+] ' + message + self.endcolor)

	def promptFail(self, message):
		print(self.red + '[-] ' + message + self.endcolor)

	def promptInfo(self, message):
		print(self.yellow + '-*- ' + message + self.endcolor)

	# color(String) is either:
	# pink/blue/green/yellow/red/white
	def cPrint(self, message, color):
		if color == 'pink' or color == 'p':
			c = self.pink
		elif color == 'blue' or color == 'b':
			c = self.blue
		elif color == 'green' or color == 'g':
			c = self.green
		elif color == 'yellow' or color == 'y':
			c = self.yellow
		elif color == 'red' or color == 'r':
			c = self.red
		elif color == 'white' or color == 'w':
			c = self.white
		else:
			print("Output.cPrint Error: " + color + " is not a valid color")
			return
		
		print(c + message + self.endcolor)

	def debug(self, message, flag):
		if(flag==1):
			print(self.white + message + self.endcolor)
	def clear(self):
		import os
		os.system('cls' if os.name == 'nt' else 'clear')
