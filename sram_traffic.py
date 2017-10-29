import math


def gen_sram_write_trace(
        dimensions=4,
        v_id = [], e2 = 25, r2c = 27, v_use = 4,
        global_cycles = 0,
        sram_write_trace_file = "sram_write.csv"
    ):
        t_last_out = []

        for v in range(dimensions):
            if v == 0:
                t_last_out.append(global_cycles + dimensions)
            else:
                val =t_last_out[v-1] + 1
                t_last_out.append(val)

        num_folds = math.ceil(e2/dimensions)
        num_left = e2

        fwrite = open(sram_write_trace_file, 'a')

        for i in range(num_folds):
            d = int(min(dimensions, num_left))

            for j in range(dimensions):
                if v_id[j] > -1:
                    cycl = t_last_out[j] + max(r2c, v_use)
                    trace = str(cycl) + ", "
                    t_last_out[j] = cycl

                    for k in range(d):
                        add = v_id[j] * e2 + i * dimensions + k
                        trace += str(add) + ", "

                    fwrite.write(trace + "\n")

            num_left -= d

        fwrite.close()

def gen_trace_one_fold(
        d = 4,
        ifmap_w = 7,
        filt_w = 3,
        num_channels = 3,
        strides = 1,
        E_w = 5, r2c = 27, e2 =25, rc =9,
        sram_trace_file = "sram_read.csv",
        ifmap_base = 0,
        v_base = [], v_id = [], max_v_counts = 1,
        global_cycles = 0
    ):

    sram_read = open(sram_trace_file, 'a')

    max_v_id = max(v_id)

    v_ctr = []
    v_addr = []

    h_id   = []
    h_base = []
    h_addr = []
    slide_ctr   = 0

    for i in range(d):
        if i == 0:
            base = 0
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

        base += ifmap_base
        h_base.append(base)
        h_addr.append(base)
        h_id.append(i)

        v_ctr.append(0)
        addr = v_base[i]
        v_addr.append(addr)

    all_done = False
    all_h_done = False
    all_v_done = False
    cycles = 0

    print(global_cycles)

    while not all_done:
        ifmap_trace  = ""
        filter_trace = ""

        for i in range(d):
            adj_cycl = cycles - i

            if adj_cycl > 0:
                if adj_cycl % r2c == 0:

                    # Step 1 : Check the incremented id and slide to new base address
                    id = (h_id[i] + d)

                    if id >=e2:
                        h_id[i] = -1

                    if h_id[i] > -1:

                        if i == 0:
                            h_ind = d - 1
                        else:
                            h_ind = i - 1

                        if slide_ctr < E_w:
                            base = h_base[h_ind] + (strides * num_channels)
                            slide_ctr += 1
                        else:
                            gap = ifmap_w - filt_w - (E_w - 1) * strides
                            v_disp = (strides - 1) * ifmap_w
                            base = h_base[h_ind] + (filt_w + gap + v_disp) * num_channels
                            slide_ctr = 1  # Walkthrough to understand this

                        h_base[i] = base
                        h_addr[i] = base
                        h_id[i]   = id

                    # For all the filters
                    if v_id[i] > -1:
                        v_ctr[i] += 1

                        if v_ctr[i] < max_v_counts:
                            v_addr[i] = v_base[i]
                        else:
                            if v_id[i] == max_v_id:
                                all_v_done = True

                            v_id[i] = -1

                elif adj_cycl % rc == 0:
                    if h_id[i] > -1:
                        add = 1 + (ifmap_w - filt_w) * num_channels
                        h_addr[i] += add

                    if v_id[i] > -1:
                        v_addr[i] += 1

                else:
                    if h_id[i] > -1:
                        h_addr[i] += 1

                    if v_id[i] > -1:
                        v_addr[i] += 1

                if h_id[i] > -1:
                    ifmap_trace += str(h_addr[i]) + ", "
                else:
                    ifmap_trace += ", "

                if v_id[i] > -1:
                    filter_trace += str(v_addr[i]) + ", "
                else:
                    filter_trace += ", "

            elif adj_cycl == 0:

                if h_id[i] > -1:
                    ifmap_trace += str(h_addr[i]) + ", "
                else:
                    ifmap_trace+= ", "

                if v_id[i] > -1:
                    filter_trace += str(v_addr[i]) + ", "
                else:
                    filter_trace += ", "

            else:
                ifmap_trace += ", "
                filter_trace += ", "

        trace = str(global_cycles) + ", " + filter_trace + ifmap_trace + "\n"
        sram_read.write(trace)

        if max(h_id) == -1:
            all_h_done = True

        all_done = all_h_done and all_v_done

        global_cycles += 1
        cycles += 1

    sram_read.close()
    return global_cycles


def sram_traffic(
        dimensions=4,
        ifmap_h=7, ifmap_w=7,
        filt_h=3, filt_w=3,
        num_channels=3,
        strides=1, num_filt=8,
        filt_base=1000000,
        ifmap_base=0,
        sram_read_trace_file="sram_read.csv",
        sram_write_trace_file="sram_write.csv"
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

    # Simulation part
    global_cycles = 0

    # Delete the prev file
    f = open(sram_read_trace_file, 'w')
    f.close()

    f1 = open(sram_write_trace_file, 'w')
    f1.close()

    num_folds = math.ceil(num_filt / d)
    max_v_counts = math.ceil(e2 / d)

    v_rem = num_filt

    for fold in range(num_folds):
        v_base = []
        v_id = []

        for i in range(d):
            if i < v_rem:
                id = fold * d + i
                base = id * r2c + filt_base
            else:
                id = -1
                base = -1

            v_id.append(id)
            v_base.append(base)

        gen_sram_write_trace(
            v_id=v_id,
            e2=e2, r2c=r2c,
            global_cycles=global_cycles,
            dimensions=d, v_use=min(v_rem,d),
            sram_write_trace_file=sram_write_trace_file
        )

        global_cycles = gen_trace_one_fold(
                                    d=d,
                                    ifmap_w=ifmap_w, filt_w=filt_w,
                                    num_channels=num_channels, strides=strides,
                                    E_w=E_w, r2c=r2c, e2=e2, rc=rc,
                                    sram_trace_file=sram_read_trace_file,
                                    ifmap_base=ifmap_base,
                                    v_base=v_base, v_id=v_id, max_v_counts=max_v_counts,
                                    global_cycles=global_cycles
                            )

        global_cycles -= 1
        print(global_cycles)

        del(v_id[:])
        del(v_base[:])

        v_rem -= min(d, v_rem)


if __name__ == "__main__":
    sram_traffic(
                    dimensions=14,
                    ifmap_h=20, ifmap_w=20,
                    filt_h=3, filt_w=3,
                    num_channels=3, strides=1,
                    num_filt=16,
                    sram_read_trace_file="sram_read.csv",
                    sram_write_trace_file="sram_write.csv",
                   )