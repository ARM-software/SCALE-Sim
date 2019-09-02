import numpy as np
import multiprocessing as mp
from multiprocessing import Array, Process

# output is the ifmap trace, filter trace, and ofmap
# hyper parameters: systolic array size (cols, rows)
# hyper_parameter: s1 (pixels in filter)
# hyper_parameter: s2 (# of filters)
# hyper_parameter: T (ofmap pixels in one channel (=(ifmap_rows-filter_rows+stride)/stride))


def read_filters(i, j, s1, filter):
    filter_base = 1000
    filter[i*s1 + j] = filter_base + i * s1 + j

def read_ifmap(i, j, self.T, self.stride, ifmap, temp_ifmap):




class simulation:
    def __init__(self, s2, T):
        self.left_column = np.zeros((1, T))
        self.top_row = np.zeros((1, s2))


class sram_trace_generator:
    def __init__(self, stride=1, filt_h=2, filt_w=2,
                 ifmap_h=3, ifmap_w=3, num_filters=4, num_channels=1):
        self.stride = stride  # input
        self.filt_h = filt_h  # input
        self.filt_w = filt_w  # input
        self.num_channels = num_channels  # input
        self.ifmap_h = ifmap_h  # input
        self.ifmap_w = ifmap_w  # input
        self.num_filters = num_filters  # input
        self.ofmap_h = int((self.ifmap_h - self.filt_h + self.stride)/self.stride)
        self.ofmap_w = int((self.ifmap_w - self.filt_w + self.stride)/self.stride)
        self.s1 = self.filt_h * self.filt_w * self.num_channels
        self.s2 = self.num_filters
        self.T = self.ofmap_h * self.ofmap_w

    def simulate_sram_trace(self, input, filter):
        output = np.ones((self.T + self.s2 - 1, self.s2))*(-1)
        outputBase = 0
        outputPixel = outputBase
        simArray = []
        filtersArray = []
        start = False
        increasing = True
        for cycle in range(self.T + self.s2 + self.s1):
            if cycle < min(len(input[0]), len(filter[0])):
                sim = simulation(s2=self.s2, T=self.T)
                sim.left_column = np.transpose(input[:, cycle])
                sim.top_row = np.transpose(filter[:, cycle])
                simArray.append(sim)
            outputCycle = cycle - self.s1
            if outputCycle == 0:
                start = True
            elif outputCycle == self.T:
                increasing = False
            if start:
                if increasing:
                    filtersArray.append(len(filtersArray))
                elif len(filtersArray) > 0:
                    filtersArray.pop(0)
                    outputPixel = outputPixel + self.T - 1
                for i in range(len(filtersArray)):
                    output[outputCycle][filtersArray[i]] = outputPixel + ((self.T - 1) * i)
                outputPixel = outputPixel + 1
        return simArray, output


    def noSkewMat(self, inpMatrix):
        returnMatrix = np.ones(((len(inpMatrix) - len(inpMatrix[0]) + 1), len(inpMatrix[0])))
        for i in range(len(returnMatrix)):
            for j in range(len(returnMatrix[0])):
                returnMatrix[i][j] = inpMatrix[i + j][j]
        return returnMatrix


    def skewMat(self, inpMatrix):
        returnMatrix = np.ones((len(inpMatrix), (len(inpMatrix[0])+len(inpMatrix)-1)))*-1
        for i in range(len(inpMatrix)):
            for j in range(len(inpMatrix[0])):
                returnMatrix[i][i + j] = inpMatrix[i][j]
        return returnMatrix


    def read_trace_arrays_os(self):
        filter = Array('i', self.s1*self.s2)
            #np.zeros((self.s2, self.s1))
        filter_base = 0
        jobs = []
        # populate the filter input matrix
        for i in range(self.s2):
            for j in range(self.s1):
                process = Process(target=read_filters, args=(i, j, self.s1, filter))
                jobs.append(process)
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        filter = np.reshape(filter[:], (self.s2, self.s1))
        print(filter)
        # populate the ifmap input matrix
        #ifmap = np.zeros((self.T, self.s1))
        filter = Array('i', self.T*self.s1)
        input_base = 0
        temp_ifmap = input_base
        first_address = temp_ifmap
        for i in range(self.T):
            for j in range(self.s1):
                process = Process(target=read_ifmap, args=(i, j, self.T, self.stride, ifmap, temp_ifmap))
                jobs.append(process)
                ifmap[i][j] = temp_ifmap
                temp_ifmap = temp_ifmap + 1
                if (j + 1) % self.ofmap_w == 0:
                    temp_ifmap = int(temp_ifmap/self.ifmap_w) + self.ifmap_w
            if (i + 1) % self.ofmap_h == 0:
                first_address = int(first_address/self.ifmap_w) + self.ifmap_w*self.stride
            else:
                first_address = first_address + self.stride
            temp_ifmap = first_address
        return ifmap, filter


if __name__ == "__main__":
    s = sram_trace_generator()
    (ifmap, filter) = s.read_trace_arrays_os()
    input = s.skewMat(ifmap)
    filter = s.skewMat(filter)
    (simArray, output) = s.simulate_sram_trace(input, filter)
    unskewedOutput = s.noSkewMat(output)
    for i in range(len(simArray)):
        print("Inputs at Cycle " + str(i) + ":")
        print(simArray[i].left_column)
        print("Filters at Cycle " + str(i) + ":")
        print(simArray[i].top_row)
    print("Outputs Skewed: ")
    print(output)
    print("Outputs Unskewed: ")
    print(unskewedOutput)