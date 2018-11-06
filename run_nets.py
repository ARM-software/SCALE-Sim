import trace_gen_wrapper as tg
import os
import subprocess


def run_net( ifmap_sram_size=1,
             filter_sram_size=1,
             ofmap_sram_size=1,
             array_h=32,
             array_w=32,
             data_flow = 'os',
             topology_file = './topologies/yolo_v2.csv',
             net_name='yolo_v2',
             offset_list = [0, 10000000, 20000000]
            ):

    ifmap_sram_size *= 1024
    filter_sram_size *= 1024
    ofmap_sram_size *= 1024

    #fname = net_name + ".csv"
    param_file = open(topology_file, 'r')

    fname = net_name + "_avg_bw.csv"
    bw = open(fname, 'w')

    f2name = net_name + "_max_bw.csv"
    maxbw = open(f2name, 'w')

    f3name = net_name + "_cycles.csv"
    cycl = open(f3name, 'w')

    f4name = net_name + "_detail.csv"
    detail = open(f4name, 'w')

    bw.write("IFMAP SRAM Size,\tFilter SRAM Size,\tOFMAP SRAM Size,\tConv Layer Num,\tDRAM IFMAP Read BW,\tDRAM Filter Read BW,\tDRAM OFMAP Write BW,\tSRAM Read BW,\tSRAM OFMAP Write BW, \n")
    maxbw.write("IFMAP SRAM Size,\tFilter SRAM Size,\tOFMAP SRAM Size,\tConv Layer Num,\tMax DRAM IFMAP Read BW,\tMax DRAM Filter Read BW,\tMax DRAM OFMAP Write BW,\tMax SRAM Read BW,\tMax SRAM OFMAP Write BW,\n")
    cycl.write("Layer,\tCycles,\t% Utilization,\n")
    detailed_log = "Layer," +\
                 "\tDRAM_IFMAP_start,\tDRAM_IFMAP_stop,\tDRAM_IFMAP_bytes," + \
                 "\tDRAM_Filter_start,\tDRAM_Filter_stop,\tDRAM_Filter_bytes," + \
                 "\tDRAM_OFMAP_start,\tDRAM_OFMAP_stop,\tDRAM_OFMAP_bytes," + \
                 "\tSRAM_read_start,\tSRAM_read_stop,\tSRAM_read_bytes," +\
                 "\tSRAM_write_start,\tSRAM_write_stop,\tSRAM_write_bytes,\n"

    detail.write(detailed_log)


    first = True
    
    for row in param_file:
        if first:
            first = False
            continue
            
        elems = row.strip().split(',')
        #print(len(elems))
        
        # Do not continue if incomplete line
        if len(elems) < 9:
            continue

        name = elems[0]
        print("")
        print("Commencing run for " + name)

        ifmap_h = int(elems[1])
        ifmap_w = int(elems[2])

        filt_h = int(elems[3])
        filt_w = int(elems[4])

        num_channels = int(elems[5])
        num_filters = int(elems[6])

        strides = int(elems[7])
        
        ifmap_base  = offset_list[0]
        filter_base = offset_list[1]
        ofmap_base  = offset_list[2]

        bw_log = str(ifmap_sram_size) +",\t" + str(filter_sram_size) + ",\t" + str(ofmap_sram_size) + ",\t" + name + ",\t"
        max_bw_log = bw_log
        detailed_log = name + ",\t"

        bw_str, detailed_str, util, clk =  \
            tg.gen_all_traces(  array_h = array_h,
                                array_w = array_w,
                                ifmap_h = ifmap_h,
                                ifmap_w = ifmap_w,
                                filt_h = filt_h,
                                filt_w = filt_w,
                                num_channels = num_channels,
                                num_filt = num_filters,
                                strides = strides,
                                data_flow = data_flow,
                                word_size_bytes = 1,
                                filter_sram_size = filter_sram_size,
                                ifmap_sram_size = ifmap_sram_size,
                                ofmap_sram_size = ofmap_sram_size,
                                filt_base = filter_base,
                                ifmap_base = ifmap_base,
                                ofmap_base = ofmap_base,
                                sram_read_trace_file= net_name + "_" + name + "_sram_read.csv",
                                sram_write_trace_file= net_name + "_" + name + "_sram_write.csv",
                                dram_filter_trace_file=net_name + "_" + name + "_dram_filter_read.csv",
                                dram_ifmap_trace_file= net_name + "_" + name + "_dram_ifmap_read.csv",
                                dram_ofmap_trace_file= net_name + "_" + name + "_dram_ofmap_write.csv"
                            )

        bw_log += bw_str
        bw.write(bw_log + "\n")

        detailed_log += detailed_str
        detail.write(detailed_log + "\n")

        max_bw_log += tg.gen_max_bw_numbers(
                                sram_read_trace_file = net_name + "_" + name + "_sram_read.csv",
                                sram_write_trace_file= net_name + "_" + name + "_sram_write.csv",
                                dram_filter_trace_file=net_name + "_" + name + "_dram_filter_read.csv",
                                dram_ifmap_trace_file= net_name + "_" + name + "_dram_ifmap_read.csv",
                                dram_ofmap_trace_file= net_name + "_" + name + "_dram_ofmap_write.csv"
                                )

        maxbw.write(max_bw_log + "\n")

        # Anand: This is not needed, sram_traffic() returns this
        #last_line = subprocess.check_output(["tail","-1", net_name + "_" + name + "_sram_write.csv"] )
        #clk = str(last_line).split(',')[0]
        #clk = str(clk).split("'")[1]

        util_str = str(util)
        line = name + ",\t" + clk +",\t" + util_str +",\n"
        cycl.write(line)

    bw.close()
    maxbw.close()
    cycl.close()
    param_file.close()

#if __name__ == "__main__":
#    sweep_parameter_space_fast()    

