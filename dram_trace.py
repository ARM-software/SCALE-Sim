import os.path
import math


def prune(input_list):
    l = []

    for e in input_list:
        e = e.strip()
        if e != '' and e != ' ':
            l.append(e)

    return l


def dram_trace(
    filter_sram_sz  = 512000,        # 500 KB
    ifmap_sram_sz   = 512000,
    word_size       = 1,             # Word size in bytes
    sram_trace_file = "sram_log.csv",
    dram_filter_trace_file = "dram_filter_log.csv",
    dram_ifmap_trace_file  = "dram_ifmap_log.csv"
    ):

    if not os.path.exists(sram_trace_file):
        print("SRAM trace not found, please provide a valid path")
        return

    ifmap_data_cap  = int(ifmap_sram_sz / word_size)
    filter_data_cap = int(filter_sram_sz / word_size)

    unique_filters  = set()
    unique_ifmap    = set()

    last_flush_filter = 0
    last_flush_ifmap  = 0

    data_per_clk_filter = 0
    data_per_clk_ifmap = 0

    sram_requests = open(sram_trace_file, 'r')
    dram_filter = open(dram_filter_trace_file, 'w')
    dram_ifmap  = open(dram_ifmap_trace_file, 'w')

    for row in sram_requests:
        elems = row.strip().split(',')
        elems = prune(elems)
        elems = [float(x) for x in elems]
        print(elems)
        clk = int(elems[0])

        for e in range(1, len(elems)):
            if elems[e] >= 1000000:

                if elems[e] not in unique_filters:
                # --- So new SRAM request has come in this clock. 
                # --- we first check that weather this new element is present in the working buffer
                # --- In case the working buffer was full, this implies that data from the double buffer
                # --- is needed to copied over to the working buffer, ie the present working buffer is flushed.

                    # First check if space exist
                    if len(unique_filters) == filter_data_cap:
                    # --- We are full here, flush the existing data ---
                        delta = clk - last_flush_filter
                        data_per_clk_filter = int(math.ceil(filter_data_cap / delta))

                        # Here we are using delta clock cycles to chug
                        c = last_flush_filter
                        while len(unique_filters) > 0:
                            dram_log = str(c) + ", "
                            for i in range(data_per_clk_filter):
                                if len(unique_filters) > 0:
                                    p = unique_filters.pop()
                                    dram_log += str(p) + ", "
                            dram_filter.write(dram_log + "\n")
                            c += 1

                        last_flush_filter = clk

                    #Enter new data
                    unique_filters.add(elems[e])
                ## -------- End adding data part -----------
                #  If the data existed in the first place then we can just reuse it.
        
            else:
            # --- Same thing but this time for ifmap rather then filters ---
                if elems[e] not in unique_ifmap: 
                # First check if space exist

                    if len(unique_ifmap) == ifmap_data_cap:
                    # --- We are full here, flush the existing data ---
                        delta = clk - last_flush_ifmap
                        data_per_clk_ifmap = int(math.ceil(ifmap_data_cap / delta))

                        # Here we are using delta clock cycles to chug
                        c = last_flush_ifmap
                        while len(unique_ifmap) > 0:
                            dram_log = str(c) + ", "
                            for i in range(data_per_clk_ifmap):
                                if len(unique_ifmap) > 0:
                                    p = unique_ifmap.pop()
                                    dram_log += str(p) + ", "
                            dram_ifmap.write(dram_log + "\n")
                            c += 1

                        last_flush_ifmap = clk

                #Enter new data
                unique_ifmap.add(elems[e])


    # Write the rest of the data
    if len(unique_filters) > 0:
        c = last_flush_filter
        while len(unique_filters) > 0:
            dram_log = str(c) + ", "
            c += 1

            for i in range(data_per_clk_filter):
                if len(unique_filters) > 0:
                    p = unique_filters.pop()
                    dram_log += str(p) + ", "
            dram_filter.write(dram_log + "\n")

    if len(unique_ifmap) > 0:
        c = last_flush_ifmap
        while len(unique_ifmap) > 0:
            dram_log = str(c) + ", "
            c += 1

            for i in range(data_per_clk_ifmap):
                if len(unique_ifmap) > 0:
                    p = unique_ifmap.pop()
                    dram_log += str(p) + ", "
            dram_ifmap.write(dram_log + "\n")

    dram_filter.close()
    dram_ifmap.close()


if __name__ == "__main__":
        dram_trace(filter_sram_sz=64, ifmap_sram_sz=64, sram_trace_file="sram_log.csv")
