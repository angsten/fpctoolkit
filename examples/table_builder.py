from fpctoolkit.io.file import File
from fpctoolkit.util.path import Path





def get_table_chunk(misfit_strain, mode_count):

	output_string = ""

	file_path = Path.join(str(misfit_strain).replace('-', 'n'), "output_mode_effective_charge_vectors")

	file = File(file_path)

	for i in range(0, mode_count):
		output_string += file[i]




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