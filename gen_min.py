import os

#net_name = "resnet1_int8"
#net_name = "yolo_v2"
net_name = "yolo_tiny"

dump_file = net_name + "_min.csv"

command = "ls " + net_name + "/ > tmp"
os.system(command)

lst = open("tmp", 'r')
min_file = open(dump_file, 'a')

for fname in lst:
    fname = fname.strip()
    fname = net_name +"/" + fname

    f = open(fname, 'r')
    first = True
    min_cycl= 1000000000
    min_dim = ""

    for l in f:
        if first:
            first = False
        else:
            entry = l.strip().split(',')

            cycl = float(entry[1])
            #print(entry[0])

            if cycl < min_cycl:
                min_cycl = cycl
                min_dim = entry[0]

    log = min_dim + "\n"
    print(log)
    min_file.write(log)

    f.close()

lst.close()
min_file.close()

command = "rm -rf tmp"
os.system(command)
