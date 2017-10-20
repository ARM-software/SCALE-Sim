
def test():
    D = 32

    H = 224
    R = 3
    C = 3
    U = 1 
    M = 96

    E = (H - R + U) / U

    n_ofmap = E * E 

    sram = 1024 * 1024  #Size of SRAM in bytes

    fmap_sram = sram / 2
    filt_sram = sram - fmap_sram

    t_fmap = fmap_sram / D


    global_cycles = 0

    all_hlane_done = False
    all_vlane_done = False

    filt_base   = 1000000
    ifmap_base  = 0

    while not(all_hlane_done and all_vlane_done):

        global_cycles += 1

        v_sram_trace = ""
        h_sram_trace = ""
        
        for v_lane in num_v_lanes:
            if global_cycles > v_lane:
                if ((global_cycles - v_lane) % r2c == 0): 
                    if (all_hlane_done == False):
                        address = v_base[v_lane]
                    else:
                        v_base[v_lane] += r2c
                        filter_done += 1

                        if(filter_done >= M):
                            trail_v -= 1
                            
                            if trail_v == 0:
                                all_v_lane_done = True
                                break
                            else:
                                address = -1
                        else:
                            address = v_base[v_lane]

                else:
                    address += 1

                if address != -1:
                    v_sram_trace += str(address + filt_base) + ", "


        for h_lane in num_h_lanes:

            if global_cycles > h_lane:
                if (global_cycles - h_lane) % r2c == 0:
                    h_base[h_lane] += U
                    
                    ofmap_done += 1
                    if ofmap_done >= e2:
                        trail_h -= 1

                        if trail_h == 0:
                            all_hlane_done = True
                            break
                        else:
                            address = -1
                    else:
                        address = h_base[h_lane]

                elif (global_cycles - h_lane) %rc == 0:
                    address += (H - 1) * rc

                else: 
                    address += 1

                if address != -1:
                    h_sram_trace += str(address + ifmap_base) + ", "

        trace = str(global_cycles) + ", " + v_sram_trace + h_sram_trace + "\n"
        sram.write(trace)

