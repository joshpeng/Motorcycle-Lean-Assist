'''
Splits training data into a 85-15 train-test split.

Takes into account that each image has 91 variants and moves all of them together.
This prevents potential "cheating" in the training.
'''

import shutil
import glob


train_test_split = 0.15
n_files = 833
split = int(train_test_split * n_files)

with open("dataset_list.txt") as myfile:
	base = [next(myfile)[:-5] for x in xrange(split)]

dst = "../test"
for f in base:
	name = "../train/" + f + "*.jpg"
	print name
	for file in glob.glob(name):
		shutil.move(file, dst)