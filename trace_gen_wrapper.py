import math
import dram_trace as dram
import sram_traffic as sram

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

    sram.sram_traffic(
        dimensions=dimentions,
        ifmap_h=ifmap_h, ifmap_w=ifmap_w,
        filt_h=filt_h, filt_w=filt_w,
        num_channels=num_channels,
        strides=strides, num_filt=num_filt,
        filt_base=filt_base, ifmap_base=ifmap_base,
        sram_read_trace_file=sram_read_trace_file,
        sram_write_trace_file=sram_write_trace_file
    )

    dram.dram_trace_read_v2(
        sram_sz=ifmap_sram_size,
        word_sz_bytes=word_size_bytes,
        min_addr=ifmap_base, max_addr=filt_base,
        sram_trace_file=sram_read_trace_file,
        dram_trace_file=dram_ifmap_trace_file,
    )

    dram.dram_trace_read_v2(
        sram_sz= filter_sram_size,
        word_sz_bytes= word_size_bytes,
        min_addr=filt_base, max_addr=(filt_base * 10000),
        sram_trace_file= sram_read_trace_file,
        dram_trace_file= dram_filter_trace_file,
    )

    dram.dram_trace_write(
        ofmap_sram_size= ofmap_sram_size,
        data_width_bytes= word_size_bytes,
        sram_write_trace_file= sram_write_trace_file,
        dram_write_trace_file= dram_ofmap_trace_file
    )
'''
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
'''

def test():

    # The parameters for 1st layer of yolo_tiny
    ifmap_h = 418
    ifmap_w = 418
    num_channels = 3

    filt_h = 3
    filt_w = 3
    num_filters = 16

    strides = 1

    # Model parameters
    dimensions = 32 #16
    word_sz = 1

    filter_sram_size = 1 * 1024
    ifmap_sram_size = 1 * 1024
    ofmap_sram_size = 1 * 1024

    filter_base = 1000000
    ifmap_base = 0

    # Trace files
    sram_read_trace = "test_sram_read.csv"
    sram_write_trace  = "test_sram_write.csv"

    dram_filter_read_trace = "test_dram_filt_read.csv"
    dram_ifmap_read_trace  = "test_dram_ifamp_read.csv"
    dram_write_trace = "test_dram_write.csv"

    gen_all_traces(
        dimentions= dimensions,
        ifmap_h= ifmap_h, ifmap_w= ifmap_w, num_channels=num_channels,
        filt_h= filt_h, filt_w= filt_w, num_filt= num_filters,
        strides= strides,

        filter_sram_size= filter_sram_size, ifmap_sram_size= ifmap_sram_size, ofmap_sram_size= ofmap_sram_size,
        word_size_bytes= word_sz, filt_base= filter_base, ifmap_base= ifmap_base,

        sram_read_trace_file= sram_read_trace, sram_write_trace_file= sram_write_trace,

        dram_filter_trace_file= dram_filter_read_trace,
        dram_ifmap_trace_file= dram_ifmap_read_trace,
        dram_ofmap_trace_file= dram_write_trace
    )


if __name__ == "__main__":
    test()
