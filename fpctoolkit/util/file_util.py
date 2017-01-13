

from fpctoolkit.io.file import File

"""
Functions in this file operate on files as auxiliary methods.
"""


def get_lines_containing_string(file,string):
	lines = []
	for line in file.lines:
		if not line.find(string) == -1:
			lines.append(line)
	return lines

def concatenate(*files):
	concatenated_file = File()
	for file in files:
		concatenated_file.lines += file.lines
		if len(concatenated_file.lines) > 0:
			concatenated_file.lines[-1] = concatenated_file.lines[-1].rstrip() + '\n' #make sure eof has a return

	return concatenated_file