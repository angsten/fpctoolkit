

"""
Functions in this file operate on strings as auxiliary methods.
"""

# def contains(string,substring):
# 	if not string.find(substring) == -1:
# 		return True

#if string ends with \n or \r\n return one of these, else return empty string
# def get_string_return_char(string):
# 	if len(string) == 0:
# 		return ''
# 	elif string[-1:] == '\n':
# 		return '\n'
# 	elif string[-2:] == '\r\n':
# 		return '\r\n'

def enforce_newline(string):
	return string.rstrip('\n')+'\n'

def enforce_newline_on_list(strings_list):
		result = [enforce_newline(x) for x in strings_list]
		return result

