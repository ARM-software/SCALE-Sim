import math

def gen_sram_trace(
        dimensions = 4,
        ifmap_h = 7, ifmap_w = 7,
        filt_h  = 3, filt_w = 3,
        num_channels = 3,
        strides = 1, num_filt = 8,
        sram_trace_file = "sram_log.csv",
        sram_write_trace_file = "sram_write.csv"
):

    E_h = (ifmap_h - filt_h + strides) / strides
    E_w = (ifmap_w - filt_w + strides) / strides

    e2 = E_h * E_w
    r2c = filt_h * filt_h * num_channels
    rc = filt_w * num_channels
    h2 = ifmap_w * ifmap_h

    num_h_lanes = min(dimensions, e2)
    num_v_lanes = min(dimensions, num_filt)

    d = min(num_h_lanes, num_v_lanes)
    num_h_lanes = d
    num_v_lanes = d

    sram = open(sram_trace_file, 'w')

    # Simulation part
    global_cycles = 0

    filt_base = 1000000
    ifmap_base = 0

    all_hlane_done = False
    all_vlane_done = False
    more_filters_remaining = True
    slide_ctr = 0

    h_base  = []
    #v_base  = []
    h_id    = []
    v_id    = []
    address_h_lane = []
    address_v_lane = []
    v_ctr = []
    new_window = []
    write_traces = []

    # Initialize h lane stuff here
    for i in range(num_h_lanes):
        h_id.append(i)
        new_window.append(True)

        if i == 0:
            h_base.append(0)
            address_h_lane.append(0)
            slide_ctr += 1

        else:
            if slide_ctr < E_w:
                base = h_base[i - 1] + (strides * num_channels)
                slide_ctr += 1
            else:
                gap = ifmap_w - filt_w - (E_w - 1) * strides
                v_disp = (strides - 1) * ifmap_w
                base = h_base[i - 1] + (filt_w + gap + v_disp) * num_channels
                slide_ctr = 1  # Walkthrough to understand this

            address_h_lane.append(base)
            h_base.append(base)


    #Initialize v lane stuff here
    for i in range(num_v_lanes):
        v_id.append(i)
        base_address = filt_base + i * r2c
        address_v_lane.append(base_address)
        v_ctr.append(0)

    max_id_vlane = max(v_id)
    v_ctr_max_val = math.ceil(e2 / num_h_lanes)

    while not(all_hlane_done and all_vlane_done):
        v_sram_trace = ""
        h_sram_trace = ""

        #if (all_hlane_done == True) and (max_id_vlane < num_filt - 1):
        if (all_hlane_done == True) and (more_filters_remaining == True):
            h_base[0] = 0
            address_h_lane[0] = h_base[0]
            all_hlane_done = False
            slide_ctr = 0
            for i in range(num_h_lanes):
                h_id[i] = i
                if i > 0:
                    h_id[i] -= num_h_lanes

        if all_vlane_done == False:
            for v in range(num_v_lanes):
                if global_cycles - v >= 0:

                    if (address_v_lane[v] != -1):
                        v_sram_trace += str(address_v_lane[v]) + ", "
                    else:
                        v_sram_trace += " , "

                    if ((global_cycles - v + 1) % r2c == 0) and (v_id[v] > -1):
                        v_ctr[v] += 1

                        if v_ctr[v] == v_ctr_max_val:
                            v_ctr[v] = 0

                            id = v_id[v] + num_v_lanes
                            address = address_v_lane[v] + 1 + (num_v_lanes - 1) * r2c

                            if id >= num_filt:
                                id = -1
                                address = -1

                                if v_id[v] == num_filt - 1:
                                    all_vlane_done = True

                            v_id[v] = id
                            address_v_lane[v] = address

                        else:
                            address = address_v_lane[v] - (r2c - 1)
                            address_v_lane[v] = address

                    else:
                        if v_id[v] > -1:
                            address_v_lane[v] += 1


        if all_hlane_done == False:
            for h in range(num_h_lanes):
                if global_cycles - h >= 0:
                    # If valid then print
                    if (address_h_lane[h] > -1):
                        h_sram_trace += str(address_h_lane[h]) + ", "
                    else:
                        h_sram_trace += " , "

                    #update for the next cycle
                    if (global_cycles - h + 1) % r2c == 0:
                        id = (h_id[h] + num_h_lanes)

                        if h == 0: h_ind = num_h_lanes - 1
                        else: h_ind = h - 1

                        if slide_ctr < E_w:
                            base = h_base[h_ind] + (strides * num_channels)
                            slide_ctr += 1
                        else:
                            gap = ifmap_w - filt_w - (E_w - 1) * strides
                            v_disp = (strides - 1) * ifmap_w
                            base = h_base[h_ind] + (filt_w + gap + v_disp) * num_channels
                            slide_ctr = 1               # Walkthrough to understand this

                        if id >= e2:
                           id = -1
                           base = -1

                           if h_id[h] == e2 - 1:
                                all_hlane_done = True
                                slide_ctr = 0

                        if id > -1:
                            new_window[h] = True

                        h_id[h] = id
                        h_base[h] = base
                        address_h_lane[h] = h_base[h]

                    elif (global_cycles - h + 1) % rc == 0:
                        # We are controlling vertical fold with negative addresses
                        # Therefore this
                        if address_h_lane[h] > -1:
                            address = address_h_lane[h] + 1 + (ifmap_w - filt_w) * num_channels
                            address_h_lane[h] = address

                    else:
                        if h_id[h] > -1:
                            address_h_lane[h] += 1

                        # Handle the initial conditions of a new vertical fold
                        elif address_h_lane[h] == 0:
                            address_h_lane[h] = h_base[h]


                    if new_window[h] == True:
                        for v in range(num_v_lanes):
                            ofmap_addr = h_id[h] * num_filt + v_id[v]
                            clk  = global_cycles + v + r2c
                            write_traces.append([clk, ofmap_addr])

                        new_window[h] = False

        trace = str(global_cycles) + ", " + v_sram_trace + h_sram_trace + "\n"
        sram.write(trace)

        global_cycles += 1

        #if global_cycles >= 376:
        #   print("Break")

        max_id_vlane = max(v_id)

        # This needs to be cleaner
        if max_id_vlane == num_filt - 1:
            ind = v_id.index(max_id_vlane)
            if v_ctr[ind] == v_ctr_max_val - 1:
                more_filters_remaining = False
            else:
                more_filters_remaining = True
        else:
            more_filters_remaining = True

    #print(str(len(write_traces)))
    #for i in range(len(write_traces)):
    #    print(write_traces[i])
    write_traces = sorted(write_traces, key=lambda x: x[0])
    #for i in range(len(write_traces)):
    #    print(write_traces[i])
    #print(str(len(write_traces)))

    last_clk = -1
    addr_list = ""
    sram_write = open(sram_write_trace_file, 'w')

    for entry in write_traces:
        clk = entry[0]
        addr = entry[1]
        #print(str(clk) + ", " + str(addr))

        if clk == last_clk:
            addr_list += str(addr) +", "
        else:
            addr_list += " \n"
            #print(addr_list)
            sram_write.write(addr_list)

            addr_list = str(clk) + ", " + str(addr) + ", "
            last_clk = clk

    sram_write.close()
    sram.close()

if __name__ == "__main__":

    gen_sram_trace(dimensions=32,
                   ifmap_h=418, ifmap_w=418,
                   filt_h=3, filt_w=3,
                   num_channels=3, strides=1,
                   num_filt=16, sram_trace_file="yolo_tiny_layer1.csv", sram_write_trace_file="yolo_tiny_layer1_write.csv")

    #gen_sram_trace()