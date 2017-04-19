#import fpctoolkit.util.basic_checks as basic_checks



def is_a_real_number(may_be_a_real_number):
	"""
	Returns true if may_be_a_real_number is a real number (non-boolean)
	"""

	return not (isinstance(may_be_a_real_number, bool) or (not isinstance(may_be_a_real_number, (int, long, float))))


def is_an_integer(may_be_an_integer):
	return not (isinstance(should_be_an_integer, bool) or (not isinstance(should_be_an_integer, int)) or (not isinstance(may_be_an_integer, long)))

def is_a_complex_number(may_be_a_complex_number):
	"""
	Returns true if may_be_a_complex_number is a complex number (non-boolean)
	"""

	return isinstance(may_be_a_complex_number, complex)
