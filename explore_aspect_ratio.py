import sram_traffic as sram
import os
import subprocess

D_H = [4, 8, 16, 32 , 64, 128, 256]
D_V = [256, 128, 64, 32, 16, 8, 4]

#net_name = "yolo_tiny"
#net_name = "resnet1_int8"
net_name = "yolo_v2"

fname = net_name + ".csv"
f = open(fname, 'r')

for row in f:
    elems = row.strip().split(',')

    name = elems[0]

    ifmap_h = int(elems[1])
    ifmap_w = int(elems[2])

    filt_h = int(elems[3])
    filt_w = int(elems[4])

    num_channels = int(elems[5])
    num_filters = int(elems[6])

    strides = int(elems[7])
    filter_base = 1000000 * 100
    ifmap_base = 0
    
    sram_read_file = net_name + "_" + name + "_sram_read.csv"
    sram_write_file = net_name + "_" + name + "_sram_write.csv"

    fcycles_name = net_name + "_" + name + "_cycles.csv"
    fcycles = open(fcycles_name, 'w')
    print("Dimentions, Cycles,")
    fcycles.write("Dimentions, Cycles,\n")

    for i in range(len(D_V)):  
        print("Conv: " + name + " index= " + str(i))
	
        sram.sram_traffic( 
            dimensions_h = D_H[i], 
    	    dimensions_v = D_V[i],
    	    ifmap_h = ifmap_h, ifmap_w = ifmap_w,
    	    filt_h = filt_h, filt_w = filt_w,
    	    num_channels = num_channels,
    	    num_filt = num_filters,
    	    filt_base = filter_base,
    	    ifmap_base = ifmap_base,
    	    sram_read_trace_file = sram_read_file,
    	    sram_write_trace_file = sram_write_file
    	)

        last_line = subprocess.check_output(["tail","-1", sram_write_file]) 
        clk = str(last_line).split(',')[0]
        clk = str(clk).split("'")[1]
        line = "(" + str(D_H[i]) + ":" + str(D_V[i]) + "), " + clk + ","
        print(line)
        fcycles.write(line + "\n")
        
        os.system("rm -rf " + sram_read_file)
        os.system("rm -rf " + sram_write_file)
