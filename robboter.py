#!/usr/bin/python3
#-*- coding: utf-8 -*-
enc = "utf-8"
# 
# robboter - the ultimate IRC bot
#
# read the README file for further information
# 
# CHANGELOG
# 11.5.14: Created basic outlines / classes / basic functions
# 30.5.14: Repaired some class stuff, first small tests, added KeyInterrupt
# 31.5.14: Added Join, some more tests, schöner Log(wie in irssi), kann jetzt recht zuverlässig joinen und mitloggen
# 01.6.14: Added loads of function prototypes for the IRC protocol / further features
# 04.6.14: Added more function prototypes, added youtube link parser and urban dictionary lookup function. Completed few smaller functions
#	   Made first Menu Prototype, added some more function prototypes
# 26.9.16: Minor fixes, added git
# Version and source Information

version     = '0.10'
author      = 'robrt'
latest_edit = '26.9.2016'

# -----------------------
# Developer Settings

debug = 1	# 0/1 - debugging on/off

# -----------------------

import settings
import socket
import time
import re
import random
import output
import requests
from bs4 import BeautifulSoup

# -----------------------
# some constants
rn = '\r\n'
logfile = "chatlog.log"


class IrcBot:
	ownerauth = 0
	def __init__(self, nick, ident, realname, owner, controlchan, channels):
		self.nick        = nick
		self.ident       = ident
		self.realname    = realname
		self.owner       = owner
		self.controlchan = controlchan
		self.channels    = channels
		self.connected   = False
		self.auth	 = 0

	def connectToServer(self, host, port):
		self.host = host
		self.port = port
		self.server = socket.socket()
		try:
			self.server.connect((host, port))
		except socket.error:
			out.promptFail("Socket Error, quitting")
			quit()

		nickMsg = 'NICK ' + self.nick + rn
		userMsg = 'USER ' + self.ident + ' 8 * : ' + self.realname + rn 
		self.sendToServer(nickMsg)
		self.sendToServer(userMsg)

	def sendToServer(self, message):
		self.server.send(bytes(message, enc))

	def pong(self, ping):
		print(re.split("PING :", ping))
		ping = "PING :" + re.split("PING :", ping)[1]
		self.sendToServer(re.sub('I', 'O', ping, 1))

	def recv(self):
		recvLength = 2**13
		try:
			message = str(self.server.recv(recvLength), enc)

		except UnicodeError:
			out.debug("Unicode Error", debug)
			return

		self.parse(message)

	def parse(self, message):
		out.debug(message, debug)
		if 'PRIVMSG' in message:
			#print("p " + message)
			self.analyzePrivMsg(message)

		elif 'MOTD' in message:
			if self.connected == False:
				l = time.strftime("%D %H:%M", time.localtime()) + " Joined Server " + self.host + "\n"
				log(logfile, l)

				time.sleep(5)	# wait before first Joining
				self.join([self.controlchan])
				self.join(self.channels)
				self.connected = True
				
		elif 'PING :' in message :#and len(message) <= 24:
			#print("pi " + message)
			self.pong(message)

		else:
			#print(message)
			pass

	def analyzePrivMsg(self, privmsg): # add inderError exception?
		# TODO
		# ERST PRÜFEN OB DAS WIRKLICH NE PRIVMSG IST, ODER OB JEMAND EINFACH EINEN TEXT MIT PRIVMSG GESCHICKT HAT
		if privmsg[0] == ':':
			privmsg = privmsg[1:]
		if ':' in privmsg:
			splt    = re.split(":", privmsg)
			if len(splt) > 2:
				for i in range(0,len(splt)):
					if i > 1:
						splt[i] = ":" + splt[i]
		else:
			return
		if '!' in splt[0]:
			sender  = re.split("!", re.split("PRIVMSG", splt[0])[0])[0] # nick of sender
		else:
			return
		message = splt[1:] # assuming theres no ":" within the message
		m = ''
		for i in message:
			m += i
		#print(m)
		message = m
		if '#' in splt[0]:
			chan    = "#" + re.split("#", splt[0])[1]
		else: 
			return
		if self.owner in sender:
			if (self.auth == 0):
				self.challenge()
			else:
				self.parseCommand(message, chan)
			pass
		else:
			pass
		
		if self.containsLink(message):
			a = self.linkParse(message)
			if a != '':
				self.say(chan, a)
		else:
			pass

		self.parseCommand(message, chan)

		n = time.strftime("%H:%M", time.localtime()) + " < " + sender + "@" + chan[1:len(chan)-1] + "> " + message
		log(logfile,n)

	def parseCommand(self, message, chan):
		if len(message) <= 4:
			return
		if message[0:4] == '!ud ':
			term = message.split()
			if len(term) != 2:
				return
			else:
				exp = self.urbanDictionary(term[1])
				if "Error" in exp or "is undefined" in exp:
					self.say(chan, exp)
					return
				else:
					exp_sp = exp.split()
					l = len(exp_sp)
					e = ''
					for word in exp_sp:
						e += word + " "
						if len(e) > 50:
							self.say(chan, e)
							e = ''
					self.say(chan, e)
				#self.say(chan, self.urbanDictionary(term[1]))
	#	pass # TODO

	def join(self, chans):
		for i in chans:
			if i[0] == '#':
				self.sendToServer("JOIN " + i + rn)
			else:
				self.sendToServer("JOIN #" + i + rn)

	def challenge(self):
		pass
	
	def say(self, channel, message):
		self.sendToServer('PRIVMSG ' + channel + ' :' + message + rn)
	
	def msg(self, nick, message):
		#TODO?
		self.sendToServer('PRIVMSG ' + nick + ' :' + message + rn)
	
	def kick(self, nick, channel):
		self.sendToServer('KICK ' + channel + ' ' + nick + rn)
	
	def invite(self, nick, channel):
		pass

	def part(self, channel):
		pass

	def quit(self, message):
		self.sendToServer("QUIT :" + message + rn)
		l = time.strftime("%D %H:%M", time.localtime()) + " Left Server " + settings.host +  "\n"
		log(logfile, l)
	
	def stats(self, param): # param: l/m/o/u
		# l: returns a list of the server's connections, showing how
                # long each connection has been established and the
                # traffic over that connection in Kbytes and messages for
                # each direction;
		#
		# m: returns the usage count for each of commands supported
                # by the server; commands for which the usage count is
                # zero MAY be omitted;
		#
		# o: returns a list of configured privileged users,
                # operators; 
		#
		# u: returns a string showing how long the server has been
                # up.
		pass
			
	def getTopic(self, channel):
		pass
	
	def setTopic(self, channel, topic):
		pass

	def notice(self, channel, message):
		self.sendToServer('NOTICE ' + channel + ' ' + message + rn)

	def names(self, channel):
		self.sendToServer("NAMES " + channel + rn)
	
	def msgPing(self, message):
		pass

	def detectCurse(self, chan, nick, message, dic):
		for i in message.split():
			if i in dic:
				self.say(chan, 'Please don\'t swear, ' + nick)

	
	def isPublicCommand(self, message):
		pass
	
	def containsLink(self, message):
		if "https://" in message or "http://" in message:
			return True
		else:
			return False

	def linkParse(self, message):
		if self.containsLink(message):
			x = message.split()
			link = ''
			for i in x:
				if self.containsLink(i):
					link = i
					break
			if "www.youtube.com/watch?v=" in link:
				return self.youtubeParse(link)
			else:
				return ''
		else:
			return ''
	
	def youtubeParse(self, link):
		site = requests.get(link)
		if site.status_code != 200:
			return 'Error - cant open youtube link'
		else:
			soup = BeautifulSoup(site.text)
			title = soup.title.string
			print(title)
			views = soup.find(id="watch7-views-info").div.string
			return link + " ~ " + title + ", Views: " + views + rn
	
	def help(self, message):
		pass
	
	def disable(self, command):
		pass
	
	def enable(self, command):
		pass
	
	def urbanDictionary(self, word):
		r = requests.get("http://www.urbandictionary.com/define.php?term="+word)
		if r.status_code != 200:
			return 'Connection Error' + rn
		else:
			soup = BeautifulSoup(r.text)
			meaning = soup.find("div", "meaning")
			if meaning == None:
				return word + " is undefined." + rn
			else:
				meaning = meaning.text
				if len(meaning) > 1024:
					return 'UD Entry too long. look it up: http://www.urbandictionary.com/define.php?term='+word
				try:
					return word + " - " + meaning.rstrip() + rn
				except AttributeError:
					return 'Error'
		pass
	
	def setNick(self, newnick):
		pass
	
	def setUser(self, newUser):
		pass

	def oper(self, name, password):
		pass

	def mode(self, channel, command):
		pass

	def list(self):
		pass
	
	def shell(self):
		a = input(">>> ")
		self.sendToServer(a + rn)
		pass
	
	def stats(self):
		print(" no stats to show ")
		pass
	
# TODO
# Implement into Class structure
def log(filename, message):
	f = open(filename , 'a')
	
	# remove \r in logfile, add \n if it lacks
	message = re.sub('\r\n' , '\n', message, 1)
	if message[len(message)-1] != '\n':
		message = message + '\n'
	f.write(message)
	f.close

def startNormalBot():
	global out 
	out = output.Output()
	bot = IrcBot(settings.nick, settings.ident, settings.realname, settings.owner, settings.controlChannel, settings.channels)
	while 1:
		bot.connectToServer(settings.host, settings.port)
		while 1:
			try:
				bot.recv()
			except KeyboardInterrupt:
				print()
				out.promptInfo("Keyboard Interrupt")
				out.promptInfo("Opening Menu")
				menu = '''+--------------------------------+
| 1. IRC Shell                   |
| 2. Send Chat Message           |
| 3. Show Settings               |
| 4. Show Stats                  |
| 5. ---Pro Version---           |
| 6. ---Pro Version---           |
| 7. ---Pro Version---           |
| 8. About                       |
| 9. Quit                        |
| 0. Back [Default]              |
+--------------------------------+
|  '''
				out.clear()
				print(menu)
				choice = input('+->> ')
				if choice == '1':
					bot.shell()
				elif choice == '2':
					bot.say(input('chan: '), input('message: '))
				elif choice == '3':
					showSettings()
				elif choice == '4':
					bot.stats()
				elif choice == '5':
					pass
				elif choice == '6':
					pass
				elif choice == '7':
					pass
				elif choice == '8':
					about()
				elif choice == '9':
					bot.quit('')
					quit()
				elif choice == '0':
					continue

def showSettings():
	pass

def about():
	pass
def main():
	startNormalBot()




if __name__ == "__main__":
	main()

# set auth to 0 if owner leaves
#
