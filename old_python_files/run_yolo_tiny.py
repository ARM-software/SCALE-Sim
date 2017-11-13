import trace_gen_wrapper as tg
import os


def run_yolo_tiny(sram_sz_kb=1):
    #dimensions = 16
    dimensions = 24 
    sram_size = sram_sz_kb * 1024

    yolo_tiny = open("yolo_tiny.csv", 'r')
    bw = open("yolo_tiny_avg_bw.csv", 'w')

    bw.write("SRAM Size, Conv Layer Num,  DRAM IFMAP Read BW, DRAM Filter Read BW, DRAM OFMAP Write BW,")
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

        bw_log = str(sram_sz_kb) +", " + str(ctr) + ", "
        bw_log += tg.gen_all_traces(dimentions=dimensions,
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

def gen_sram_write_bw():
    path = "/home/ubuntu/anand/Repos/systolic/output/nn_euphrates/512KB_yolo_tiny/" 
    for i in range(1,10):
        filename = path
        filename += "yolo_tiny_Conv" + str(i) + "_sram_write.csv"

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


if __name__ == "__main__":

    gen_sram_write_bw()

    #points = [32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
    #points = [64, 128, 256, 512, 1024, 2048, 4096, 8192]
    #points = [512]
    #for p in points:
    #    print(" SRAM size = " +str(p)+ " KB")
    #    run_yolo_tiny(p)

    #    dirname = "output/" + str(p) + "KB"
    #    command = "mkdir " + dirname
    #    os.system(command)

    #    command = "mv *read* " + dirname
    #    os.system(command)

    #    command = "mv *write* " + dirname
    #    os.system(command)
