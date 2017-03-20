#import fpctoolkit.util.basic_validators as basic_validators



def validate_real_number(should_be_a_real_number):
	"""
	Raises an exception if should_be_a_real_number represents anything other than a real number.
	"""

	if isinstance(should_be_a_real_number, bool) or (not isinstance(should_be_a_real_number, (int, long, float))):
		raise Exception("Input argument is not a real number. Type is", type(should_be_a_real_number), "value is ", should_be_a_real_number)

def validate_first_real_number_is_strictly_less_than_or_equal_to_second(real_number_1, real_number_2):
	"""
	Raises an exception if either values are not real numbers or if real_number_1 > real_number_2.
	"""
	validate_real_number(real_number_1)
	validate_real_number(real_number_2)

	if real_number_1 > real_number_2:
		raise Exception("First value should be less than or equal to second. First value is", real_number_1, "and second value is", real_number_2)