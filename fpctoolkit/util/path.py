#from fpctoolkit.util.path import Path

import os
import shutil

import fpctoolkit.util.string_util as su

class Path(object):
	@staticmethod
	def expand(path):
		"""
		Returns absolute and expanded path. Setting path='~/bin' will return /home/angsten/bin   path='../bin' will return /home/angsten/bin
		"""
		return os.path.abspath(os.path.expanduser(path))

	@staticmethod
	def join(*args):
		return Path.clean(*args) #* is splat - takes from list and makes into comma separated args for a function

	@staticmethod
	def clean(*paths):
		return Path.expand(os.path.join(*paths))

	@staticmethod
	def exists(path):
		if path == None:
			return False

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
	def split_into_components(path):
		"""
		Returns list of componenents making up path:
		Path.split_into_components('/home/angsten/bin/') = ['home', 'angsten', 'bin']
		Path.split_into_components('/home/angsten/bin') = ['home', 'angsten', 'bin']
		Path.split_into_components('/') = []
		Path.split_into_components('') = []
		Path.split_into_components('random_string') = []
		Path.split_into_components('./angsten/ball/to') = ['.', 'angsten', 'ball', 'to']
		Path.split_into_components('../angsten/ball/to') = ['..', 'angsten', 'ball', 'to']

		**This function is ONLY compatible with unix operating systems.**
		"""

		path_components_list = []
		sub_path = path

		while sub_path not in ['', '/']:
			split_pair = os.path.split(sub_path)
			component_to_append = split_pair[1]

			if component_to_append != '':
				path_components_list.append(component_to_append)

			sub_path = split_pair[0]

		path_components_list.reverse()

		return path_components_list

	@staticmethod
	def get_list_of_files_at_path(path):
		return [file for file in os.listdir(path) if os.path.isfile(Path.join(path, file))]

	@staticmethod
	def get_list_of_file_paths_at_path(path):
		return [Path.join(path, file) for file in os.listdir(path) if os.path.isfile(Path.join(path, file))]

	@staticmethod
	def remove_all_files_at_path(path):
		for file_path in Path.get_list_of_file_paths_at_path(path):
			Path.remove(file_path)

	@staticmethod
	def get_list_of_directories_at_path(path):
		return [file for file in os.listdir(path) if os.path.isdir(Path.join(path, file))]

	@staticmethod
	def get_case_insensitive_file_name(path, file_string):
		"""
		Looks at files in path, if one matches file_string in all aspects except case,
		return this file (first one for which this is true). If no file, return None
		"""

		files = Path.get_list_of_files_at_path(path)

		for file_name in files:
			if file_name.upper() == file_string.upper():
				return file_name

	@staticmethod
	def all_files_are_present(path, file_basenames_list):
		"""
		Returns true if every file in the list is present at path
		"""

		files_present = Path.get_list_of_files_at_path(path)

		for required_file in file_basenames_list:
			if required_file not in files_present:
				return False

		return True

	@staticmethod
	def get_list_of_directory_basenames_containing_string(path, sub_string):
		"""
		Returns directory basenames containing sub_string at path
		"""

		directory_basenames = Path.get_list_of_directories_at_path(path)

		return [directory_basename for directory_basename in directory_basenames if directory_basename.find(sub_string) != -1]


	@staticmethod
	def get_containing_directory(path):
		"""
		If /home/angsten/bla is input, return value is /home/angsten
		If / is input, '' is returned
		"""

		path_components_list = Path.split_into_components(path)

		print "Components are", path_components_list
		print "splatted is", path_components_list[:-1]

		containing_directory = Path.join(*path_components_list[:-1])

		print "cont dir is", containing_directory

		return containing_directory


	@staticmethod
	def validate(path, allow_none=False, expand_path=True):
		"""
		Raises an exception if the path does not exist. 
		If allow_none is True, path can be None without raising an exception.
		If expand_path is True, the path is expanded before checking if it exists.
		"""

		exception = Exception("Path at", path, "does not exist.")

		if path == None:
			if not allow_none:
				raise exception
		else:
			if expand_path:
				path = Path.expand(path)

			if not Path.exists(path):
				raise exception


	@staticmethod
	def validate_does_not_exist(path, allow_none=False, expand_path=True):
		"""
		Raises an exception if the path exists. 
		If allow_none is True, path can be None without raising an exception.
		If expand_path is True, the path is expanded before checking if it exists.
		"""

		exception = Exception("Path at", path, "already exists.")

		if path == None:
			if not allow_none:
				raise Exception("Path cannot be None")
		else:
			if expand_path:
				path = Path.expand(path)

			if Path.exists(path):
				raise exception

	@staticmethod
	def validate_writeable(path, allow_none=False, expand_path=True):
		"""
		Raises an exception if the path cannot be written to because the containing directory is not defined. 
		If allow_none is True, path can be None without raising an exception.
		If expand_path is True, the path is expanded before checking if it exists.
		"""

		exception = Exception("Path at", path, "cannot be written to because the parent directory does not exist.")

		if path == None:
			if not allow_none:
				raise Exception("Path cannot be None")
		else:
			if expand_path:
				path = Path.expand(path)

			print "HYYYYYYYYYYYYYY"
			print "path is", path
			print Path.get_containing_directory(path)
			if not Path.exists(Path.get_containing_directory(path)):
				raise exception