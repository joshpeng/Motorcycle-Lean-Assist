'''
Rename input files with too many periods.
Filenames should only have one period for the file extension separator.
'''

import sys
import os
def lv2grename():
	print("Renaming files...")
	for filename in os.listdir('.'):
		sp=filename.split(".")
		if len(sp)>2 and sp[3]=='jpg':
			new=sp[0]+sp[1]+sp[2]+".jpg"
			print("\t" + filename + " -> " + new)
			os.rename(filename, new)

if __name__ == '__main__':
	lv2grename()