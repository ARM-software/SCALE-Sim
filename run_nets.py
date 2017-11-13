import trace_gen_wrapper as tg
import sram_traffic as sram
import dram_trace as dram
import os
import subprocess


def run_net_fast(dimensions=32, net_name='yolo_v2'):
    fname = net_name + ".csv"
    param_file = open(fname, 'r')

    fname = net_name + "_avg_bw.csv"
    bw = open(fname, 'w')

    f2name = net_name + "_max_bw.csv"
    maxbw = open(f2name, 'w')

    f3name = net_name + "_cycles.csv"
    cycl = open(f3name, 'w')

    bw.write("SRAM Size, Conv Layer Num,  DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW, SRAM OFMAP Write BW, Min clk, Max clk\n")
    maxbw.write("SRAM Size, Conv Layer Num, Max DRAM IFMAP Read BW,Max DRAM Filter Read BW,Max DRAM OFMAP Write BW,Max SRAM OFMAP Write BW, Cycl MaxActBW, Cycl MaxFiltBW, Cycl MaxOfmapBW\n")
    cycl.write("Layer, Cycles,\n")
    
    for row in param_file:
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

        print("Generating SRAM traffic for " + name)
        sram.sram_traffic( 
                dimensions_h = dimensions,
                dimensions_v = dimensions,
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
        line = name + ", " + clk + ",\n"
        cycl.write(line)

        points = [128, 256, 512, 1024, 2048, 4096, 8192]
        
        for p in points:
            print(name + " : " + str(p) + "KB")

            dram_ifmap_read_file = net_name + "_" + name + "_" + str(p) + "KB_dram_ifmap_read.csv"
            dram_filter_read_file = net_name + "_" + name + "_" + str(p) + "KB_dram_filter_read.csv"
            dram_ofmap_write_file = net_name + "_" + name + "_" + str(p) + "KB_dram_ofmap_write.csv"

            buf_sz = p * 1024
            dram.dram_trace_read_v2(
                    sram_sz = buf_sz,
                    word_sz_bytes =1,
                    min_addr = ifmap_base,
                    max_addr = filter_base -1,
                    sram_trace_file = sram_read_file,
                    dram_trace_file = dram_ifmap_read_file
                    )

            dram.dram_trace_read_v2(
                    sram_sz = buf_sz,
                    word_sz_bytes =1,
                    min_addr = filter_base,
                    max_addr = filter_base * 100000,
                    sram_trace_file = sram_read_file,
                    dram_trace_file = dram_filter_read_file
                    )

            dram.dram_trace_write(
                    ofmap_sram_size = buf_sz,
                    data_width_bytes = 1,
                    sram_write_trace_file = sram_write_file,
                    dram_write_trace_file = dram_ofmap_write_file
                    )

            bw_log = str(p) +", " + name + ", "
            max_bw_log = bw_log

            bw_log += tg.gen_bw_numbers(
                            dram_ifmap_read_file, 
                            dram_filter_read_file,
                            dram_ofmap_write_file,
                            sram_write_file
                        )

            bw.write(bw_log + "\n")

            max_bw_log += tg.gen_max_bw_numbers(
                            dram_ifmap_trace_file = dram_ifmap_read_file,
                            dram_filter_trace_file = dram_filter_read_file,
                            dram_ofmap_trace_file = dram_ofmap_write_file,
                            sram_write_trace_file = sram_write_file
                    )

            maxbw.write(max_bw_log + "\n")

            command = "rm -rf "
            command += dram_ifmap_read_file + " " + dram_filter_read_file + " "
            command += dram_ofmap_write_file

            os.system(command)

    bw.close()
    maxbw.close()
    cycl.close()
    param_file.close()


def run_net(sram_sz_kb=1, dimensions=32,net_name='yolo_v2'):
    sram_size = sram_sz_kb * 1024

    fname = net_name + ".csv"
    param_file = open(fname, 'r')

    fname = net_name + "_avg_bw.csv"
    bw = open(fname, 'w')

    f2name = net_name + "_max_bw.csv"
    maxbw = open(f2name, 'w')

    f3name = net_name + "_cycles.csv"
    cycl = open(f3name, 'w')

    bw.write("SRAM Size, Conv Layer Num,  DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW, SRAM OFMAP Write BW, ")
    maxbw.write("SRAM Size, Conv Layer Num, Max DRAM IFMAP Read BW,Max DRAM Filter Read BW,Max DRAM OFMAP Write BW,Max SRAM OFMAP Write BW,\n")
    cycl.write("Layer, Cycles,\n")
    
    #ctr = 0
    #threshold = 21
    for row in param_file:
        #if ctr >= threshold:
        #    break

        #ctr += 1

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

        bw_log = str(sram_sz_kb) +", " + name + ", "
        max_bw_log = bw_log

        bw_log += tg.gen_all_traces(dimentions=dimensions,
                                ifmap_h=ifmap_h, ifmap_w=ifmap_w,
                                filt_h=filt_h, filt_w=filt_w,
                                num_channels=num_channels, num_filt=num_filters,
                                strides=strides,
                                word_size_bytes=1,
                                filter_sram_size=sram_size, ifmap_sram_size=sram_size, ofmap_sram_size=sram_size,
                                filt_base = filter_base,
                                sram_read_trace_file= net_name + "_" + name + "_sram_read.csv",
                                sram_write_trace_file= net_name + "_" + name + "_sram_write.csv",

                                dram_filter_trace_file=net_name + "_" + name + "_dram_filter_read.csv",
                                dram_ifmap_trace_file= net_name + "_" + name + "_dram_ifmap_read.csv",
                                dram_ofmap_trace_file= net_name + "_" + name + "_dram_ofmap_write.csv"
                                )

        bw.write(bw_log + "\n")

        max_bw_log += tg.gen_max_bw_numbers(
                                sram_write_trace_file= net_name + "_" + name + "_sram_write.csv",
                                dram_filter_trace_file=net_name + "_" + name + "_dram_filter_read.csv",
                                dram_ifmap_trace_file= net_name + "_" + name + "_dram_ifmap_read.csv",
                                dram_ofmap_trace_file= net_name + "_" + name + "_dram_ofmap_write.csv"
                                )

        maxbw.write(max_bw_log + "\n")

        last_line = subprocess.check_output(["tail","-1", net_name + "_" + name + "_sram_write.csv"] )
        clk = str(last_line).split(',')[0]
        clk = str(clk).split("'")[1]
        line = name + ", " + clk + ",\n"
        cycl.write(line)

    bw.close()
    maxbw.close()
    cycl.close()
    param_file.close()

def gen_sram_write_bw():
    path = "/home/ubuntu/anand/Repos/systolic/output/nn_euphrates/yolo_v2_512KB/" 
    for i in range(1,22):
        filename = path
        filename += "yolo_v2_Conv" + str(i) + "_sram_write.csv"

        bw = 0
        num_clks = 0
        num_bytes = 0

        f = open(filename, 'r')

        for row in f:
            num_clks += 1
            num_bytes += len(row.split(',')) - 2

        bw = num_bytes / num_clks
        print(str(bw))
        f.close()

def gen_avg_bw_log( net_name="yolo_v2",
                    sram_size="128KB"
                    ):

    log_path    = "./output/" + sram_size
    common_path = "./output/" + sram_size + "/layer_wise/"

    fname = net_name + ".csv"
    f = open(fname, 'r')

    fname = net_name + "_avg_bw.csv"
    fo = open(fname, 'w')

    fo.write("SRAM Size, Layer Num, DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW, SRAM OFMAP Write BW,\n")

    for row in f:
        elem = row.strip().split(',')

        layer = elem[0]

        dram_ifmap_trace_file   = common_path + net_name + "_" + layer + "_dram_ifmap_read.csv"
        dram_filter_trace_file  = common_path + net_name + "_" + layer + "_dram_filter_read.csv"
        dram_ofmap_trace_file   = common_path + net_name + "_" + layer + "_dram_ofmap_write.csv"
        sram_write_trace_file   = common_path + net_name + "_" + layer + "_sram_write.csv"

        bw_log = sram_size + ", " + layer + ", "
        bw_log += tg.gen_bw_numbers(dram_ifmap_trace_file=dram_ifmap_trace_file,
                            dram_filter_trace_file=dram_filter_trace_file,
                            dram_ofmap_trace_file=dram_ofmap_trace_file,
                            sram_write_trace_file=sram_write_trace_file
                            )

        fo.write(bw_log + "\n")

    f.close()
    fo.close()

    command = "mv " + fname + " " + log_path
    os.system(command)


def sweep_parameter_space_fast():

    dim = 32
    net_name = "resnet1_int8"

    run_net_fast(dimensions=dim, net_name=net_name)

    dirname = "output/" + net_name
    command = "mkdir " + dirname
    os.system(command)

def sweep_parameter_space():

    #points = [64, 128, 256, 512, 1024, 2048, 4096, 8192]
    #points = [128, 256, 512, 1024, 2048, 4096, 8192]
    #points = [512, 1024, 2048, 4096, 8192]
    #points = [4096,8192] 
    points = [256, 512]

    dim = 24
    #net_name = "yolo_tiny"
    net_name = "yolo_v2"
    for p in points:
        print(" SRAM size = " +str(p)+ " KB")
        run_net(p, dim, net_name)

        dirname = "output/" + str(p) + "KB"
        command = "mkdir " + dirname
        os.system(command)

        dirname2 = dirname + "/layer_wise" 
        command = "mkdir " + dirname2
        os.system(command)

        command = "mv *read* " + dirname2
        os.system(command)

        command = "mv *write* " + dirname2
        os.system(command)
         
        command = "mv " + net_name + "_avg_bw.csv " + dirname
        os.system(command)
        
        command = "mv " + net_name + "_max_bw.csv " + dirname
        os.system(command)

        command = "mv " + net_name + "_cycles.csv " + dirname
        os.system(command)

def debug():
    dram_ifmap_trace_file = "/home/ubuntu/anand/Repos/systolic/output/24x24/yolo_v2/512KB/layer_wise/yolo_v2_Conv21_dram_ifmap_read.csv"
    dram_filter_trace_file = "/home/ubuntu/anand/Repos/systolic/output/24x24/yolo_v2/512KB/layer_wise/yolo_v2_Conv21_dram_filter_read.csv"
    dram_ofmap_trace_file = "/home/ubuntu/anand/Repos/systolic/output/24x24/yolo_v2/512KB/layer_wise/yolo_v2_Conv21_dram_ofmap_write.csv"
    sram_write_trace_file = "/home/ubuntu/anand/Repos/systolic/output/24x24/yolo_v2/512KB/layer_wise/yolo_v2_Conv21_sram_write.csv"

    tg.gen_max_bw_numbers(dram_ifmap_trace_file, dram_filter_trace_file, dram_ofmap_trace_file, sram_write_trace_file)



if __name__ == "__main__":
    sweep_parameter_space_fast()    
    #sweep_parameter_space()    
    #debug()
    #gen_avg_bw_log(net_name = "yolo_v2", sram_size="256KB")

