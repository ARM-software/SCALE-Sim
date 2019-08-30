import numpy as np

####input is s1, s2, T
#####output is the ifmap trace, filter trace, and ofmap trace
#hyperparameters: systolic array size (cols, rows)
#hyper_parameter: s1 (in this case, pixels in filter)
#hyper_parameter: s2 (in this case, # of filters)
#hyper_parameter: T (in this case ofmap pixels (=(ifmap_rows-filter_rows+1)/1))
class simulation:
    def __init__(self, s2, T):
        self.left_column = np.zeros((1, T))
        self.top_row = np.zeros((1, s2))


class sram_trace_generator:
    def __init__(self):
        self.filt_h = 3
        self.filt_w = 3
        self.ifmap_h = 5
        self.ifmap_w = 5
        self.ofmap_h = 3
        self.ofmap_w = 3

    sysarray_rows = 4
    sysarray_cols = 4
    top_row = np.zeros((1, sysarray_cols))
    left_col = np.zeros((1, sysarray_rows))
    cycles = 0

    def simulate_sram_trace(self, input, filter):
        simArray = []
        for cycle in range(min(len(input[0]), len(filter[0]))):
            sim = simulation(s2=len(filter), T=len(input))
            sim.left_column = np.transpose(input[:,cycle])
            sim.top_row = np.transpose(filter[:,cycle])
            simArray.append(sim)
        return simArray


    #def noSkewMat(inpMatrix):


    def skewMat(self, inpMatrix):
        returnMatrix = np.ones((len(inpMatrix),(len(inpMatrix[0])+len(inpMatrix)-1)))*-1
        for i in range(len(inpMatrix)):
            for j in range(len(inpMatrix[0])):
                returnMatrix[i][i + j] = inpMatrix[i][j]
        return returnMatrix


    def read_trace_arrays_os(self, s1, s2, T, stride):
        filter = np.zeros((s2, s1))
        ifmap = np.zeros((T, s1))
        filter_base = 0
        temp_filt = filter_base
        ##populate the filter input matrix
        for i in range(s2):
            for j in range(s1):
                filter[i][j] = temp_filt
                temp_filt = temp_filt + 1

        ##populate the ifmap input matrix
        input_base = 0
        temp_ifmap = input_base
        first_address = temp_ifmap
        start_row = input_base
        for i in range(T):
            for j in range(s1):
                ifmap[i][j] = temp_ifmap
                temp_ifmap = temp_ifmap + 1
                if (j + 1) % self.ofmap_w == 0:
                    temp_ifmap = int(temp_ifmap/self.ifmap_w) + self.ifmap_w
            if (i + 1) % self.ofmap_h == 0:
                first_address = int(first_address/self.ifmap_w) + self.ifmap_w*stride
            else:
                first_address = first_address + stride
            temp_ifmap = first_address
        return ifmap, filter

if __name__ == "__main__":
    s = sram_trace_generator()
    (ifmap, filter) = s.read_trace_arrays_os(9, 4, 9, stride = 1)
    input = s.skewMat(ifmap)
    filter = s.skewMat(filter)
    simArray = s.simulate_sram_trace(input, filter)
    print("herel")




















