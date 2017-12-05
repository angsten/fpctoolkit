#from fpctoolkit.io.vasp.vasp_xml import VaspXML

import numpy as np

from fpctoolkit.io.file import File
import fpctoolkit.util.string_util as su
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.structure_analyzer import StructureAnalyzer

import xml.etree.ElementTree as ET



class VaspXML(object):
	
	def __init__(self, xml_file_path):

		self.tree = ET.parse(xml_file_path)

		root = self.tree.getroot()

		self.atom_types = []
		
		for arr in root.find('atominfo'):
			if arr.attrib.has_key('name') and arr.attrib['name'] == 'atoms':

				for atoms in arr.find('set'):
					for atom in atoms:
						if not su.string_represents_integer(atom.text):
							self.atom_types.append(atom.text.strip())

		self.positions = []
		self.lattices = []
		self.forces = []

		#get forces and atom positions
		for calculation in root.findall('calculation'):

			for structure in calculation.findall('structure'):

				for v in structure.find('crystal'):
					if v.attrib.has_key('name') and v.attrib['name'] == 'basis':
						self.lattices.append([su.get_number_list_from_string(v[i].text) for i in range(len(v))])

				for v in structure.findall('varray'):

					if v.attrib.has_key('name') and v.attrib['name'] == 'positions':
						self.positions.append([su.get_number_list_from_string(v[i].text) for i in range(len(v))])

			for v in calculation:

				if v.attrib.has_key('name') and v.attrib['name'] == 'forces':
					
					self.forces.append([su.get_number_list_from_string(v[i].text) for i in range(len(v))])


		#make the list of structures, one for each ionic step
		self.structures = []

		num_ionic_steps = len(self.positions)
		num_atoms = len(self.atom_types)

		if len(self.lattices) != num_ionic_steps or len(self.forces) != num_ionic_steps:
			raise Exception("Inconsistent number of data.")

		for i in range(num_ionic_steps):

			sites = []

			if len(self.positions[i]) != num_atoms or len(self.forces[i]) != num_atoms:
				raise Exception("Not a consistent atom count in data.")


			for j in range(num_atoms):
				site = Site({'position': self.positions[i][j], 'coordinate_mode': 'Direct', 'type': self.atom_types[j], 'force': self.forces[i][j]}) ##########Assumes direct coords!!!!

				sites.append(site)

			self.structures.append(Structure(lattice=self.lattices[i], sites=SiteCollection(sites)))




# num_neighbors = 140

# vxml = VaspXML('C:/Users/Tom/Desktop/cu_force_256.xml')


# output = File()

# xml_structures = vxml.structures


# count = 0
# for structure in xml_structures:
# 	count += 1

# 	print "Structure count is " + str(count) + " out of " + str(len(xml_structures))

# 	samples = StructureAnalyzer.get_force_potential_samples(structure=structure, N_max=1, cutoff_fraction=0.9)

# 	for sample in samples:
# 		output += " ".join([str(round(x, 5)) for x in sample[0:num_neighbors*3+3]])

# output.write_to_path('C:/Users/Tom/Desktop/out.txt')