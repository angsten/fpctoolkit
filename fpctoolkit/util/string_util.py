from datetime import datetime

"""
Functions in this file operate on strings as auxiliary methods.
"""

# def contains(string,substring):
# 	if not string.find(substring) == -1:
# 		return True

def remove_extra_spaces(string): 
	"""
	' hello    yo  u' => ' hello yo u'
	"""
	return " ".join(string.split())


def string_represents_integer(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

def string_represents_float(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def get_time_stamp_string():
	"""Safe for file usage"""
	
	return str(datetime.now()).replace('.', '_').replace(':', '_').replace('-', '_')


def get_number_list_from_string(string_of_numbers):
	"""
	Takes a string filled with numbers separated by spaces and returns a list of those numbers:

	"1.3   4.3       5.3\n" returns [1.3, 4.3, 5.3]

	"1.4a   4.3jjj" gives an error - no non-numeric characters allowed
	"""

	string_of_numbers = string_of_numbers.strip()

	string_of_numbers = remove_extra_spaces(string_of_numbers)

	number_strings_list = string_of_numbers.split(' ')

	number_list = []

	for number_string in number_strings_list:
		if string_represents_integer(number_string):
			number_list.append(int(number_string))
		elif string_represents_float(number_string):
			number_list.append(float(number_string))
		else:
			raise Exception("Cannot coerce string to list of numbers - a non-numerical component exists. String is ", string_of_numbers)

	return number_list


