import os
import time
import configparser as cp
import run_nets as r


class scale:
    def parse_config(self):
        arch_sec = 'architecture_presets'
        net_sec  = 'network_presets'
        config_filename = "./scale.cfg"
    
        config = cp.ConfigParser()
        config.read(config_filename)
    
        ## Read the architecture_presets
        ## Array height min, max
        ar_h = config.get(arch_sec, 'ArrayHeight').split(',')
        self.ar_h_min = ar_h[0].strip()
    
        if len(ar_h) > 1:
            self.ar_h_max = ar_h[1].strip()
        #print("Min: " + ar_h_min + " Max: " + ar_h_max)
    
        ## Array width min, max
        ar_w = config.get(arch_sec, 'ArrayWidth').split(',')
        self.ar_w_min = ar_w[0].strip()
        
        if len(ar_w) > 1:
            self.ar_w_max = ar_w[1].strip()
    
        ## IFMAP SRAM buffer min, max
        ifmap_sram = config.get(arch_sec, 'IfmapSramSz').split(',')
        self.isram_min = ifmap_sram[0].strip()
        
        if len(ifmap_sram) > 1:
            self.isram_max = ifmap_sram[1].strip()
       
    
        ## FILTER SRAM buffer min, max
        filter_sram = config.get(arch_sec, 'FilterSramSz').split(',')
        self.fsram_min = filter_sram[0].strip()
        
        if len(filter_sram) > 1:
            self.fsram_max = filter_sram[1].strip()
        
        
        ## OFMAP SRAM buffer min, max
        ofmap_sram = config.get(arch_sec, 'OfmapSramSz').split(',')
        self.osram_min = ofmap_sram[0].strip()
        
        if len(ofmap_sram) > 1:
            self.osram_max = ofmap_sram[1].strip()
    
    
        ## Read network_presets
        ## For now that is just the topology csv filename
        topology_file = config.get(net_sec, 'TopologyCsvLoc')
        self.topology_file = topology_file.split('"')[1]     #Config reads the quotes as well 


    def run_scale(self):
        self.parse_config()
        print("====================================================")
        print("******************* SCALE SIM **********************")
        print("====================================================")
        print("Array Size: \t" + str(self.ar_h_min) + "x" + str(self.ar_w_min))
        print("SRAM IFMAP: \t" + str(self.isram_min))
        print("SRAM Filter: \t" + str(self.fsram_min))
        print("SRAM OFMAP: \t" + str(self.osram_min))
        print("CSV file path: \t" + self.topology_file)
        print("====================================================")

        net_name = self.topology_file.split('/')[-1].split('.')[0]
        #print("Net name = " + net_name)
        
        r.run_net(  ifmap_sram_size  = int(self.isram_min),
                    filter_sram_size = int(self.fsram_min),
                    ofmap_sram_size  = int(self.osram_min),
                    array_h = int(self.ar_h_min),
                    array_w = int(self.ar_w_min),
                    net_name = net_name,
                    topology_file = self.topology_file
                )
        
        self.cleanup()
        print("************ SCALE SIM Run Complete ****************") 


    def cleanup(self):
        if not os.path.exists("./outputs/"):
            os.system("mkdir ./outputs")
        
        net_name = self.topology_file.split('/')[-1].split('.')[0]
        path = "./outputs/" + net_name

        if not os.path.exists(path):
            os.system("mkdir " + path)
        else:
            t = time.time()
            new_path= path + "_" + str(t)
            os.system("mv " + path + " " + new_path)
            os.system("mkdir " + path)


        cmd = "mv *.csv " + path
        os.system(cmd)

        cmd = "mkdir " + path +"/layer_wise"
        os.system(cmd)

        cmd = "mv " + path +"/*Conv* " + path +"/layer_wise"
        os.system(cmd)

if __name__ == "__main__":
    s = scale()
    s.run_scale()

    
