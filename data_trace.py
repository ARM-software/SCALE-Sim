
def gen_sram_trace(dimentions = 4,
                    ifmap_h = 9, ifmap_w = 9,
                    filt_h = 3, filt_w = 3,
                    num_channels = 3 ,
                    strides = 1, num_filt =8,
                    sram_trace_file = "sram.log"
         ):
    num_h_lanes = dimentions
    num_v_lanes = dimentions

    E_h = (ifmap_h - filt_h + strides) / strides
    E_w = (ifmap_w - filt_w + strides) / strides

    e2  = E_h * E_w
    r2c = filt_h * filt_h * num_channels
    rc  = filt_w * num_channels

    trail_h = (dimentions - 1) * (dimentions - 2) / 2
    trail_v = trail_h

    sram = open(sram_trace_file, 'w')

    # Simulation part
    global_cycles = 0

    filt_base   = 1000000
    ifmap_base  = 0

    all_hlane_done  = False
    all_vlane_done = False
    ofmap_done      = 0
    filter_done     = 0

    h_base = []
    address_hlane = []
    for i in range(num_h_lanes):
        base_address = ifmap_base + i * (strides * num_channels)
        #base_address = 0
        h_base.append(base_address)
        address_hlane.append(base_address)

    v_base = []
    address_vlane = []
    for i in range(num_v_lanes):
        base_address = filt_base + i * r2c
        #base_address = 0
        v_base.append(base_address)
        address_vlane.append(base_address)


    while not(all_hlane_done and all_vlane_done):

        v_sram_trace = ""
        h_sram_trace = ""
        
        for h_lane in range(num_h_lanes):

            if global_cycles >= h_lane:
                if global_cycles == h_lane:
                    pass
                elif ((global_cycles - h_lane) % r2c == 0):
                    h_base[h_lane] += strides * num_channels    # UC
                    
                    ofmap_done += 1
                    if ofmap_done >= e2:
                        trail_h -= 1

                        if trail_h == 0:
                            all_hlane_done = True
                            address_hlane[h_lane] = -1
                            break
                        else:
                            address_hlane[h_lane] = -1
                    else:
                        address_hlane[h_lane] = h_base[h_lane]

                elif ((global_cycles - h_lane) %rc == 0):
                    address_hlane[h_lane] += (ifmap_w - 1) * rc

                else: 
                    address_hlane[h_lane] += 1

                if address_hlane[h_lane] != -1:
                    h_sram_trace += str(address_hlane[h_lane]) + ", "

        for v_lane in range(num_v_lanes):
            if global_cycles >= v_lane:
                if global_cycles == v_lane:
                    pass
                elif (global_cycles - v_lane) % r2c == 0:
                    if (all_hlane_done == False):
                        address_vlane[v_lane] = v_base[v_lane]
                    else:
                        v_base[v_lane] += r2c
                        filter_done += 1

                        if (filter_done >= num_filt):
                            trail_v -= 1

                            if trail_v == 0:
                                all_vlane_done = True
                                address_vlane[v_lane] = -1
                                break
                            else:
                                address_vlane[v_lane] = -1
                        else:
                            address_vlane[v_lane] = v_base[v_lane]

                else:
                    address_vlane[v_lane] += 1

                if address_vlane[v_lane] != -1:
                    v_sram_trace += str(address_vlane[v_lane]) + ", "

        global_cycles += 1
        trace = str(global_cycles) + ", " + v_sram_trace + h_sram_trace + "\n"
        sram.write(trace)

        if all_hlane_done == True and all_vlane_done == False:
            all_hlane_done = False
            ofmap_done = 0

    # End of while loop
    sram.close()


if __name__ == "__main__":
    gen_sram_trace()
