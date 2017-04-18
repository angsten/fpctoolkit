#import fpctoolkit.util.basic_validators as basic_validators

import fpctoolkit.util.basic_checks as basic_checks


def validate_index_tuple(index_tuple, array_shape):

	validate_tuple_of_positive_or_zero_integers(index_tuple)
	validate_tuple_of_positive_nonzero_integers(array_shape)

	if not len(index_tuple) == len(array_shape):
		raise Exception("Index tuple is not valid for the given array shape. The dimension of the array", len(array_shape), "and the number of indicies in the tuple", len(index_tuple), "do not match.")

	for i, index in enumerate(index_tuple):
		validate_sequence_index(index, array_shape[i])


def validate_tuple_of_positive_nonzero_integers(should_be_tuple_of_positive_nonzero_integers):
	"""
	Empty tuple is okay.
	"""

	validate_tuple(should_be_tuple_of_positive_nonzero_integers)

	for should_be_a_positive_nonzero_integer in should_be_tuple_of_positive_nonzero_integers:
		validate_positive_nonzero_integer(should_be_a_positive_nonzero_integer)


def validate_tuple_of_positive_or_zero_integers(should_be_tuple_of_positive_or_zero_integers):
	"""
	Empty tuple is okay.
	"""

	validate_tuple(should_be_tuple_of_positive_or_zero_integers)

	for should_be_a_positive_or_zero_integer in should_be_tuple_of_positive_or_zero_integers:
		validate_positive_or_zero_integer(should_be_a_positive_or_zero_integer)


def validate_tuple(should_be_a_tuple):
	if not isinstance(should_be_a_tuple, tuple):
		raise Exception("Input argument is not a tuple")


def validate_sequence_index(sequence_index_integer, sequence_length):
	"""
	Raises an exception if sequence_index_integer or sequence_length is not of type integer or is greater than or equal to sequence_length.
	"""

	validate_positive_or_zero_integer(sequence_index_integer)
	validate_positive_or_zero_integer(sequence_length)

	validate_first_real_number_is_strictly_less_than_or_equal_to_second(sequence_index_integer, sequence_length-1)

def validate_real_number_is_in_range(real_number_that_should_be_in_range, minimum_real_number, maximum_real_number, minimum_inclusive=True, maximum_inclusive=True):
	"""
	Raises an exception if real_number_that_should_be_in_range is not in (minimum_real_number, maximum_real_number) 
	if inclusive == False or [minimum_real_number, maximum_real_number] if inclusive == True.
	"""

	validate_real_number(real_number_that_should_be_in_range)
	validate_real_number(minimum_real_number)
	validate_real_number(maximum_real_number)
	validate_boolean(minimum_inclusive)
	validate_boolean(maximum_inclusive)

	inclusive_min_tag = '[' if minimum_inclusive else '('
	inclusive_max_tag = ']' if maximum_inclusive else ')'

	exception = Exception("Input argument is not within the specified range of " + inclusive_min_tag + str(minimum_real_number) + ", " + str(maximum_real_number) + " Value is" + str(real_number_that_should_be_in_range))

	if minimum_inclusive:
		if real_number_that_should_be_in_range < minimum_real_number:
			raise exception
	elif not minimum_inclusive:
		if real_number_that_should_be_in_range <= minimum_real_number:
			raise exception

	if maximum_inclusive:
		if real_number_that_should_be_in_range > maximum_real_number:
			raise exception
	elif not maximum_inclusive:
		if real_number_that_should_be_in_range >= maximum_real_number:
			raise exception
		


def validate_boolean(should_be_a_boolean):

	if not isinstance(should_be_a_boolean, bool):
		raise Exception("Input argument should be of boolean type. Type is", type(should_be_a_boolean))

def validate_integer(should_be_an_integer):
	"""
	Raises an exception if should_be_an_integer is not a non-boolean representation of an integer (int or long).
	"""

	if not basic_checks.is_an_integer(should_be_an_integer):
		raise Exception("Input argument is not an integer. Type is", type(should_be_an_integer), "value is ", should_be_an_integer)

def validate_real_number_is_positive_or_zero(should_be_positive_or_zero):
	"""
	Raises an exception if should_be_positive_or_zero is < 0.
	"""
	validate_real_number(should_be_positive_or_zero)

	if not (should_be_positive_or_zero >= 0):
		raise Exception("Input argument should be positive or zero. Value is", should_be_positive_or_zero)

def validate_real_number_is_positive_nonzero(should_be_positive):
	"""
	Raises an exception if should_be_positive is <= 0.
	"""
	validate_real_number(should_be_positive)

	if not (should_be_positive > 0):
		raise Exception("Input argument should be positive. Value is", should_be_positive)


def validate_positive_nonzero_integer(should_be_a_positive_nonzero_integer):
	"""
	Raises an exception if should_be_a_positive_nonzero_integer is not a positive nonzero integer.
	"""

	validate_integer(should_be_a_positive_nonzero_integer)
	validate_real_number_is_positive_nonzero(should_be_a_positive_nonzero_integer)


def validate_positive_or_zero_integer(should_be_a_positive_or_zero_integer):
	"""
	Raises an exception if should_be_a_positive_or_zero_integer is not a positive integer or 0.
	"""

	validate_integer(should_be_a_positive_or_zero_integer)
	validate_real_number_is_positive_or_zero(should_be_a_positive_or_zero_integer)



def validate_real_number(should_be_a_real_number):
	"""
	Raises an exception if should_be_a_real_number represents anything other than a real number.
	"""

	if not basic_checks.is_a_real_number(should_be_a_real_number):
		raise Exception("Input argument is not a real number. Type is", type(should_be_a_real_number), "value is ", should_be_a_real_number)

def validate_first_real_number_is_strictly_less_than_or_equal_to_second(real_number_1, real_number_2):
	"""
	Raises an exception if either values are not real numbers or if real_number_1 > real_number_2.
	"""
	validate_real_number(real_number_1)
	validate_real_number(real_number_2)

	if real_number_1 > real_number_2:
		raise Exception("First value should be less than or equal to second. First value is", real_number_1, "and second value is", real_number_2)

def validate_approximately_equal(number_1, number_2, tolerance=0.000001):
	"""
	Throws exception if number_1 is not within tolerance of number_2
	"""

	validate_real_number(number_1)
	validate_real_number(number_2)
	validate_real_number(tolerance)

	if abs(number_1-number_2) > tolerance:
		raise Exception("Two numbers are not approximately equal. Values are:,", number_1, number_2)