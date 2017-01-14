

"""
Functions in this file operate on strings as auxiliary methods.
"""

# def contains(string,substring):
# 	if not string.find(substring) == -1:
# 		return True

def enforce_newline(string):
	return string.rstrip('\n')+'\n'

def enforce_newline_on_list(strings_list):
		result = [enforce_newline(x) for x in strings_list]
		return result

