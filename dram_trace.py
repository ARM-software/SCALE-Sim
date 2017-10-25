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
    filt_base       = 1000000,
    sram_trace_file = "sram_log.csv",
    dram_filter_trace_file = "dram_filter_log.csv",
    dram_ifmap_trace_file  = "dram_ifmap_log.csv"
    ):

    if not os.path.exists(sram_trace_file):
        print("SRAM trace not found, please provide a valid path")
        return


    #filter_buffer  = [set(), set()]
    #ifmap_buffer    = [set(), set()]
    filter_buffer = set()
    ifmap_buffer  = set()

    t_fill_filter = -1
    t_fill_ifmap  = -1

    t_drain_filter = 0
    t_drain_ifmap = 0

    #data_per_clk_filter = 0
    #data_per_clk_ifmap = 0
    base_bw = 2

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
            if elems[e] >= filt_base:

                if elems[e] not in filter_buffer:
                # --- So new SRAM request has come in this clock. 
                # --- we first check that weather this new element is present in the working buffer
                # --- In case the working buffer was full, this implies that data from the double buffer
                # --- is needed to copied over to the working buffer, ie the present working buffer is flushed.

                    # First check if space exist
                    if len(filter_buffer) + word_size > filter_sram_sz:

                        if t_fill_filter == -1:
                            t_fill_filter = t_drain_filter - math.ceil(len(filter_buffer) / base_bw)

                        time_to_fill = t_drain_filter - t_fill_filter

                        if time_to_fill == 0:
                            print("Drain time = " + str(t_drain_filter) + " Fill time = " + str(t_fill_filter))

                        out_data_per_clk = math.ceil(len(filter_buffer) / time_to_fill)
                        c = t_fill_filter
                        while len(filter_buffer) > 0:
                            trace = str(c) + ", "

                            for i in range(int(out_data_per_clk)):
                                if len(filter_buffer) > 0:
                                    p = filter_buffer.pop()
                                    trace += str(int(p)) + ", "
                            trace += "\n"
                            dram_filter.write(trace)
                            c += 1

                        t_fill_filter = t_drain_filter
                        t_drain_filter = clk

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

                        if t_fill_ifmap == -1:
                            t_fill_ifmap = t_drain_ifmap - math.ceil(len(ifmap_buffer) / base_bw)

                        time_to_fill = t_drain_ifmap - t_fill_ifmap

                        out_data_per_clk = int(math.ceil(len(ifmap_buffer) / time_to_fill))

                        # Here we are using delta clock cycles to chug
                        c = t_fill_ifmap
                        while len(ifmap_buffer) > 0:
                            trace = str(c) + ", "
                            for i in range(out_data_per_clk):
                                if len(ifmap_buffer) > 0:
                                    p = ifmap_buffer.pop()
                                    trace += str(int(p)) + ", "
                            dram_ifmap.write(trace + "\n")
                            c += 1

                        t_fill_ifmap = t_drain_ifmap
                        t_drain_ifmap = clk

                #Enter new data
                ifmap_buffer.add(elems[e])

    # Write the rest of the data
    if len(filter_buffer) > 0:
        #delta = clk - last_clk_filter
        if t_fill_filter == -1:
            t_fill_filter = t_drain_filter - math.ceil(len(filter_buffer) / base_bw)

        time_to_fill = t_drain_filter - t_fill_filter

        out_data_per_clk = math.ceil(len(filter_buffer) / time_to_fill)
        c = t_fill_filter
        while len(filter_buffer) > 0:
            trace = str(c) + ", "

            for i in range(int(out_data_per_clk)):
                if len(filter_buffer) > 0:
                    p = filter_buffer.pop()
                    trace += str(int(p)) + ", "
            trace += "\n"
            dram_filter.write(trace)
            c += 1

    if len(ifmap_buffer) > 0:
        if t_fill_ifmap == -1:
            t_fill_ifmap = t_drain_ifmap - math.ceil(len(ifmap_buffer) / base_bw)

        time_to_fill = t_drain_ifmap - t_fill_ifmap

        out_data_per_clk = math.ceil(len(ifmap_buffer) / time_to_fill)
        c = t_fill_ifmap
        while len(ifmap_buffer) > 0:
            trace = str(c) + ", "

            for i in range(int(out_data_per_clk)):
                if len(ifmap_buffer) > 0:
                    p = ifmap_buffer.pop()
                    trace += str(int(p)) + ", "
            trace += "\n"
            dram_ifmap.write(trace)
            c += 1

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
