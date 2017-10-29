import trace_gen_wrapper as tg


def run_yolo_tiny():
    dimensions = 16
    sram_size = 32 * 1024

    yolo_tiny = open("yolo_tiny.csv", 'r')
    bw = open("yolo_tiny_avg_bw.csv", 'w')

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

        bw_log = tg.gen_all_traces(dimentions=dimensions,
                                ifmap_h=ifmap_h, ifmap_w=ifmap_w,
                                filt_h=filt_h, filt_w=filt_w,
                                num_channels=num_channels, num_filt=num_filters,
                                strides=strides,
                                word_size_bytes=1,
                                filter_sram_size=sram_size, ifmap_sram_size=sram_size, ofmap_sram_size=sram_size,
                                sram_read_trace_file="yolo_tiny_" + name + "_sram_read.csv",
                                sram_write_trace_file="yolo_tiny_" + name + "_sram_write.csv",

                                dram_filter_trace_file="yolo_tiny_" + name + "_dram_filter_read.csv",
                                dram_ifmap_trace_file="yolo_tiny_" + name + "_dram_ifmap_read.csv",
                                dram_ofmap_trace_file="yolo_tiny_" + name + "_dram_ofmap_write.csv"
                                )

        bw.write(bw_log + "\n")

    bw.close()
    yolo_tiny.close()


if __name__ == "__main__":
    run_yolo_tiny()