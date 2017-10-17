import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from matplotlib.backends.backend_pdf import PdfPages

import sys

from fpctoolkit.io.file import File


plt.rcParams['axes.linewidth'] = 3.0

tick_size = 9
tick_width = 3.0
label_size = 17

plt.rcParams['xtick.major.size'] = tick_size
plt.rcParams['xtick.major.width'] = tick_width
plt.rcParams['xtick.minor.size'] = tick_size*0.6
plt.rcParams['xtick.minor.width'] = tick_width*0.75
plt.rcParams['xtick.labelsize'] = label_size

plt.rcParams['ytick.major.size'] = plt.rcParams['xtick.major.size']
plt.rcParams['ytick.major.width'] = plt.rcParams['xtick.major.width']
plt.rcParams['ytick.minor.size'] = plt.rcParams['xtick.minor.size']
plt.rcParams['ytick.minor.width'] = plt.rcParams['xtick.minor.width']
plt.rcParams['ytick.labelsize'] = plt.rcParams['xtick.labelsize']



j = 0

def get_plot(file_lines, header_data, out_dict, j):
	x_data = []
	y_data = []

	title_string = header_data[0] + ' ' + header_data[1]
	right_title_string = header_data[2] + ' ' + header_data[3] + ' ' + header_data[4]

	labels_line = file_lines[0]

	x_label_string = labels_line.split(' ')[0]
	y_label_string = labels_line.split(' ')[1]

	for i in range(1, len(file_lines)):
		line = file_lines[i].strip()

		if j == 3:
			ref_energy = 0
		else:
			ref_energy = -353.47406

		x_data.append(float(line.split(' ')[0]))
		y_data.append(float(line.split(' ')[1])-ref_energy)

	

	# ax = plt.gca()
	# ax.get_yaxis().get_major_formatter().set_scientific(True)

	# plt.title(right_title_string, loc='right', size=8)
	# plt.title(title_string)



	if x_label_string in ['e_4', 'e_5'] or (x_label_string == 'e_3' and y_label_string[0] == 'd'):
		order = 2
	else:
		order = 4

	fitting_parameters = np.polyfit(x_data, y_data, order)

	if order == 2:
		if y_label_string == 'Energy':
			fitting_parameters[1] = 0.0

		f = lambda x: fitting_parameters[0]*x**2.0 + fitting_parameters[1]*x + fitting_parameters[2]

	elif order == 4:
		# if x_label_string in ['e_3']:
		# 	fitting_parameters[3] = 0.0

		f = lambda x: fitting_parameters[0]*x**4.0 + fitting_parameters[1]*x**3.0 + fitting_parameters[2]*x**2.0 + fitting_parameters[3]*x + fitting_parameters[4]

	fit_x_data = []

	start_x = min(x_data)
	end_x = max(x_data)
	step = (max(x_data)-min(x_data))/1000.0

	x = start_x
	while x <= end_x:
		fit_x_data.append(x)
		x += step

	fit_y_data = [f(x) for x in fit_x_data]


	# fit_string = get_fit_string(fitting_parameters)

	# plt.suptitle(fit_string)

	plt.minorticks_on()

	ax = plt.axes()
	ax.tick_params(pad=8)

	lab_font_size = 20

	if j == 1:
		plt.axis([-1.3, 1.3, -0.072, 0.032])
		
		ax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
		ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))
		ax.yaxis.set_major_locator(ticker.MultipleLocator(0.02))
		ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.01))

		ax.text(0.0, -0.09, '$u_{1}$ ($\AA$)', size=34, horizontalalignment='center')
		ax.text(-1.75, -0.02, '$\Delta$E  (eV)', verticalalignment='center', rotation='vertical', fontsize=28)
	elif j == 2:
		plt.axis([-0.08, 0.08, -0.3, 4.3])
		
		ax.xaxis.set_major_locator(ticker.MultipleLocator(0.02))
		ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.01))
		ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
		ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))

		ax.text(0.0, -1.0, '$\epsilon_{zz}$', size=38, horizontalalignment='center')
		ax.text(-0.1, 2.0, '$\Delta$E  (eV)', verticalalignment='center', rotation='vertical', fontsize=28)
	elif j == 3:
		plt.axis([-0.017, 0.017, -0.69, -0.32])
		
		ax.xaxis.set_major_locator(ticker.MultipleLocator(0.005))
		ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.0025))
		ax.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
		ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.025))

		ax.text(0.0, -0.77, '$\epsilon_{zz}$', size=38, horizontalalignment='center')
		# ax.text(-0.015, -0.6, '$\frac{1}{2}  (eV)', verticalalignment='center', rotation='vertical', fontsize=28)

	plt.plot(x_data, y_data, 'o', c='black', markersize=9)
	plt.plot(fit_x_data, fit_y_data, c='black', linewidth=2.5)
	

	fig = plt.gcf()
	fig.set_size_inches(10, 6)

	plt.savefig('C:\\Users\\Tom\\Documents\\Berkeley\\research\my_papers\\Epitaxial Phase Validation Paper\\Paper\\rough_figures\\fig_fits_stuff\\plot' + str(j) + '.eps', format='eps', dpi=1000, bbox_inches='tight')



	# plt.show()

	if j == 3:
		plt.show()
		sys.exit()

	plt.clf()
		


	rnd = 2
	if x_label_string[0] == 'u':
		ulbl = x_label_string[2]

		if len(x_label_string) > 3:
			ulbl += x_label_string[3]

		print 'u' + ulbl + 'o2 = ' + str(round(fitting_parameters[2], rnd)) + ';'
		print 'u' + ulbl + 'o4 = ' + str(round(fitting_parameters[0], rnd)) + ';'

		out_dict['u' + ulbl + 'o2'] = str(round(fitting_parameters[2], rnd))
		out_dict['u' + ulbl + 'o4'] = str(round(fitting_parameters[0], rnd))		
	elif x_label_string[0] == 'e':
		if y_label_string == 'Energy':
			if x_label_string[2] == '3':
				print 'e' + x_label_string[2] + 'o2 = ' + str(round(fitting_parameters[2], rnd)) + ';'
				print 'e' + x_label_string[2] + 'o3 = ' + str(round(fitting_parameters[1], rnd)) + ';'
				print 'e' + x_label_string[2] + 'o4 = ' + str(round(fitting_parameters[0], rnd)) + ';'

				out_dict['e' + x_label_string[2] + 'o2'] = str(round(fitting_parameters[2], rnd))
				out_dict['e' + x_label_string[2] + 'o3'] = str(round(fitting_parameters[1], rnd))
				out_dict['e' + x_label_string[2] + 'o4'] = str(round(fitting_parameters[0], rnd))
	
			else:
				print 'e' + x_label_string[2] + 'o2 = ' + str(round(fitting_parameters[0], rnd)) + ';'
				out_dict['e' + x_label_string[2] + 'o2'] = str(round(fitting_parameters[0], rnd))
		else:
			if y_label_string[-3] == '_':
				ulbl = y_label_string[-2:]
			else:
				ulbl = y_label_string[-1]


			print 'e' + x_label_string[2] + 'u' + ulbl + 'o2 = ' + str(round(fitting_parameters[1], rnd)) + ';'
			out_dict['e' + x_label_string[2] + 'u' + ulbl + 'o2'] = str(round(fitting_parameters[1]*0.5, rnd))

	

def get_fit_string(fitting_parameters):

	fit_string = ''

	order = len(fitting_parameters) - 1

	for index in range(order+1):
		exp = order-index

		if exp > 1:
			exp_string = "*x^" + str(exp)
		elif exp == 1:
			exp_string = "*x"
		else:
			exp_string = ""


		fit_string += str(round(fitting_parameters[index], 3)) + exp_string + " + "


	return fit_string[:-2]





data_file = File("C:/Users/Tom/Documents/Berkeley/research/scripts/fpctoolkit/data/derivative_plot_data_pretty")

header_line = data_file[0]
header_data = header_line.split(' ') #SrTiO3 a=3.79 encut=600eV kpoints=3x3x3M disp_step=0.01A u2 Energy



pp = PdfPages('C:\Users\Tom\Desktop\derivative_fits/' + header_data[0] + "/" + header_data[1] + '.pdf')


start_index = 1
end_index = None

out_dict = {}

j = 1

for i, line in enumerate(data_file):

	if line.strip() == '':
		end_index = i



		get_plot(data_file[start_index:end_index], header_data, out_dict, j)
		j += 1

		start_index = end_index+1


pp.close()

sep = ' & '

keys = ['e3o2', 'e3o3', 'e3o4']

for i in range(1, 10):
	# keys.append('u' + str(i) + 'o2')
	keys.append('u' + str(i) + 'o4')

for i in range(1, 10):
	keys.append('e3u' + str(i) + 'o2')

outstr = ''
for key in keys:
	try:
		outstr += sep + out_dict[key]
	except KeyError as e:
		outstr += sep + '*'

print outstr + ' \\\\'



#& $\epsilon_3u^2_1$ & $\epsilon_3u^2_2$ & $\epsilon_3u^2_3$ & $\epsilon_3u^2_4$ & $\epsilon_3u^2_5$ & $\epsilon_3u^2_6$ & $\epsilon_3u^2_7$ & $\epsilon_3u^2_8$  \\ \hline
#-0.02 & 516 & -1726 & 4875 & 179 & 179 & -.88 & 7.4 & -.55 & .26 & -.34 & .24 & -.23 & .25 & -.23 & .25 & * & * & * & * & * & * & -175 & -8.7 & -13.4 & 9.7 & 9.8 & * & * & * \\