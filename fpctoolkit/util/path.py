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
	def copy(path_src, path_dest):
		path_src = Path.clean(path_src)
		path_dest = Path.clean(path_dest)

		if os.path.isdir(path_src):
			shutil.copytree(path_src, path_dest)
		else:
			shutil.copy(path_src, path_dest)

	@staticmethod
	def move(path_src, path_dest):
		path_src = Path.clean(path_src)
		path_dest = Path.clean(path_dest)

		shutil.move(path_src, path_dest)

	@staticmethod
	def is_empty(path):
		return os.listdir(path) == []

	@staticmethod
	def get_list_of_files_at_path(path):
		return [file for file in os.listdir(path) if os.path.isfile(Path.join(path,file))]

	@staticmethod
	def get_list_of_directories_at_path(path):
		return [file for file in os.listdir(path) if os.path.isdir(Path.join(path,file))]

	@staticmethod
	def get_case_insensitive_file_name(path, file_string):
		"""Looks at files in path, if one matches file_string in all aspects except case,
		return this file (first one for which this is true). If no file, return None
		"""

		files = Path.get_list_of_files_at_path(path)

		for file_name in files:
			if file_name.upper() == file_string.upper():
				return file_name

	@staticmethod
	def all_files_are_present(path, file_basenames_list):
		"""Returns true if every file in the list is present at path"""
		files_present = Path.get_list_of_files_at_path(path)

		for required_file in file_basenames_list:
			if required_file not in files_present:
				return False

		return True

	@staticmethod
	def get_all_directory_basenames_containing_string(path, sub_string):
		"""Returns directory basenames containing sub_string at path"""

		directory_basenames = Path.get_list_of_directories_at_path(path)

		directories_containing_string_list = []

		for directory_basename in directory_basenames:
			if directory_basename.find(sub_string) != 

