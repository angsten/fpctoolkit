from fpctoolkit.io.file import File
from fpctoolkit.util.path import Path
import fpctoolkit.util.string_util as su



def round_string(string):
	rnd = 2

	if float(string) == 0.0:
		return '0.0'

	return str(round(float(string), rnd))

def get_table_chunk(misfit_strain, mode_count):

	output_string = ""


	mfit_str = str(misfit_strain)
	while len(mfit_str) < 5:
		mfit_str += " "


	output_string += "Misfit Strain & Eigenmode & " + " & ".join(str(x) for x in range(1, mode_count+1)) + " \\\\ \hline\n"


	file_path = Path.join(str(misfit_strain).replace('-', 'n'), "output_mode_effective_charge_vectors")

	file = File(file_path)

	eigen_values_list = []
	polarizations_list = []
	spg_list = []
	glazers_list = ['N/A']*mode_count

	glazers = ["$a^0_+b^0_0b^0_0$", "$a^0_0b^0_+a^0_0$", "$a^0_0a^0_0c^0_+$", "$a^-_0b^0_0b^0_0$", "$a^0_0b^-_0a^0_0$", "$a^0_0a^0_0c^-_0$", "$a^+_0b^0_0b^0_0$",  "$a^0_0b^+_0a^0_0$", "$a^0_0a^0_0c^+_0$"]

	for i in range(0, mode_count):
		line = file[i]

		line = su.remove_extra_spaces(line)

		parts = line.split(' ')

		eigen_value = parts[1]
		px = parts[2]
		py = parts[3]
		pz = parts[4]
		spg = parts[5]

		translational_mode = bool(spg == 'Pm-3m')


		spg_list.append(spg)

		if not translational_mode:
			eigen_values_list.append(round_string(eigen_value))
			polarizations_list.append('(' + round_string(px) + ' ' + round_string(py) + ' ' + round_string(pz) + ')')

			if spg == 'P4mm':
				if abs(float(px)) > 0.0:
					glazers_list[i] = glazers[0]
				elif abs(float(py)) > 0.0:
					glazers_list[i] = glazers[1]
				elif abs(float(pz)) > 0.0:
					glazers_list[i] = glazers[2]

		else:
			eigen_values_list.append('')
			polarizations_list.append('*')
			glazers_list[i] = ''

	# for i in range(0, mode_count):
	# 	glazer_string = ""


	# 	if polarizations_list





 	output_string += "         &  $\lambda_i$      & " + " & ".join(eigen_values_list) + '\\\\\n'
 	output_string += mfit_str + "    &  $\\vec{Z}_i$      &" + " & ".join(polarizations_list) + ' \\\\\n'
 	output_string += "         &  Modified Glazer  & " + " & ".join(glazers_list) + "\\\\ \hline"

 	return output_string


# u_1     -0.4900       0.0000  0.0000  0.0000    I4/mcm (140)  I4/mcm (140)  I4/mcm (140)
# u_2     -0.4900       0.0000  0.0000  0.0000    I4/mcm (140)  I4/mcm (140)  I4/mcm (140)
# u_3     -0.4800       0.0000  0.0000  0.0000    I4/mcm (140)  I4/mcm (140)  I4/mcm (140)
# u_4     -0.0500       0.0000  0.0000  0.0000    P4/mbm (127)  Immm (71)  Immm (71)
# u_5     -0.0500       0.0000  0.0000  0.0000    P4/mbm (127)  Immm (71)  Immm (71)
# u_6     -0.0400       0.0000  0.0000  0.0000    P4/mbm (127)  P4/mbm (127)  P4/mbm (127)
# u_7      0.0000       0.0375  0.0000  0.0000    Pm-3m (221)  Pm-3m (221)  P4mm (99)
# u_8      0.0000       0.0000 -0.0375  0.0000    Pm-3m (221)  Pm-3m (221)  P4mm (99)
# u_9      0.0000       0.0000  0.0000  0.0058    Pm-3m (221)  Pm-3m (221)  P4mm (99)
# u_10     0.1900       0.0000  0.0000 -0.8757    P4mm (99)  P4mm (99)  P4mm (99)
# u_11     0.2000      -0.8746  0.0000  0.0000    P4mm (99)  P4mm (99)  P4mm (99)
# u_12     0.2000       0.0000  0.8746  0.0000    P4mm (99)  P4mm (99)  P4mm (99)
# u_13     1.7100       0.0000  0.0000  0.0000    Pmma (51)  Pbam (55)  Pbam (55)
# u_14     1.7100       0.0000  0.0000  0.0000    Pmma (51)  Pbam (55)  Pbam (55)
# u_15     1.7100       0.0000  0.0000  0.0000    P4/nmm (129)  P4/nmm (129)  Pmmn (59)





#     Misfit Strain    &  Eigenmode     & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 \\ \hline
#               &  $\lambda_i$   & -2.1 & -1.1 & -0.69 & -0.46 & -0.46 & & & \\ 
#       -0.02   &  $\vec{Z}_i$   &  (0 0 0.9) & (0 0 0)  & (0 0 0)  &  (0 0 0)  & (0 0 0)  & * & * & *  \\ 
#               &  Modified Glazer   & $a^0_0a^0_0c^0_+$  & $a^0_0a^0_0c^-_0$  & $a^0_0a^0_0c^+_0$  & $a^0_0b^-_0a^0_0$  & $a^-_0b^0_0b^0_0$  &   &   &  \\ \hline
              
#               &  $\lambda_i$   & -0.81 & -0.76 & -0.49 & -0.49 & -0.33 & -0.01 & -0.01 & \\ 
#       -0.01   &  $\vec{Z}_i$   &  (0 0 0.9) & (0 0 0)  & (0 0 0)  &  (0 0 0)  & (0 0 0)  & (0 0 0) & (0 0 0) & *  \\ 
#               &  Modified Glazer   & $a^0_0a^0_0c^0_+$  & $a^0_0a^0_0c^-_0$  & $a^-_0b^0_0b^0_0$ & $a^0_0b^-_0a^0_0$  &  $a^0_0a^0_0c^+_0$ & $a^+_0b^0_0b^0_0$  & $a^0_0b^+_0a^0_0$  &  \\ \hline
                            
#               &  $\lambda_i$   & -0.49 & -0.49 & -0.48 & -0.05 & -0.05 & -0.04 &  & \\ 
#       0.0     &  $\vec{Z}_i$   &  (0 0 0) & (0 0 0)  & (0 0 0)  &  (0 0 0)  & (0 0 0)  & (0 0 0) & * & *  \\ 
#               &  Modified Glazer & $a^-_0b^0_0b^0_0$  & $a^0_0b^-_0a^0_0$ & $a^0_0a^0_0c^-_0$ & $a^+_0b^0_0b^0_0$  & $a^0_0b^+_0a^0_0$ & $a^0_0a^0_0c^+_0$ &  &  \\ \hline


if __name__ == "__main__":

	mode_count = 8
	misfits = [-0.02, -0.01, 0.0, 0.01, 0.02]

	print "\\begin{tabular}{" + 'c'*(mode_count+2) + "}"

	for misfit in misfits:
		print get_table_chunk(misfit, mode_count)


	print "\\end{tabular}"