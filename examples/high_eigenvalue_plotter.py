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


misfits = [-0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04]

misfits = [x*100.0 for x in misfits]

cati_x_data = misfits
cati_y_data = [220.1988975, 194.76437, 177.4207625, 159.8922675, 142.7562337, 138.3984288, 170.8971613, 207.2808062, 240.39877]

srhf_x_data = misfits
srhf_y_data = [0, 73.22375, 77.94625, 69.24875, 51.99875, 46.0125, 43.37, 43.255, 44.6825]


plt.minorticks_on()

ax = plt.axes()
ax.tick_params(pad=8)

lab_font_size = 20


plt.axis([-4.5, 4.5, -20.0, 270.0])

ax.xaxis.set_major_locator(ticker.MultipleLocator(1.0))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(25))

ax.text(0.0, -70.0, 'Misfit Strain (%)', size=32, horizontalalignment='center')
ax.text(-5.73, 125.0, '$\Delta$E  (meV)', verticalalignment='center', rotation='vertical', fontsize=32)

marksize = 11

cati, = plt.plot(cati_x_data, cati_y_data, 'o', c='black', markersize=marksize, label="CaTiO$_3$")
srhf, = plt.plot(srhf_x_data, srhf_y_data, 'd', c='red', markersize=marksize, label="SrHfO$_3$")

plt.legend(handles=[cati, srhf])

plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

fig = plt.gcf()
fig.set_size_inches(10, 6)

plt.savefig('C:\\Users\\Tom\\Documents\\Berkeley\\research\my_papers\\Epitaxial Phase Validation Paper\\Paper\\rough_figures\\plot_high_eigval.eps', format='eps', dpi=1000, bbox_inches='tight')
# plt.savefig('C:\\Users\\Tom\\Documents\\Berkeley\\research\my_papers\\Epitaxial Phase Validation Paper\\Paper\\rough_figures\\plot_high_eigval.png', format='png')
plt.show()

plt.clf()
