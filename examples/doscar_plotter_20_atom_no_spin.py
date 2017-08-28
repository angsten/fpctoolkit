import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from fpctoolkit.io.file import File
import fpctoolkit.util.string_util as su

file_path = 'C:\Users\Tom\Desktop/20at_dos'
file = File(file_path)


num_atoms = 20


def get_floats_list_from_string(line):
	return [float(x) for x in su.remove_extra_spaces(line.strip()).split(' ')]

# print file

tag_line = file[5]
fermi_energy = get_floats_list_from_string(tag_line)[3]

print "Fermi energy: " + str(fermi_energy)


section_indices = []

for i, line in enumerate(file):
	if line == tag_line:
		section_indices.append(i)
		

data_series = []
		
for i in range(len(section_indices)):

	start_index = section_indices[i]

	if i == (len(section_indices) - 1):
		end_index = len(file)
	else:
		end_index = section_indices[i+1]

	new_data_set = []

	for j in range(start_index+1, end_index):
		new_data_set.append(get_floats_list_from_string(file[j]))

	data_series.append(new_data_set)

energies_list = [x[0]-fermi_energy for x in data_series[0]]



total_dos = []

#get total dos
if len(data_series[0][0]) == 3: #no spin, columns are energy dos integrated dos

	for data in data_series[0]:
		dos_value = data[1]

		total_dos.append(dos_value)


pdos = [] #each index corresponds to the associated atom in the poscar, a set of dictionaries with keys like 's_up' or just 's' and values as lists of dos vals

#get projected dos sets
if len(data_series[1][0]) == 4: #no spin, columns are energy s p d, one set for each atom

	for i in range(num_atoms):
		new_pdos = {'s': [], 'p': [], 'd': []}

		for data in data_series[i+1]:
			new_pdos['s'].append(data[1])
			new_pdos['p'].append(data[2])
			new_pdos['d'].append(data[3])

		pdos.append(new_pdos)


vd_lists = [pd['d'] for pd in pdos[4:8]]
vd_sum = map(sum, zip(*vd_lists))

O1p_lists = [pd['p'] for pd in pdos[8:12]]
O1p_sum = map(sum, zip(*O1p_lists))

O2p_lists = [pd['p'] for pd in pdos[16:20]]
O2p_sum = map(sum, zip(*O2p_lists))



energy_min = -5
energy_max = 8
state_count_max = 100

title = 'KVO3 (20-atom Pcmb) LDA No Spin Polarization 600eV encut 16x16x8M Kpoints'
labels = ['Total', 'V d-states', 'O1 p-states', 'O2 p-states']

# plt.suptitle('DOS')

# plt.plot(energies_list, total_dos, 'black', linewidth=2.0)

figure, sub_plots = plt.subplots(4, sharex=True)
figure.set_size_inches(12, 9, forward=True)

sub_plots[0].plot(energies_list, total_dos, 'black', linewidth=2.0)
# sub_plots[0].set_title('Total DOS')
sub_plots[0].axis([energy_min, energy_max, 0, state_count_max])

sub_plots[1].plot(energies_list, vd_sum, 'black', linewidth=2.0)

sub_plots[2].plot(energies_list, O1p_sum, 'black', linewidth=2.0)
sub_plots[3].plot(energies_list, O2p_sum, 'black', linewidth=2.0)


sub_plots[-1].set_xlabel('Energy (eV)', fontsize=18)
figure.text(0.04, 0.5, 'Density of States (states/eV*cell)', fontsize=18, va='center', rotation='vertical')

figure.subplots_adjust(hspace=0)

for i, plot in enumerate(sub_plots):
	for tick in plot.xaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	for tick in plot.yaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	plot.xaxis.set_tick_params(width=1.25, length=5) #set tick length and width
	plot.yaxis.set_tick_params(width=1.25, length=5)
	[spine.set_linewidth(1.5) for spine in plot.spines.itervalues()] #set border width

	plot.yaxis.get_major_ticks()[-1].set_visible(False)
	plot.axvline(x=0.0, color='r', linestyle='--')

	plot.text(0.88, 0.85, labels[i], verticalalignment='top', horizontalalignment='center', transform=plot.transAxes, color='black', fontsize=16)



# plt.savefig(pp, format='pdf')

figure.set_figwidth(8)
figure.set_figheight(8)
figure.patch.set_facecolor('white')
figure.text(0.5, 0.94, title, fontsize=16, ha='center')

plt.show()

# plt.clf()


