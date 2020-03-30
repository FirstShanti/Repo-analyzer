import sys
import time

def loading():
	chars = ['/', '-', '\\', '|', ]
	while True:
		for i in chars:
			yield print(f"\rloading: {i}", end='', flush=True)

