import math
import dram_trace as dram
import data_trace2 as sram

def gen_all_traces(
        dimentions = 4,
        ifmap_h = 7, ifmap_w = 7,
        filt_h  = 3, filt_w = 3,
        num_channels = 3,
        strides = 1, num_filt = 8,

        word_size_bytes = 1,
        filter_sram_size = 64, ifmap_sram_size= 64, ofmap_sram_size = 64,

        filt_base = 1000000, ifmap_base=0,
        sram_read_trace_file = "sram_read.csv",
        sram_write_trace_file = "sram_write.csv",

        dram_filter_trace_file = "dram_filter_read.csv",
        dram_ifmap_trace_file = "dram_ifmap_read.csv",
        dram_ofmap_trace_file = "dram_ofmap_write.csv"
    ):

    sram.gen_sram_trace(
        dimensions=dimentions,
        ifmap_h=ifmap_h, ifmap_w=ifmap_w, filt_h=filt_h, filt_w=filt_w,
        num_channels=num_channels, strides=strides, num_filt=num_filt,
        filt_base=filt_base, ifmap_base=ifmap_base,
        sram_trace_file=sram_read_trace_file,
        sram_write_trace_file=sram_write_trace_file
    )

    dram.dram_trace_read(
        filter_sram_sz= filter_sram_size,
        ifmap_sram_sz= ifmap_sram_size,
        word_size= word_size_bytes,
        filt_base=filt_base,
        sram_trace_file= sram_read_trace_file,
        dram_filter_trace_file= dram_filter_trace_file,
        dram_ifmap_trace_file= dram_ifmap_trace_file
    )

    dram.dram_trace_write(
        ofmap_sram_size= ofmap_sram_size,
        data_width_bytes= word_size_bytes,
        sram_write_trace_file= sram_write_trace_file,
        dram_write_trace_file= dram_ofmap_trace_file
    )

    dram_activation_bw = 0
    num_clks = 0
    num_bytes = 0
    f = open(dram_ifmap_trace_file, 'r')

    for row in f:
        num_clks += 1
        num_bytes += len(row.split(',')) - 2

    dram_activation_bw = num_bytes / num_clks
    f.close()

    dram_filter_bw = 0
    num_clks = 0
    num_bytes = 0
    f = open(dram_filter_trace_file, 'r')

    for row in f:
        num_clks += 1
        num_bytes += len(row.split(',')) - 2

    dram_filter_bw = num_bytes / num_clks
    f.close()

    dram_ofmap_bw = 0
    num_clks = 0
    num_bytes = 0
    f = open(dram_ofmap_trace_file, 'r')

    for row in f:
        num_clks += 1
        num_bytes += len(row.split(',')) - 2

    dram_ofmap_bw = num_bytes / num_clks
    f.close()

    print("DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW,")
    log = str(dram_activation_bw) + ", " + str(dram_filter_bw) + ", " + str(dram_ofmap_bw) + ","
    print(log)
    return log

if __name__ == "__main__":
    dimensions = 16
    sram_size = 32 * 1024

    yolo_tiny = open("yolo_tiny.csv", 'r')
    bw        = open("yolo_tiny_avg_bw.csv", 'w')

    bw.write("DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW,")
    ctr = 0
    threshold = 21
    for row in yolo_tiny:
        if ctr >= threshold:
            break

        ctr += 1

        elems = row.strip().split(',')

        name = elems[0]

        ifmap_h = int(elems[1])
        ifmap_w = int(elems[2])

        filt_h = int(elems[3])
        filt_w = int(elems[4])

        num_channels = int(elems[5])
        num_filters = int(elems[6])

        strides = int(elems[7])

        bw_log = gen_all_traces(dimentions=dimensions,
                   ifmap_h=ifmap_h, ifmap_w=ifmap_w,
                   filt_h=filt_h, filt_w=filt_w,
                   num_channels=num_channels, num_filt=num_filters,
                   strides=strides,
                   word_size_bytes=1,
                   filter_sram_size=sram_size, ifmap_sram_size=sram_size, ofmap_sram_size=sram_size,
                   sram_read_trace_file="yolo_tiny_" + name +"_sram_read.csv",
                   sram_write_trace_file= "yolo_tiny_" + name +"_sram_write.csv",

                   dram_filter_trace_file= "yolo_tiny_" + name +"_dram_filter_read.csv",
                   dram_ifmap_trace_file= "yolo_tiny_" + name +"_dram_ifmap_read.csv",
                   dram_ofmap_trace_file= "yolo_tiny_" + name +"_dram_ofmap_write.csv"
                   )

        bw.write(bw_log + "\n")

    bw.close()
    yolo_tiny.close()