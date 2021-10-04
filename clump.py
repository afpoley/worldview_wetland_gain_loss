# Create image clumps from input image. Clumps are defined as continuous regions of connected pixels with the same value
# Image clumps are created using the categorical change layer and are used during hybrid change process to smooth
# radiometric change.
# Poley 2/1/2021
import whitebox

wbt = whitebox.WhiteboxTools()
# wbt.verbose = False

# Input file
input_file = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\categoricalChange.tif'
out_file = 'D:\\Users\\afpoley\\Desktop\\USFWF_TEMP\\stClair\\change\\change_clumps.tif'

wbt.clump(input_file, out_file, diag=True, zero_back=False)

