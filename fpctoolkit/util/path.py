import os
import shutil

import fpctoolkit.util.string_util as su

class Path(object):
	@staticmethod
	def expand_path(path):
		return os.path.abspath(os.path.expanduser(path))

	@staticmethod
	def join(*args):
		return Path.clean(*args)

	@staticmethod
	def clean(*paths):
		return Path.expand_path(os.path.join(*paths))

	@staticmethod
	def exists(path):
		return os.path.exists(path)

	@staticmethod
	def make(path):
		path = Path.clean(path)
		if not Path.exists(path):
			os.mkdir(path)

	@staticmethod
	def remove(path):
		path = Path.clean(path)

		if path == Path.clean("~"):
			raise Exception("Cannot remove entire home directory")

		if os.environ['QUEUE_ADAPTER_HOST'] == 'Tom_hp': #Don't want to destroy my home computer files
			if Path.exists(path):
				move_path = Path.clean("C:\Users\Tom\Documents\Coding\python_work/fpc_recycle_bin/", os.path.basename(path)+'_'+ su.get_time_stamp_string())
				shutil.move(path, move_path)
			return

		if Path.exists(path):
			if os.path.isfile(path):
				os.remove(path)
			elif os.path.isdir(path):
				shutil.rmtree(path)

	@staticmethod
	def is_empty(path):
		return os.listdir(path) == []

	@staticmethod
	def get_list_of_files_at_path(path):
		return [file for file in os.listdir(path) if os.path.isfile(Path.join(path,file))]

	@staticmethod
	def get_case_insensitive_file_name(path, file_string):
		"""Looks at files in path, if one matches file_string in all aspects except case,
		return this file (first one for which this is true). If no file, return None
		"""

		files = Path.get_list_of_files_at_path(path)

		for file_name in files:
			if file_name.upper() == file_string.upper():
				return file_name