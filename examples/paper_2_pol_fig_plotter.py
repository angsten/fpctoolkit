import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import sys
import matplotlib.ticker as ticker


misfit_strains_pol_en = np.arange(-4.0, 4.5, 0.5)
misfit_strains_eig = np.arange(-4, 5)


srti_dftenergydata = np.array([173.042, 130.206, 93.2761, 62.3573, 37.5297, 18.8065, 6.39428, 0.519511, 1.08218, 3.85182, 12.5049, 25.7351, 43.02, 63.8481, 87.7561, 114.364, 143.352])
cati_dftenergydata = np.array([115.502, 79.992, 50.6094, 27.5892, 11.5205, 2.47138, 0.340233, 4.99274, 16.3013, 32.6422, 52.3653, 76.2343, 103.783, 134.569, 168.105, 203.982, 241.67])
srhf_dftenergydata = np.array([121.037, 89.2625, 65.0318, 37.9393, 17.9565, 5.36332, 0.251091, 1.8786, 9.93387, 25.5892, 48.6987, 79.1408, 116.685, 161.117, 212.235, 269.777, 333.512])


srti_dftpoldata = np.abs(np.array([[0.,0.,0.308,0.308],[0.,0.,-0.270571,0.270571],[0.,0.,-0.23124,0.23124],[0.,0.,-0.188373,0.188373],[0.,0.,-0.137565,0.137565],[0.,0.,-0.0635332,0.0635332],[0.,0.,-0.000260026,0.000263689],[0.,0.,0.000194373,0.000197461],[-0.00134651,0.000183031,0.,0.0013589],[0.0609831,0.0596806,-0.000328052,0.0853277],[0.144528,0.142343,-0.000311432,0.202855],[0.196502,-0.193006,0.,0.275434],[0.236314,0.23532,-0.000143363,0.333496],[0.271,0.271,0.,0.383253],[0.302,0.302,0.,0.427],[0.33,0.33,0.,0.467],[0.356,0.356,0.,0.5035]]))
cati_dftpoldata = np.abs(np.array([[0.,0.0019479,-0.221397,0.221405],[0.,0.000469221,0.165736,0.165737],[-0.000360764,0.,0.0853327,0.0853334],[0.,0.,-0.000252849,0.000252874],[0.,0.,0.000288596,0.000288759],[0.,0.,0.,0.],[0.,0.,0.,0.],[-0.000130183,0.000213396,0.,0.000250524],[-0.00230344,0.000788262,0.,0.00243511],[-0.108792,0.108784,0.,0.153849],[-0.165037,0.165084,0.,0.233431],[-0.207312,0.207368,0.,0.293223],[-0.243249,0.243221,0.,0.343986],[-0.275261,0.27527,0.,0.389284],[0.304,0.304,0.,0.43],[0.33,0.33,0.,0.467],[0.3609,0.3609,0.,0.5103]]))
srhf_dftpoldata = np.abs(np.array([[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.]]))


srti_eigamp_data = np.array([
[0,	0, 1.3579,	0, 0, 0,	0,	0,	0.3119],
[0,	0,	1.2907,	0,	0,	0,	0,	0,	0.2702],
[0,	0,	1.2213,	0,	0,	0,	0,	0,	0.2285],
[0,	0,	1.1499,	0,	0,	0,	0,	0,	0.1847],
[0,	0,	1.0773,	0,	0,	0,	0,	0,	0.1341],
[0,	0,	1.0032,	0,	0,	0,	0,	0,	0.0617],
[0,	0,	0.9218,	0,	0,	0,	0,	0,	0],
[0,	0,	0.8361,	0,	0,	0,	0,	0,	0],
[0, 0.0125, 0.7466, 0, 0, 0, 0, 0, 0],
[0.5421, 0.5507, 0, 0, 0, 0, 0.0672, 0.0658, 0],
[0.5374, 0.573, 0, 0, 0, 0, 0.1639, 0.1573, 0],
[0.5551, 0.5795, 0, 0, 0, 0, 0.2242, 0.22, 0],
[0.5773, 0.5848, 0, 0, 0, 0, 0.2742, 0.273, 0],
[0.5937, 0.5978, 0, 0, 0, 0, 0.32, 0.3193, 0],
[0.6122, 0.6119, 0, 0, 0, 0, 0.3622, 0.3623, 0],
[0.6283, 0.6278, 0, 0, 0, 0, 0.4024, 0.4024, 0],
[0.6442, 0.6442, 0, 0, 0, 0, 0.4407, 0.4407, 0]
])

cati_eigamp_data = np.array([
[1.1497, 0, 1.5055, 0, 1.2094, 0, 0.0086, 0, 0.2315],
[1.1649, 0, 1.4573, 0, 1.2221, 0, 0.0048, 0, 0.1702],
[1.1798, 0, 1.4105, 0, 1.2325, 0, 0.0016, 0, 0.0862],
[1.1957, 0, 1.361, 0, 1.2473, 0, 0, 0, 0],
[1.2113, 0, 1.3123, 0, 1.2624, 0, 0, 0, 0],
[1.2256, 0, 1.2675, 0, 1.2737, 0, 0, 0, 0],
[1.2391, 0, 1.2264, 0, 1.2821, 0, 0, 0, 0],
[1.2516, 0, 1.1888, 0, 1.288, 0, 0, 0, 0],
[1.2637, 0, 1.1551, 0, 1.2911, 0, 0, 0, 0],
[1.2787, 1.2787, 0, 0, 0, 1.1451, 0.1096, 0.1096, 0],
[1.2825, 1.2824, 0, 0, 0, 1.1521, 0.1694, 0.1694, 0],
[1.2846, 1.2845, 0, 0, 0, 1.1666, 0.2169, 0.2169, 0],
[1.2848, 1.2849, 0, 0, 0, 1.1885, 0.2596, 0.2596, 0],
[1.2828, 1.2828, 0, 0, 0, 1.2176, 0.2999, 0.2999, 0],
[1.2775, 1.2775, 0, 0, 0, 1.2545, 0.3394, 0.3394, 0],
[1.268, 1.268, 0, 0, 0, 1.2992, 0.3793, 0.3793, 0],
[1.2518, 1.2518, 0, 0, 0, 1.3527, 0.4211, 0.4211, 0]
])

srhf_eigamp_data = np.array([
[0, 0, 2.0848, 0, 0, 0, 0, 0, 0],
[0.0385, 0, 2.0368, 0, 0, 0, 0, 0, 0],
[1.027, 0, 1.6148, 0, 0.8914, 0, 0, 0, 0],
[1.0991, 0, 1.4916, 0, 0.9862, 0, 0, 0, 0],
[1.1424, 0, 1.3942, 0, 1.0407, 0, 0, 0, 0],
[1.1751, 0, 1.3069, 0, 1.0804, 0, 0, 0, 0],
[1.2024, 0, 1.2273, 0, 1.1087, 0, 0, 0, 0],
[1.2392, 1.2392, 0, 0, 0, 1.0218, 0, 0, 0],
[1.2569, 1.2571, 0, 0, 0, 0.9451, 0, 0, 0],
[1.2706, 1.2707, 0, 0, 0, 0.8761, 0, 0, 0],
[1.2814, 1.2815, 0, 0, 0, 0.8132, 0, 0, 0],
[1.2891, 1.2893, 0, 0, 0, 0.7597, 0, 0, 0],
[1.2955, 1.2952, 0, 0, 0, 0.7117, 0, 0, 0],
[1.2996, 1.2996, 0, 0, 0, 0.6723, 0, 0, 0],
[1.3032, 1.3031, 0, 0, 0, 0.6367, 0, 0, 0],
[1.3054, 1.3054, 0, 0, 0, 0.6084, 0, 0, 0],
[1.307, 1.3069, 0, 0, 0, 0.5847, 0, 0, 0]
])


srti_eigval_data = np.array([
[1.42, 1.42, -5.29, 0.16, 0.16, -1.54, -0.54, -0.54, -1.92],
[1.65, 1.65, -3.48, 0.13, 0.13, -1.09, -0.48, -0.48, -1.48],
[1.61, 1.61, -2.06, 0.07, 0.07, -0.69, -0.46, -0.46, -1.1],
[1.17, 1.17, -0.81, -0.01, -0.01, -0.33, -0.49, -0.49, -0.76],
[0.2, 0.2, 0.19, -0.05, -0.05, -0.04, -0.49, -0.49, -0.48],
[-1.18, -1.18, 0.94, -0.12, -0.12, 0.18, -0.52, -0.52, -0.27],
[-2.81, -2.81, 1.44, -0.14, -0.14, 0.34, -0.52, -0.52, -0.11],
[-4.56, -4.56, 1.79, -0.19, -0.19, 0.43, -0.55, -0.55, -0.02],
[-6.41, -6.41, 1.89, -0.21, -0.21, 0.65, -0.56, -0.56, 0.19]
])

cati_eigval_data = np.array([
[-1.28, -1.28, -6.3, -2.88, -2.88, -4.22, -3.34, -3.34, -4.5],
[-1.13, -1.13, -4.57, -2.75, -2.75, -3.7, -3.16, -3.16, -3.99],
[-1.2, -1.2, -3.27, -2.69, -2.69, -3.23, -3.05, -3.05, -3.53],
[-1.47, -1.47, -2.35, -2.61, -2.61, -2.84, -2.94, -2.94, -3.15],
[-1.91, -1.91, -1.77, -2.53, -2.53, -2.5, -2.83, -2.83, -2.8],
[-2.5, -2.5, -1.4, -2.45, -2.45, -2.22, -2.73, -2.73, -2.53],
[-3.24, -3.24, -1.21, -2.35, -2.35, -1.98, -2.61, -2.61, -2.29],
[-4.2, -4.2, -1.1, -2.24, -2.24, -1.78, -2.49, -2.49, -2.09],
[-5.41, -5.41, -1.09, -2.12, -2.12, -1.61, -2.36, -2.36, -1.91]
])

srhf_eigval_data = np.array([
[-0.99, -0.99, -3.81, -2.27, -2.27, -3.53, -2.73, -2.73, -3.8],
[-0.52, -0.52, -2.3, -2.07, -2.07, -2.95, -2.47, -2.47, -3.23],
[-0.24, -0.24, -1.31, -1.91, -1.91, -2.46, -2.27, -2.27, -2.74],
[-0.21, -0.21, -0.72, -1.8, -1.8, -2.04, -2.11, -2.11, -2.33],
[-0.41, -0.41, -0.39, -1.69, -1.69, -1.68, -1.98, -1.98, -1.97],
[-0.74, -0.74, -0.23, -1.61, -1.61, -1.38, -1.88, -1.88, -1.67],
[-1.11, -1.11, -0.16, -1.53, -1.53, -1.12, -1.78, -1.78, -1.41],
[-1.51, -1.51, -0.18, -1.47, -1.47, -0.91, -1.71, -1.71, -1.2],
[-1.94, -1.94, -0.22, -1.41, -1.41, -0.75, -1.64, -1.64, -1.04]
])


energies = [srti_dftenergydata, cati_dftenergydata, srhf_dftenergydata]
pols = [srti_dftpoldata, cati_dftpoldata, srhf_dftpoldata]
eig_amps = [srti_eigamp_data, cati_eigamp_data, srhf_eigamp_data]
eig_vals = [srti_eigval_data, cati_eigval_data, srhf_eigval_data]

ref_lattice_constants = [3.86, 3.81, 4.07]


####### styling #########

energy_ylim_bottom = [-15.0, -25, -30]
energy_ylims = [190, 280, 380]

marker_size_base = 75.0
pol_x_marker_size_increase = marker_size_base*0.0
base_linewidth = 3.0
pol_mag_linewidth_increase = base_linewidth*0.2

energy_marker_color = (0.3,)*3
pol_x_marker_color = (1.0, 0.0, 0.0)
pol_y_marker_color = (0.0, 1.0, 0.0)
pol_z_marker_color = (0.0, 0.0, 1.0)

aminus = '#F513EA' #purple
bminus = 'gray'
cminus = (0.0, 1.0, 0.0) #green
aplus = 'cyan'
bplus = 'yellow'
cplus = (1.0, 0.0, 0.0) #red
fex = 'black'
fey = '#0049DA'
fez = '#FF6315' #orange

fex = pol_x_marker_color
fey = pol_y_marker_color
fez = pol_z_marker_color
aminus = (0.7,)*3
bminus = '#F513EA' #purple
cminus = '#FF6315'
aplus = (0.1, 0.1, 0.1)
bplus = 'yellow'
cplus = 'cyan'

eig_amp_markers = ['s', '^', 'D', 's', '^', 'D', 's', '^', 'D']
eig_amp_colors = [aminus, bminus, cminus, aplus, bplus, cplus, fex, fey, fez]

labels = ['R-x', 'R-y', 'R-z', 'M-x', 'M-y', 'M-z', '$\Gamma$-x', '$\Gamma$-y', '$\Gamma$-z']
# labels = ['$R_{4}^-$-x', '$R_{4}^-$-y', '$R_{4}^-$-z', '$M_{3}^+$-x', '$M_{3}^+$-y', '$M_{3}^+$-z', '$\Gamma$-x', '$\Gamma$-y', '$\Gamma$-z']
# labels = [r'$\mathbf{a^-}$', r'$\mathbf{b^-}$', r'$\mathbf{c^-}$', r'$\mathbf{a^+}$', r'$\mathbf{b^+}$', r'$\mathbf{c^+}$', r'$\mathrm{\mathbf{FE_x}}$', r'$\mathrm{\mathbf{FE_y}}$', r'$\mathrm{\mathbf{FE_z}}$']

eig_val_markers = eig_amp_markers
eig_val_colors = [fex, fey, fez, aplus, bplus, cplus, aminus, bminus, cminus]

#eig_val_markers = ['s', 's', 'D', 's', 's', 'D', 's', 's', 'D']

eig_amp_ylims = [1.49, 1.65, 2.3]
eig_val_ylims = [[-3.0, 2.4], [-5.0, -0.6], [-4.0, 0.4]]


y_tick_spacings = [[50, 100, 100], [0.1, 0.1, 0.1], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]]

x_lab_padding = 10.0
y_lab_padding = 7.0

upper_x_lab_padding = 5.0

x_label_font_size = 22
upper_x_font_size = 16

y_label_font_size = 17


plt.rcParams['axes.linewidth'] = 3.0

tick_size = 9
tick_width = 3.0
label_size = 15

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
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

#########################





figure, sub_plots = plt.subplots(nrows=4, ncols=3, sharex=True, gridspec_kw={'height_ratios': [2, 3, 4, 4]})
figure.set_size_inches(21, 14, forward=True)
plt.subplots_adjust(hspace=0, wspace=0.26)


for i in range(3):

	sub_plots[0][i].set_xlim([-4.0, 4.0])
	sub_plots[0][i].set_ylim([energy_ylim_bottom[i], energy_ylims[i]])

	sub_plots[0][i].scatter(misfit_strains_pol_en, energies[i], c=energy_marker_color, marker='o', s=marker_size_base)


	sub_plots[1][i].set_ylim([0.0, 0.57])

	sub_plots[1][i].scatter(misfit_strains_pol_en, pols[i][:, 0], c=pol_x_marker_color, marker='s', s=marker_size_base+pol_x_marker_size_increase, label=r'$\mathrm{\mathbf{P_x}}$')
	sub_plots[1][i].scatter(misfit_strains_pol_en, pols[i][:, 1], c=pol_y_marker_color, marker='^', s=marker_size_base*1.7, label=r'$\mathrm{\mathbf{P_y}}$')
	sub_plots[1][i].scatter(misfit_strains_pol_en, pols[i][:, 2], c=pol_z_marker_color, marker='D', s=marker_size_base, label=r'$\mathrm{\mathbf{P_z}}$')
	sub_plots[1][i].plot(misfit_strains_pol_en, pols[i][:, 3], c='black', linewidth=(base_linewidth+pol_mag_linewidth_increase), dashes=[10, 10], label=r'$\mathrm{\mathbf{||P||}}$')

	sub_plots[2][i].set_ylim(0.0, eig_amp_ylims[i])

	for j in range(9):

		if eig_amp_markers[j] == '^':
			boost = 1.7
		else:
			boost = 1.0

		sub_plots[2][i].scatter(misfit_strains_pol_en, eig_amps[i][:, j], marker=eig_amp_markers[j], c=eig_amp_colors[j], s=marker_size_base*boost,  label=labels[j])

	sub_plots[3][i].set_ylim(eig_val_ylims[i])

	for j in range(9):

		if eig_amp_markers[j] == '^':
			boost = 1.4
			zorder = 3
			linewidth_boost = 0.9
			dashes = [3, 3]

		if eig_amp_markers[j] == 's':
			boost = 1.4
			zorder = 2
			dashes = []
			linewidth_boost = 1.0

		if eig_amp_markers[j] == 'D':
			boost = 1.0
			linewidth_boost = 1.0
			dashes = []


		step = 0.005
		x = np.arange(min(misfit_strains_pol_en), max(misfit_strains_pol_en)+step, step)
		poly_fit = np.polyfit(misfit_strains_eig, eig_vals[i][:, j], 4)
		sub_plots[3][i].plot(x, np.poly1d(poly_fit)(x), c=eig_val_colors[j], linewidth=(base_linewidth*linewidth_boost), zorder=zorder, dashes=dashes)
		sub_plots[3][i].plot(x, np.poly1d(poly_fit)(x), c='black', linewidth=(base_linewidth*linewidth_boost)*1.4, zorder=1)



		sub_plots[3][i].scatter(misfit_strains_eig, eig_vals[i][:, j], marker=eig_val_markers[j], c=eig_val_colors[j], s=marker_size_base*boost, zorder=4)


	for c in range(4):
		sub_plots[c][i].xaxis.set_tick_params(pad=x_lab_padding)
		sub_plots[c][i].yaxis.set_tick_params(pad=y_lab_padding)


		sub_plots[c][i].xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
		sub_plots[c][i].xaxis.set_major_locator(ticker.MultipleLocator(2.0))

		sub_plots[c][i].yaxis.set_minor_locator(ticker.MultipleLocator(y_tick_spacings[c][i]/2.0))
		sub_plots[c][i].yaxis.set_major_locator(ticker.MultipleLocator(y_tick_spacings[c][i]))

	sub_plots[0][i].set_ylabel('E (meV/f.u.)', fontsize=y_label_font_size)	
	sub_plots[1][i].set_ylabel('P (C/m$^2$)', fontsize=y_label_font_size)
	sub_plots[2][i].set_ylabel('Eigenmode Amp.', fontsize=y_label_font_size)
	sub_plots[3][i].set_ylabel('Eigenvalue (eV/$\mathrm{\mathbf{\AA^2}}$)', fontsize=y_label_font_size)

	sub_plots[3][i].set_xlabel('Misfit Strain (%)', fontsize=x_label_font_size, labelpad=8)


	a = ref_lattice_constants[i]

	upper_x = sub_plots[0][i].twiny()
	upper_x.set_xlim([0.96*a, 1.04*a])

	f = lambda x : a*(1.0+x*0.01)
	ticks = f(sub_plots[0][i].get_xticks())
	minor_ticks = []

	for r in range(2*len(ticks)-1):
		if r % 2 == 0:
			minor_ticks.append(ticks[int(r/2)])
		else:
			minor_ticks.append((ticks[int(r/2)]+ticks[int(r/2)+1])*0.5)

	upper_x.xaxis.set_major_locator(ticker.FixedLocator(ticks))
	upper_x.xaxis.set_minor_locator(ticker.FixedLocator(minor_ticks))
	upper_x.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))


	upper_x.set_xlabel(r'Epitaxial Lattice Constant ($\mathrm{\AA}$)', fontsize=upper_x_font_size, labelpad=14)

	upper_x.xaxis.set_tick_params(pad=upper_x_lab_padding)


ax = sub_plots[1][1]

handles, labels = ax.get_legend_handles_labels()
dashed_line = plt.Line2D((0,1),(0,0), color='black', linestyle='--', linewidth=4.0)

handles[0] = dashed_line

pol_legend = ax.legend(handles, labels, loc='center', fancybox=True, scatterpoints=1, bbox_to_anchor=(0.3435, 0.53), ncol=1, fontsize=16, labelspacing=0.7, borderpad=0.4, handletextpad=0.2)

pol_legend.get_frame().set_linewidth(3.0)


ax = sub_plots[2][1]

handles, labels = ax.get_legend_handles_labels()

handles = handles[6:9] + handles[3:6] + handles[0:3]
labels = labels[6:9] + labels[3:6] + labels[0:3]

pol_legend = ax.legend(handles, labels, loc='center', fancybox=True, scatterpoints=1, bbox_to_anchor=(0.4, 0.41), ncol=3, 
	columnspacing=0.6, labelspacing=0.7, borderpad=0.5, handletextpad=0.08, prop={'weight':'normal', 'size':16})

pol_legend.get_frame().set_linewidth(3.0)


title_size = 32
title_x = 0.5
title_y = 1.54

ax = sub_plots[0][0]
ax.text(title_x, title_y, '(a) SrTiO$_3$', size=title_size, horizontalalignment='center', transform=ax.transAxes)

ax = sub_plots[0][1]
ax.text(title_x, title_y, '(b) CaTiO$_3$', size=title_size, horizontalalignment='center', transform=ax.transAxes)

ax = sub_plots[0][2]
ax.text(title_x, title_y, '(c) SrHfO$_3$', size=title_size, horizontalalignment='center', transform=ax.transAxes)



phase_lines_width = 2.5
color = (0.2,)*3

for i in range(2):

	ax = sub_plots[i][0]
	ax.axvline(x=-1.0, color=color, linestyle='--', zorder=-1, linewidth=phase_lines_width)
	ax.axvline(x=0.25, color=color, linestyle='--', zorder=-1, linewidth=phase_lines_width)

	ax = sub_plots[i][1]
	ax.axvline(x=-2.5, color=color, linestyle='--', zorder=-1, linewidth=phase_lines_width)
	ax.axvline(x=0.0, color=color, linestyle='--', zorder=-1, linewidth=phase_lines_width)

	ax = sub_plots[i][2]
	ax.axvline(x=-3.0, color=color, linestyle='--', zorder=-1, linewidth=phase_lines_width)
	ax.axvline(x=-1.0, color=color, linestyle='--', zorder=-1, linewidth=phase_lines_width)


phase_text_y = 0.66
font_size = 15

ax = sub_plots[0][0]
ax.text(0.23, phase_text_y, 'I4cm', horizontalalignment='center', transform=ax.transAxes, style='italic', size=font_size, bbox={'facecolor':'white', 'edgecolor':'none'})
ax.text(0.455, phase_text_y, 'I4/mcm', horizontalalignment='center', transform=ax.transAxes, style='italic', size=font_size, bbox={'facecolor':'white', 'edgecolor':'none'})
ax.text(0.73, phase_text_y, 'Ima2', horizontalalignment='center', transform=ax.transAxes, style='italic', size=font_size, bbox={'facecolor':'white', 'edgecolor':'none'})

ax = sub_plots[0][1]
ax.text(0.1, phase_text_y, 'Pm', horizontalalignment='center', transform=ax.transAxes, style='italic', size=font_size, bbox={'facecolor':'white', 'edgecolor':'none'})
ax.text(0.335, phase_text_y, 'P2$_1$/m', horizontalalignment='center', transform=ax.transAxes, style='italic', size=font_size, bbox={'facecolor':'white', 'edgecolor':'none'})
ax.text(0.68, phase_text_y, 'Pmn2$_1$', horizontalalignment='center', transform=ax.transAxes, style='italic', size=font_size, bbox={'facecolor':'white', 'edgecolor':'none'})

ax = sub_plots[0][2]
ax.text(0.10, phase_text_y, 'I4/mcm', horizontalalignment='center', transform=ax.transAxes, style='italic', size=font_size, bbox={'facecolor':'white', 'edgecolor':'none'})
ax.text(0.25, phase_text_y-0.25, 'P2$_1$/m', horizontalalignment='center', transform=ax.transAxes, style='italic', size=font_size, bbox={'facecolor':'white', 'edgecolor':'none'})
ax.text(0.59, phase_text_y, 'Pnma', horizontalalignment='center', transform=ax.transAxes, style='italic', size=font_size, bbox={'facecolor':'white', 'edgecolor':'none'})






# figure.set_figwidth(8)
# figure.set_figheight(8)
figure.patch.set_facecolor('white')
#figure.text(0.5, 0.94, title, fontsize=16, ha='center')


# plt.show()

plt.savefig('C:\\Users\\Tom\\Documents\\Berkeley\\research\my_papers\\Epitaxial Phase Validation Paper\\Exploring Energy Landscape Paper\\rough_figures\\en_pol_total.jpg', format='jpeg', dpi=200, bbox_inches='tight')