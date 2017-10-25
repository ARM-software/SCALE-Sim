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
        sram_trace_file=sram_read_trace_file,
        sram_write_trace_file=sram_write_trace_file
    )

    dram.dram_trace_read(
        filter_sram_sz= filter_sram_size,
        ifmap_sram_sz= ifmap_sram_size,
        word_size= word_size_bytes,
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


if __name__ == "__main__":
    gen_all_traces()