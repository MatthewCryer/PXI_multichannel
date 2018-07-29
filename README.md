# PXI_multichannel
NI PXI chassis with SMU and multiple channel voltage probes. Takes .tdms files, plots and feeds into a tkinter animation.

**tdms_import.py**

Takes a .tdms file from LabView, data from a differential voltage probe board (NI PXIe-4303), renames the channels (just a chance to try regex...) then plots each channel. Also provides a normalisation function, signal filtering (scipy medfilt), detrending (i.e. removes linear trends) and provides an output array.

**tkinter_rectangle.py**

Takes the array provided above, passes each column (channel) into a tkinter generated animation where the colour of each output pixel is dependent upon the current in the channel. Basically a very simple camera software.
Had to define a class and update the drawn items rather than redraw for each of the 1000's of values (that crashed everything...).

**SMU_tdms.py**

Takes the SMU (NI PXIe-4138) current readings and plots, useful as a sanity check when troubleshooting.
