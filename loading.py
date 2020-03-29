import sys
import time

def loading():
	chars = ['/', '-', '\\', '|', ]
	while True:
		for i in chars:
			yield sys.stdout.write("\rloading: {0}".format(i))

