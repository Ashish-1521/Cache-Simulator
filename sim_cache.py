import Cache as cache
import sys

if len(sys.argv)<8:
    print("Passed incorrect number of vals")
else:
    block_size = int(sys.argv[1])
    L1_Size = int(sys.argv[2])
    L1_Assoc = int(sys.argv[3])
    L2_Size = int(sys.argv[4])
    L2_Assoc = int(sys.argv[5])
    replacement_policy = int(sys.argv[6])
    inclusion_property = int(sys.argv[7])
    trace_File = sys.argv[8]

    
c = cache.Cache_Simulation(block_size,L1_Size,L1_Assoc,L2_Size,L2_Assoc,replacement_policy,inclusion_property,trace_File)

print("===== L1 contents =====")
for i in range(int(c.no_sets[1])):
  res = "".join("{} {} ".format(x[2:],y) for x, y in zip(c.L1_Cache_Mem[i], c.L1_dirtyBits[i]))
  print("Set  {} :\t{}\t".format(i,res))



if c.has_L2:
    print("===== L2 contents =====")
    for i in range(int(c.no_sets[2])):
        res = " ".join("{} {} ".format(x[2:],y) for x, y in zip(c.L2_Cache_Mem[i], c.L2_dirtyBits[i]))
        print("Set  {} :\t{}\t".format(i,res))
c.printResults()
