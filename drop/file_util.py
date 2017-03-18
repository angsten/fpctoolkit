import copy

import fpctoolkit.io.file

"""
Functions in this file operate on files as auxiliary methods.
"""
# File = fpctoolkit.io.file.File()

# def get_lines_containing_string(file, string):
# 	lines = []
# 	for line in file.lines:
# 		if not line.find(string) == -1:
# 			lines.append(line)
# 	return lines

# def standardize_newlines(file, newline_char):
# 	for line in file:
# 		line = line.replace('\r\n',newline_char)

# def pad_with_newline(file):
# 	if file.lines:
# 		file[-1] = file[-1].rstrip('\n') + '\n'
# 	return file

# def concatenate(*files):
# 	concatenated_file = fpctoolkit.io.file.File()
# 	for file in files:
# 		file_copy = pad_with_newline(copy.deepcopy(file))
# 		concatenated_file.lines += file_copy.lines

# 	return concatenated_file