

"""
Functions in this file operate on strings as auxiliary methods.
"""

# def contains(string,substring):
# 	if not string.find(substring) == -1:
# 		return True

def remove_extra_spaces(string): #' hello    yo  u' => ' hello yo u'
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