import math
f = open("output.txt","w")
class Cache_Simulation:
    block_Size = 0
    L1_Size =0 
    L1_Asso = 0
    L2_Size=0
    L2_Asso=0
    replacement_policy = 0
    inclusion_property = 0
    file_name = "none"
    number_of_sets = [0]
    index_bits = [0]
    block_offset_bits = 0
    tag_bits = [0]
    cache_L1_memory = {}
    cache_L2_memory = {}
    time_counter_LRU = {}
    no_l1_reads = 0
    no_l1_reads_miss = 0
    no_l1_writes = 0
    no_l1_write_miss=0
    no_l1_writeBacks = 0

    no_l2_reads = 0
    no_l2_reads_miss = 0
    no_l2_writes = 0
    no_l2_write_miss=0
    has_L2 = False
    no_l2_writeBacks = 0

    time_counter_L1 = {}
    time_counter_L2 = {}
    dirtyBits_L1 = {}
    dirtyBits_L2 = {}
    Enter_L2 = False
    L2_OverallMissCount = 0
    L2_WriteBackCount = 0

    t_add_L1 = 0
    t_add_L2 = 0
    index_set_L1 = 0
    index_set_L2 = 0
    is_in_L2 = False

    reset_File_Mode = False
    
    invalid_blocks = {}
    make_invalid = False



    # Initializing values
    def __init__(self,blockSize,L1Size,L1Assoc,L2Size,L2Assoc,replacementpolicy,inclusionProperty,file):
        self.block_Size = blockSize
        self.L1_Size = L1Size
        self.L1_Asso = L1Assoc
        self.L2_Size = L2Size
        self.L2_Asso = L2Assoc
        self.replacement_policy = replacementpolicy
        self.inclusion_property = inclusionProperty
        self.file_name = file
        self.simulation_Configuration()
        self.Calculate_address_Fields_Widths()
    
    #Simulation Configuration
    def simulation_Configuration(self):
        f.write("===== Simulator configuration =====\n")
        f.write("BlockSize = {}\n".format(self.block_Size))
        f.write("L1 Size = {}\n".format(self.L1_Size))
        f.write("L1 Assoc = {}\n".format(self.L1_Asso))
        f.write("L2 Size = {}\n".format(self.L2_Size))
        f.write("L2 Assoc = {}\n".format(self.L2_Asso))
        f.write("Replacement_policy = {}\n".format(self.replacement_policy))
        f.write("Inclusion Property = {}\n".format(self.inclusion_property))
        f.write("Trace file = {}\n".format(self.file_name))
    
    # Calculating address fields sizes
    def Calculate_address_Fields_Widths(self):
        sets_L1 = (self.L1_Size)/(self.block_Size*self.L1_Asso)
        # print("L1 sets = ",sets_L1)
        index_bits_l1 = int(math.log(sets_L1,2))
        # print("index bits l1 = ",index_bits_l1)
        block_offset = int(math.log(self.block_Size,2))
        tag_bits_l1 = 32-index_bits_l1-block_offset
        # print("tag bits l1 = ",tag_bits_l1)

        self.number_of_sets.append(int(sets_L1))
        self.index_bits.append(index_bits_l1)
        self.tag_bits.append(tag_bits_l1)

        if self.L2_Size!=0:
            sets_L2 = (self.L2_Size)/(self.block_Size*self.L2_Asso)
            # print("L2 sets = ",sets_L2)
            index_bits_l2 = int(math.log(sets_L2,2))
            # print("index bits l2 = ",index_bits_l2)
            tag_bits_l2 = 32-index_bits_l2-block_offset
            # print("tag bits l2 = ",tag_bits_l2)
            self.number_of_sets.append(int(sets_L2))
            self.index_bits.append(index_bits_l2)
            self.tag_bits.append(tag_bits_l2)
            self.has_L2 = True

        print("Sets = ",self.number_of_sets)
        print("index bits = ",self.index_bits)
        print("tag bits = ",self.tag_bits)
        print("offset bits = ",block_offset)
        self.Calculate_addresses()

    # Calculating addresses
    def Calculate_addresses(self):
        trace_File = open(self.file_name,"r")
        for l in trace_File.readlines():
            lst = l.strip().split(" ")
            file_mode = l[0]
            while len(lst[1])<8:
                lst[1] = "0" + lst[1]
            bin_address = bin(int(lst[1],16))
            bin_address = bin_address[2:]
            while len(bin_address)<len(lst[1])*4:
                bin_address = "0"+bin_address
           
           
            self.t_add_L1 = hex(int(bin_address[:self.tag_bits[1]],2))
            self.index_set_L1 = int(bin_address[(self.tag_bits[1]):(self.tag_bits[1]+self.index_bits[1])],2)

            if self.has_L2:
                self.t_add_L2 = hex(int(bin_address[:self.tag_bits[2]],2))
                self.index_set_L2 = int(bin_address[(self.tag_bits[2]):(self.tag_bits[2]+self.index_bits[2])],2)


            # f.write(" bin = {}\n".format(bin_address))
            # f.write("lst = {}\n".format(lst))
            # f.write("Set = {}\n".format(self.index_set_L1))
            # f.write("tag_add = {}\n".format(self.t_add_L1))
            # f.write("Org add = {}\n".format(lst[1]))

            if self.inclusion_property == 0:
                self.is_in_L2=False
                self.cache_L1_memory[self.index_set_L1],self.time_counter_L1[self.index_set_L1],hit_status,self.dirtyBits_L1[self.index_set_L1],wb_c_1 = self.Replacement_Policy(self.index_set_L1,self.t_add_L1,file_mode,self.cache_L1_memory,self.time_counter_L1,self.L1_Asso,self.dirtyBits_L1)
                f.write("L1 hit status = {}\n".format(hit_status))
                f.write("Dirty Status = {}\n".format(self.dirtyBits_L1[self.index_set_L1]))
                f.write("\n")
                self.no_l1_writeBacks += wb_c_1
                self.Calculating_Hits_L1(file_mode,hit_status)
                self.Enter_L2 = hit_status
    
                if self.has_L2 and not self.Enter_L2:
                    self.is_in_L2 = True
                    if self.reset_File_Mode == True:
                        file_mode = 'r'
                    self.cache_L2_memory[self.index_set_L2],self.time_counter_L2[self.index_set_L2],hit_status,self.dirtyBits_L2[self.index_set_L2],wb_c_2 = self.Replacement_Policy(self.index_set_L2,self.t_add_L2,file_mode,self.cache_L2_memory,self.time_counter_L2,self.L2_Asso,self.dirtyBits_L2)
                    f.write("L2 hit status = {}\n".format(hit_status))
                    if hit_status==False:
                        self.L2_OverallMissCount +=1
                    # if self.reset_File_Mode==True:
                    #     self.Calculating_Hits_L2('w',hit_status)
                    # elif self.reset_File_Mode==False:
                    self.Calculating_Hits_L2(file_mode,hit_status)
                    self.reset_File_Mode = False  
                    self.no_l2_writeBacks += wb_c_2
                    self.is_in_L2 = False
                    # self.Calculating_Hits(file_mode,hit_status)
            
            elif self.inclusion_property == 1:
                self.is_in_L2=False
                self.cache_L1_memory[self.index_set_L1],self.time_counter_L1[self.index_set_L1],hit_status,self.dirtyBits_L1[self.index_set_L1],wb_c_1 = self.Replacement_Policy_Inclusion(self.index_set_L1,self.t_add_L1,file_mode,self.cache_L1_memory,self.time_counter_L1,self.L1_Asso,self.dirtyBits_L1)
                f.write("L1 hit status = {}\n".format(hit_status))
                f.write("Dirty Status = {}\n".format(self.dirtyBits_L1[self.index_set_L1]))
                f.write("\n")
                self.no_l1_writeBacks += wb_c_1
                self.Calculating_Hits_L1(file_mode,hit_status)
    
                if self.has_L2:
                    self.is_in_L2 = True
                    if self.reset_File_Mode == True:
                        file_mode = 'r'
                    self.cache_L2_memory[self.index_set_L2],self.time_counter_L2[self.index_set_L2],hit_status,self.dirtyBits_L2[self.index_set_L2],wb_c_2 = self.Replacement_Policy_Inclusion(self.index_set_L2,self.t_add_L2,file_mode,self.cache_L2_memory,self.time_counter_L2,self.L2_Asso,self.dirtyBits_L2)
                    f.write("L2 hit status = {}\n".format(hit_status))
                    if hit_status==False:
                        self.L2_OverallMissCount +=1
                    # if self.reset_File_Mode==True:
                    #     self.Calculating_Hits_L2('w',hit_status)
                    # elif self.reset_File_Mode==False:
                    self.Calculating_Hits_L2(file_mode,hit_status)
                    self.reset_File_Mode = False  
                    self.no_l2_writeBacks += wb_c_2
                    self.is_in_L2 = False
                    # self.Calculating_Hits(file_mode,hit_status)

                    


    def Calculate_DirtyTag(self,tag_add,index_):
        t1_len = len(str(index_))
        index_ = bin(index_)
        index_ = index_[2:]
        while len(index_)<self.index_bits[1]:
            index_ = "0"+index_
        t_len = len(tag_add[2:])
        tag_add = bin(int(tag_add,16))
        tag_add = tag_add[2:]
        while len(tag_add)<self.tag_bits[1]:
            tag_add = "0"+tag_add
        bb = tag_add+index_
        # while len(bb)<32:
        #     bb = "0"+bb
        f.write("======== bin add = {} len = {} index_bits={} index_ = {} tag_add = {}\n".format(bb,t_len,self.index_bits,index_,tag_add))
        L2_add = hex(int(bb[:self.tag_bits[2]],2))
        L2_index = int(bb[(self.tag_bits[2]):(self.tag_bits[2]+self.index_bits[2])],2)
        f.write("======== after Dirty Tag = {} set = {}\n".format(L2_add,L2_index))
        return L2_add,L2_index
    

    # LRU and FIFO Simulation
    def Replacement_Policy(self,set_no,tag_add,f_mode,cache_memory,cache_counter,Assoc,dirty_bit_container):
        lst_ = []
        lst_counter = []
        dirt_lst = []
        hit_ = False
        temp_counter = 0
        if set_no not in cache_memory:
            lst_.append(tag_add)
            lst_counter.append(0)
            # self.Is_Dirty(f_mode,index_)
            if f_mode=='w':
                dirt_lst.append('D')
            elif f_mode=='r':
                dirt_lst.append('')
        elif set_no in cache_memory:
            lst_ = cache_memory[set_no]
            lst_counter = cache_counter[set_no]
            dirt_lst = dirty_bit_container[set_no]
            if tag_add in lst_:
                if self.replacement_policy == 0:
                    index_ = lst_.index(tag_add)
                    lst_counter[index_] = max(lst_counter)+1
                hit_ = True
                # self.Is_Dirty(f_mode,index_)
                if f_mode == 'w':
                    dirt_lst[index_] = 'D'
                # elif f_mode == 'r':
                #     dirt_lst[index_] = ''
            if tag_add not in lst_:
                if len(cache_memory[set_no])<Assoc:
                    lst_.append(tag_add)
                    lst_counter.append(max(lst_counter)+1)
                    # self.Is_Dirty(f_mode,index_)
                    if f_mode=='w':
                        dirt_lst.append('D')
                    elif f_mode=='r':
                        dirt_lst.append('')
                elif len(cache_memory[set_no])==Assoc:
                    index_ = lst_counter.index(min(lst_counter))
                    writeBack_tag_add = lst_[index_]
                    lst_[index_] = tag_add
                    # f.write("Lst counter = {}\n".format(lst_counter))
                    lst_counter[index_] = max(lst_counter)+1
                    if dirt_lst[index_] == 'D':
                        temp_counter += 1
                        if self.has_L2 and not self.reset_File_Mode and not self.is_in_L2:
                            self.is_in_L2 = True
                            f.write("****** Before Dirty Tag = {} set = {}\n".format(writeBack_tag_add,set_no))
                            D_tag_add,D_index =self.Calculate_DirtyTag(writeBack_tag_add,set_no)
                            self.cache_L2_memory[D_index],self.time_counter_L2[D_index],hit_status_2,self.dirtyBits_L2[D_index],wb_cc = self.Replacement_Policy(D_index,D_tag_add,'w',self.cache_L2_memory,self.time_counter_L2,self.L2_Asso,self.dirtyBits_L2)
                            f.write("L2 hit status during writeback = {}\n".format(hit_status_2))
                            self.reset_File_Mode = True
                            if hit_status_2==False:
                                self.L2_OverallMissCount +=1
                            if self.reset_File_Mode and dirt_lst[index_]=='D':
                                self.Calculating_Hits_L2('w',hit_status_2)
                            self.no_l2_writeBacks += wb_cc 
                    # self.Is_Dirty(f_mode,index_)
                    if f_mode == 'w':
                        dirt_lst[index_] = 'D'
                    elif f_mode == 'r':
                        dirt_lst[index_] = ''
        # cache_counter[set_no] = lst_
        # cache_counter[set_no] = lst_counter
        return lst_,lst_counter,hit_,dirt_lst,temp_counter
    

    def Replacement_Policy_Inclusion(self,set_no,tag_add,f_mode,cache_memory,cache_counter,Assoc,dirty_bit_container):
        lst_ = []
        lst_counter = []
        dirt_lst = []
        Invalid_Lst = []
        hit_ = False
        temp_counter = 0
        if set_no not in cache_memory:
            lst_.append(tag_add)
            lst_counter.append(0)
            Invalid_Lst.append(1)
            # self.Is_Dirty(f_mode,index_)
            if f_mode=='w':
                dirt_lst.append('D')
            elif f_mode=='r':
                dirt_lst.append('')
        elif set_no in cache_memory:
            lst_ = cache_memory[set_no]
            lst_counter = cache_counter[set_no]
            dirt_lst = dirty_bit_container[set_no]
            if self.is_in_L2==False:
                Invalid_Lst = self.invalid_blocks[set_no]
            if tag_add in lst_:
                index_ = lst_.index(tag_add)
                if self.is_in_L2 == False:
                    if Invalid_Lst[index_] == 1:
                        if self.replacement_policy == 0:
                            lst_counter[index_] = max(lst_counter)+1
                        hit_ = True
                    # self.Is_Dirty(f_mode,index_)
                        if f_mode == 'w':
                            dirt_lst[index_] = 'D'
                else:
                    if self.replacement_policy == 0:
                        lst_counter[index_] = max(lst_counter)+1
                    hit_ = True
                # self.Is_Dirty(f_mode,index_)
                    # if f_mode == 'w':
                    #     dirt_lst[index_] = 'D'
                if self.is_in_L2 == False:
                    if Invalid_Lst[index_] == 0 and not self.is_in_L2:
                        if len(cache_memory[set_no])<Assoc:
                            lst_.append(tag_add)
                            lst_counter.append(max(lst_counter)+1)
                            Invalid_Lst.append(1)
                            # self.Is_Dirty(f_mode,index_)
                            if f_mode=='w':
                                dirt_lst.append('D')
                            elif f_mode=='r':
                                dirt_lst.append('')
                        elif len(cache_memory[set_no])==Assoc:
                            index_ = lst_counter.index(min(lst_counter))
                            # writeBack_tag_add = lst_[index_]
                            lst_[index_] = tag_add
                            # f.write("Lst counter = {}\n".format(lst_counter))
                            lst_counter[index_] = max(lst_counter)+1
                            if f_mode == 'w':
                                dirt_lst[index_] = 'D'
                            elif f_mode == 'r':
                                dirt_lst[index_] = ''
                # elif f_mode == 'r':
                #     dirt_lst[index_] = ''
            if tag_add not in lst_:
                if len(cache_memory[set_no])<Assoc:
                    lst_.append(tag_add)
                    lst_counter.append(max(lst_counter)+1)
                    Invalid_Lst.append(1)
                    # self.Is_Dirty(f_mode,index_)
                    if f_mode=='w':
                        dirt_lst.append('D')
                    elif f_mode=='r':
                        dirt_lst.append('')
                elif len(cache_memory[set_no])==Assoc:
                    index_ = lst_counter.index(min(lst_counter))
                    writeBack_tag_add = lst_[index_]
                    lst_[index_] = tag_add
                    # f.write("Lst counter = {}\n".format(lst_counter))
                    lst_counter[index_] = max(lst_counter)+1
                    if dirt_lst[index_] == 'D':
                        temp_counter += 1
                        if self.is_in_L2:
                            self.InvalidateBlock(writeBack_tag_add,set_no)
                        if self.has_L2 and not self.reset_File_Mode and not self.is_in_L2:
                            self.is_in_L2 = True
                            f.write("****** Before Dirty Tag = {} set = {}\n".format(writeBack_tag_add,set_no))
                            D_tag_add,D_index =self.Calculate_DirtyTag(writeBack_tag_add,set_no)
                            self.cache_L2_memory[D_index],self.time_counter_L2[D_index],hit_status_2,self.dirtyBits_L2[D_index],wb_cc = self.Replacement_Policy(D_index,D_tag_add,'w',self.cache_L2_memory,self.time_counter_L2,self.L2_Asso,self.dirtyBits_L2)
                            f.write("L2 hit status during writeback = {}\n".format(hit_status_2))
                            self.reset_File_Mode = True
                            if hit_status_2==False:
                                self.L2_OverallMissCount +=1
                            if self.reset_File_Mode and dirt_lst[index_]=='D':
                                self.Calculating_Hits_L2('w',hit_status_2)
                            self.no_l2_writeBacks += wb_cc 
                    # self.Is_Dirty(f_mode,index_)
                    if f_mode == 'w':
                        dirt_lst[index_] = 'D'
                    elif f_mode == 'r':
                        dirt_lst[index_] = ''
        # cache_counter[set_no] = lst_
        # cache_counter[set_no] = lst_counter
        if not self.is_in_L2:
            self.invalid_blocks[set_no] = Invalid_Lst
        return lst_,lst_counter,hit_,dirt_lst,temp_counter


    def InvalidateBlock(self,tag_add,index_):
        t1_len = len(str(index_))
        index_ = bin(index_)
        index_ = index_[2:]
        while len(index_)<self.index_bits[2]:
            index_ = "0"+index_
        t_len = len(tag_add[2:])
        tag_add = bin(int(tag_add,16))
        tag_add = tag_add[2:]
        while len(tag_add)<self.tag_bits[2]:
            tag_add = "0"+tag_add
        bb = tag_add+index_
        # while len(bb)<32:
        #     bb = "0"+bb
        f.write("========Before Invalidate bin add = {} len = {} index_bits={} index_ = {} tag_add = {}\n".format(bb,t_len,self.index_bits,index_,tag_add))
        L1_add = hex(int(bb[:self.tag_bits[1]],2))
        L1_index = int(bb[(self.tag_bits[1]):(self.tag_bits[1]+self.index_bits[1])],2)
        f.write("======== after Invalidate bin add = {} set = {}\n".format(L1_add,L1_index))
        if L1_index in self.cache_L1_memory:
            lst_ = self.cache_L1_memory[L1_index]
            # lst_counter = self.time_counter_L1[L1_index]
            invalid_LST = self.invalid_blocks[L1_index]
            dirt_Lst = self.dirtyBits_L1[L1_index]
            fMode = 'r'
            t_hit = False
            if L1_add in lst_:
                # if self.replacement_policy == 0:
                index_ = lst_.index(L1_add)
                # lst_counter[index_] = max(lst_counter)+1
                t_hit = True
                invalid_LST[index_] = 0
                if dirt_Lst[index_] == 'D':
                    fMode = 'w'
                    dirt_Lst[index_] = ''
                    self.no_l2_writeBacks +=1
            #     self.Calculating_Hits_L1(fMode,t_hit)
            # else:
            #     self.Calculating_Hits_L1(fMode,t_hit)
                # self.Is_Dirty(f_mode,index_)
                # if f_mode == 'w':
                #     dirt_lst[index_] = 'D'
                # elif f_mode == 'r':
                #     dirt_lst[index_] = ''
        


    # calculating misses and reads
    def Calculating_Hits_L1(self,file_m,hit):
        if file_m == 'r':
            self.no_l1_reads += 1
        elif file_m == 'w':
            self.no_l1_writes += 1

        if not hit:
            if file_m == 'r':
                self.no_l1_reads_miss += 1
            elif file_m == 'w':
                self.no_l1_write_miss += 1

            if self.has_L2:
                self.no_l2_reads+=1


    def Calculating_Hits_L2(self,file_m,hit):
        # if file_m == 'r':
        #     self.no_l2_reads += 1
        # if file_m == 'w':
        #     self.no_l2_writes += 1

        if not hit:
            if file_m == 'r' or file_m=='w':
                self.no_l2_reads_miss += 1
            elif file_m == 'w':
                self.no_l2_write_miss += 1   


    def Simulation_Results(self):
        print("Number L1 Reads = ",self.no_l1_reads)
        print("Number L1 Read misses = ",self.no_l1_reads_miss)
        print("Number L1 writes = ",self.no_l1_writes)
        print("Number L1 write misses = ",self.no_l1_write_miss)
        l1_miss_rate = (self.no_l1_reads_miss+self.no_l1_write_miss)/(self.no_l1_reads+self.no_l1_writes)
        l2_miss_rate = 0
        print("L1 miss rate = {:.6f}".format(l1_miss_rate))
        print("Number of L1 writeBacks = ",self.no_l1_writeBacks)
        if self.has_L2:
            l2_miss_rate = self.no_l2_reads_miss/self.no_l2_reads
        print("Number L2 Reads = ",self.no_l2_reads)
        print("Number L2 Read misses = ",self.no_l2_reads_miss)
        print("Number L2 writes = ",self.no_l1_writeBacks)
        print("Number L2 write misses = ",self.no_l2_write_miss)
        print("L2 miss rate = {:.6f}".format(l2_miss_rate))
        print("Total miss count L2 = ",self.L2_OverallMissCount)


    
c = Cache_Simulation(16,1024,1,8192,4,0,1,"C:\\Users\\ASHISH\\Desktop\\compress_trace.txt")
# print(c.dirtyBits_L1)
for i in range(int(c.number_of_sets[1])):
#   t = ""
#   print(i," = ",c.cache_L1_memory[i])
#   if 'D' in c.dirtyBits_L1:
#       index_ = c.dirtyBits_L1[i].index("D")
#       t = 'D'
#   print(c.dirtyBits_L1[i])
  res = "".join("{} {} ".format(x,y) for x, y in zip(c.cache_L1_memory[i], c.dirtyBits_L1[i]))
  print(i," = ",res,"\n")
#   print("{} = {} {}".format(i,c.cache_L1_memory[i],t))



if c.has_L2:
    for i in range(int(c.number_of_sets[2])):
        res = " ".join("{} {}".format(x,y) for x, y in zip(c.cache_L2_memory[i], c.dirtyBits_L2[i]))
        print(i," = ",res,"\n")
c.Simulation_Results()
print("L2 overall writebacks = {}".format(c.no_l2_writeBacks))
