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


def gen_avg_bw(dram_ifmap_trace_file, dram_filter_trace_file,
               dram_ofmap_trace_file, sram_write_trace_file
               ):


    min_clk = 0
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


def test():
    test_fc1_24x24 = [27, 37, 512, 27, 37, 512, 1, 24, 1]
    test_yolo_tiny_conv1_24x24 = [418, 418, 3, 3, 3, 16, 1, 24, 1]
    test_mdnet_conv1_24x24 = [107, 107, 3, 7, 7, 96, 2, 24, 1]
    test_yolov2_conv4_24x24 = [104, 104, 128, 1, 1, 64, 1, 24, 1]

    test_yolov2_conv21_24x24 = [16, 11, 3072, 3, 3, 1024, 1, 24, 1]

    #param = test_fc1_24x24
    #param = test_yolo_tiny_conv1_24x24
    #param = test_mdnet_conv1_24x24
    param = test_yolov2_conv21_24x24

    # The parameters for 1st layer of yolo_tiny
    ifmap_h = param[0]
    ifmap_w = param[1]
    num_channels = param[2]

    filt_h = param[3]
    filt_w = param[4]
    num_filters = param[5] #16

    strides = param[6]

    # Model parameters
    dimensions = param[7] #32 #16
    word_sz = param[8]

    #filter_sram_size = 512 * 1024
    #ifmap_sram_size = 512 * 1024
    #ofmap_sram_size = 512 * 1024

    filter_sram_size = 256 * 1024
    ifmap_sram_size = 256 * 1024
    ofmap_sram_size = 256 * 1024

    filter_base = 1000000 * 100
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
