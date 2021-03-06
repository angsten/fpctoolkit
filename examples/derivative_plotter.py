import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


from fpctoolkit.io.file import File





def get_plot(file_lines, header_data, out_dict):
	x_data = []
	y_data = []

	title_string = header_data[0] + ' ' + header_data[1]
	right_title_string = header_data[2] + ' ' + header_data[3] + ' ' + header_data[4]

	labels_line = file_lines[0]

	x_label_string = labels_line.split(' ')[0]
	y_label_string = labels_line.split(' ')[1]

	for i in range(1, len(file_lines)):
		line = file_lines[i].strip()

		x_data.append(float(line.split(' ')[0]))
		y_data.append(float(line.split(' ')[1]))

	

	# ax = plt.gca()
	# ax.get_yaxis().get_major_formatter().set_scientific(True)

	plt.title(right_title_string, loc='right', size=8)
	plt.title(title_string)

	plt.xlabel(x_label_string, size=16)
	plt.ylabel(y_label_string, size=16)

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
		if x_label_string in ['e_3']:
			fitting_parameters[3] = 0.0

		f = lambda x: fitting_parameters[0]*x**4.0 + fitting_parameters[1]*x**3.0 + fitting_parameters[2]*x**2.0 + fitting_parameters[3]*x + fitting_parameters[4]

	fit_x_data = []

	start_x = min(x_data)
	end_x = max(x_data)
	step = (max(x_data)-min(x_data))/500.0

	x = start_x
	while x <= end_x:
		fit_x_data.append(x)
		x += step

	fit_y_data = [f(x) for x in fit_x_data]


	fit_string = get_fit_string(fitting_parameters)
	plt.suptitle(fit_string)

	plt.plot(x_data, y_data, 'ro')
	plt.plot(fit_x_data, fit_y_data)

	plt.savefig(pp, format='pdf')

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

	# plt.show()

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





data_file = File("C:/Users/Tom/Documents/Berkeley/research/scripts/fpctoolkit/data/derivative_plot_data")

header_line = data_file[0]
header_data = header_line.split(' ') #SrTiO3 a=3.79 encut=600eV kpoints=3x3x3M disp_step=0.01A u2 Energy



pp = PdfPages('C:\Users\Tom\Desktop\derivative_fits/' + header_data[0] + "/" + header_data[1] + '.pdf')


start_index = 1
end_index = None

out_dict = {}

for i, line in enumerate(data_file):

	if line.strip() == '':
		end_index = i



		get_plot(data_file[start_index:end_index], header_data, out_dict)

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