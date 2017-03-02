import random



class RandomSelector(object):
	"""
	Takes in list of fractional numbers representing probabilities (must add to one)

	returns randomly selected case index (which of the probabilities occurred)

	"""

	def __init__(self, probabilities_list):
		if not (sum(probabilities_list) - 1.0) < 0.000000000001:
			raise Exception("List of probabilities does not sum to one")

		self.probabilities_list = probabilities_list


	def get_event_index(self):

		accumulations_list = []

		for i in range(len(self.probabilities_list)):
			accumulations_list.append(sum(self.probabilities_list[0:i+1]))			

		random_number = random.uniform(0.0, 1.0)

		index = 0
		while random_number > accumulations_list[index]:
			index += 1

		return index