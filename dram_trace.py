import os.path
import math


def prune(input_list):
    l = []

    for e in input_list:
        e = e.strip()
        if e != '' and e != ' ':
            l.append(e)

    return l


def dram_trace_read(
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


    #filters_buffers  = [set(), set()]
    #ifmap_buffers    = [set(), set()]
    filter_buffer = set()
    ifmap_buffer  = set()

    #filt_fill_idx = 0
    #filt_drain_idx = 1

    #ifmap_fill_idx = 0
    #ifmap_drain_idx = 1

    t_fill_filter = int(math.floor(filter_sram_sz / 2))
    t_fill_ifmap  = int(math.floor(ifmap_sram_sz / 2))

    last_clk_filter = 0
    last_clk_ifmap = 0

    #data_per_clk_filter = 0
    #data_per_clk_ifmap = 0

    sram_requests = open(sram_trace_file, 'r')
    dram_filter = open(dram_filter_trace_file, 'w')
    dram_ifmap  = open(dram_ifmap_trace_file, 'w')

    for row in sram_requests:
        elems = row.strip().split(',')
        elems = prune(elems)
        elems = [float(x) for x in elems]
        #print(elems)
        clk = int(elems[0])

        for e in range(1, len(elems)):
            if elems[e] >= 1000000:

                if elems[e] not in filter_buffer:
                # --- So new SRAM request has come in this clock. 
                # --- we first check that weather this new element is present in the working buffer
                # --- In case the working buffer was full, this implies that data from the double buffer
                # --- is needed to copied over to the working buffer, ie the present working buffer is flushed.

                    # First check if space exist
                    if len(filter_buffer) + word_size > filter_sram_sz:
                    # --- We are full here, flush the existing data ---
                        #if len(filters_buffers[filt_drain_idx]) > 0:
                        data_per_clk_filter = int(math.ceil(len(filter_buffer) / t_fill_filter))

                        # Here we are using delta clock cycles to chug
                        c = last_clk_filter - t_fill_filter
                        while len(filter_buffer) > 0:
                            dram_log = str(c) + ", "
                            for i in range(data_per_clk_filter):
                                if len(filter_buffer) > 0:
                                    p = filter_buffer.pop()
                                    dram_log += str(p) + ", "
                            dram_filter.write(dram_log + "\n")
                            c += 1

                        t_fill_filter = clk - last_clk_filter
                        last_clk_filter = clk

                        ## Swap the indices
                        #temp = filt_drain_idx
                        #filt_drain_idx = filt_fill_idx
                        #filt_fill_idx = temp

                    #Enter new data
                    filter_buffer.add(elems[e])
                ## -------- End adding data part -----------
                #  If the data existed in the first place then we can just reuse it.
        
            else:
            # --- Same thing but this time for ifmap rather then filters ---
                if elems[e] not in ifmap_buffer:
                # First check if space exist
                    if len(ifmap_buffer) + word_size > ifmap_sram_sz:
                        # --- We are full here, flush the existing data ---
                        #if len(ifmap_buffer[ifmap_drain_idx]) > 0:
                        #delta = clk - last_clk_ifmap
                        data_per_clk_ifmap = int(math.ceil(len(ifmap_buffer) / t_fill_ifmap))

                        # Here we are using delta clock cycles to chug
                        c = last_clk_ifmap - t_fill_ifmap
                        while len(ifmap_buffer) > 0:
                            dram_log = str(c) + ", "
                            for i in range(data_per_clk_ifmap):
                                if len(ifmap_buffer) > 0:
                                    p = ifmap_buffer.pop()
                                    dram_log += str(p) + ", "
                            dram_ifmap.write(dram_log + "\n")
                            c += 1

                        t_fill_ifmap = clk - last_clk_ifmap
                        last_clk_ifmap = clk

                        # Swap the indices
                        #temp = ifmap_drain_idx
                        #ifmap_drain_idx = ifmap_fill_idx
                        #ifmap_fill_idx = temp

                #Enter new data
                ifmap_buffer.add(elems[e])

    # Write the rest of the data
    if len(filter_buffer) > 0:
        #delta = clk - last_clk_filter
        c = last_clk_filter - t_fill_filter
        data_per_clk_filter = math.ceil(len(filter_buffer) / t_fill_filter)
        while len(filter_buffer) > 0:
            dram_log = str(c) + ", "
            c += 1

            for i in range(data_per_clk_filter):
                if len(filter_buffer) > 0:
                    p = filter_buffer.pop()
                    dram_log += str(p) + ", "
            dram_filter.write(dram_log + "\n")

    if len(ifmap_buffer) > 0:
        #delta = clk - last_clk_ifmap
        c = last_clk_ifmap - t_fill_ifmap
        data_per_clk_ifmap = math.ceil( len(ifmap_buffer) / t_fill_ifmap)
        while len(ifmap_buffer) > 0:
            dram_log = str(c) + ", "
            c += 1

            for i in range(data_per_clk_ifmap):
                if len(ifmap_buffer) > 0:
                    p = ifmap_buffer.pop()
                    dram_log += str(p) + ", "
            dram_ifmap.write(dram_log + "\n")

    dram_filter.close()
    dram_ifmap.close()


def dram_trace_write(ofmap_sram_size = 64,
                     data_width_bytes = 1,
                     sram_write_trace_file = "sram_write.csv",
                     dram_write_trace_file = "dram_write.csv"):

    traffic = open(sram_write_trace_file, 'r')
    trace_file  = open(dram_write_trace_file, 'w')

    last_clk = 0
    clk = 0

    sram_buffer = [set(), set()]
    filling_buf     = 0
    draining_buf    = 1

    first = True

    for row in traffic:
        if first:           #First line is empty discard it
            first = False
        else:
            elems = row.strip().split(',')
            elems = prune(elems)
            elems = [int(x) for x in elems]

            clk = elems[0]

            # If enough space is in the filling buffer
            # Keep filling the buffer
            if (len(sram_buffer[filling_buf]) + (len(elems) - 1) * data_width_bytes ) < ofmap_sram_size:
                for i in range(1,len(elems)):
                    sram_buffer[filling_buf].add(elems[i])

            # Filling buffer is full, spill the data to the other buffer
            else:
                # If there is data in the draining buffer
                # drain it
                #print("Draining data. CLK = " + str(clk))
                if len(sram_buffer[draining_buf]) > 0:
                    delta_clks = clk - last_clk
                    data_per_clk = math.ceil(len(sram_buffer[draining_buf]) / delta_clks)
                    #print("Data per clk = " + str(data_per_clk))

                    # Drain the data
                    c = last_clk
                    while len(sram_buffer[draining_buf]) > 0:
                        trace = str(c) + ", "
                        c += 1
                        for _ in range(int(data_per_clk)):
                            if len(sram_buffer[draining_buf]) > 0:
                                addr = sram_buffer[draining_buf].pop()
                                trace += str(addr) + ", "

                        trace_file.write(trace + "\n")

                #Swap the ids for drain buffer and fill buffer
                tmp             = draining_buf
                draining_buf    = filling_buf
                filling_buf     = tmp

                #Set the last clk value
                last_clk = clk

                #Fill the new data now
                for i in range(1,len(elems)):
                    sram_buffer[filling_buf].add(elems[i])

    #Drain the last fill buffer
    #print("Draining data. CLK = " + str(clk))
    if len(sram_buffer[filling_buf]) > 0:
        delta_clks = clk - last_clk
        data_per_clk = math.ceil(len(sram_buffer[filling_buf]) / delta_clks)
        #print("Data per clk = " + str(data_per_clk))

        # Drain the data
        c = last_clk
        while len(sram_buffer[filling_buf]) > 0:
            trace = str(c)+ ", "
            c += 1
            for _ in range(int(data_per_clk)):
                if len(sram_buffer[filling_buf]) > 0:
                    addr = sram_buffer[filling_buf].pop()
                    trace += str(addr) + ", "

            trace_file.write(trace + "\n")

    #All traces done
    traffic.close()
    trace_file.close()

if __name__ == "__main__":
        dram_trace_read(filter_sram_sz=1024, ifmap_sram_sz=1024, sram_trace_file="sram_read.csv")
        #dram_trace_write(ofmap_sram_size=1024,sram_write_trace_file="yolo_tiny_layer1_write.csv", dram_write_trace_file="yolo_tiny_layer1_dram_write.csv")
