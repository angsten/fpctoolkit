#import fpctoolkit.util.misc as misc

import random


"""
Miscellaneous functions.
"""

def get_list_of_unique_random_integers(length, min_integer, max_integer):
	"""
	Returns a list of random integers in range [min_integer, max_integer] (inclusive) with a list length of length.
	"""

	if length < 0:
		raise Exception("Cannot return a list of negative length")

	if min_integer > max_integer:
		raise Exception("min_integer should be less than or equal to max_integer")

	if ( (max_integer - min_integer) + 1) < length:
		raise Exception("Cannot return a list of unique integers with the given length and range.")

	random_integers_list = []

	for i in range(length):
		while(True):
			random_integer = random.randint(min_integer, max_integer)

			if random_integer not in random_integers_list:
				random_integers_list.append(random_integer)
				break

	return random_integers_list

def flatten_multi_dimensional_list(multi_dimensional_list):
	"""
	Returns a flattened version of any dimensional list of lists of lists...

	[[2, 3, 4], [5, 6, 7]] -> [2, 3, 4, 5, 6, 7]
	"""

	return [item for sublist in multi_dimensional_list for item in sublist]

