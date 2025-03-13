import math

# f = open("Debug.txt","w")
class Cache_Simulation():
    L1_size = 0
    L1_assoc = 0
    L2_Size = 0
    L2_Assoc = 0
    BlockSize = 0
    inclusion_prop = 0
    replacement_prop = 0
    trace_File = None
    L1_Cache_Mem = {}
    L2_Cache_Mem = {}
    L1_timeCounter = {}
    L2_timeCounter = {}
    L1_dirtyBits = {}
    L2_dirtyBits = {}
    L1_Invalid_status = {}
    no_sets = [0]
    no_tagbits = [0]
    no_indexbits = [0]
    no_offsetBits = [0]
    has_L2 = False
    L1_read = 0
    L1_writes = 0
    L1_read_misses = 0
    L1_write_misses = 0
    L1_writebacks = 0
    L2_read = 0
    L2_writes = 0
    L2_read_misses = 0
    L2_write_misses = 0
    L2_writebacks = 0
    entered_L2 = False
    Change_File_Mode = False
    Invalid_set = {}
    l1_miss_rate = 0
    l2_miss_rate = 0
    total_traffic = 0

    # Intialising variables
    def __init__(self,B_Size,L1_S,L1_A,L2_S,L2_A,R_policy,Inc_Policy,file_name):
        self.BlockSize = B_Size
        self.L1_size = L1_S
        self.L1_assoc = L1_A
        self.L2_Assoc = L2_A
        self.L2_Size = L2_S
        self.replacement_prop = R_policy
        self.inclusion_prop = Inc_Policy
        self.trace_File = file_name
        self.printConfig()
    
    # Printing Simulation Configuration
    def printConfig(self):
        print("===== Simulator configuration =====")
        print("Block Size:      {}".format(self.BlockSize))
        print("L1 Size:         {}".format(self.L1_size))
        print("L1 Assoc:        {}".format(self.L1_assoc))
        print("L2 Size:         {}".format(self.L2_Size))
        print("L2 Assoc:        {}".format(self.L2_Assoc))
        if self.replacement_prop==0:
            str1 = "LRU"
        elif self.replacement_prop==1:
            str1 = "FIFO"
        if self.inclusion_prop==0:
            str2 = "non-inclusive"
        elif self.inclusion_prop==1:
            str2 = "inclusive"
        print("Replacement Policy:       {}".format(str1))
        print("Inclusion Property:        {}".format(str2))
        print("Trace File:                {}".format(self.trace_File))
        self.Divide_Bits()
    
    # Calculating tag,index and offset bits using the block size
    def Divide_Bits(self):
        sets_L1 = int((self.L1_size)/(self.BlockSize*self.L1_assoc))
        index_bits_l1 = int(math.log(sets_L1,2))
        block_offset = int(math.log(self.BlockSize,2))
        tag_bits_l1 = 32-index_bits_l1-block_offset\
        
        self.no_sets.append(sets_L1)
        self.no_indexbits.append(index_bits_l1)
        self.no_tagbits.append(tag_bits_l1)

        if self.L2_Size!=0:
            sets_L2 = (self.L2_Size)/(self.BlockSize*self.L2_Assoc)
            index_bits_l2 = int(math.log(sets_L2,2))
            tag_bits_l2 = 32-index_bits_l2-block_offset
            self.has_L2 = True
            self.no_sets.append(sets_L2)
            self.no_indexbits.append(index_bits_l2)
            self.no_tagbits.append(tag_bits_l2)
        self.StartSimulation()
    
    # Started the simulation using the file input and later on calculated the tag address and index
    def StartSimulation(self):
        f = open("traces/"+self.trace_File,"r")
        for line in f.readlines():
            l = line.strip().split()
            op = l[0]
            h_add = l[1]
            diff_ = 8-len(h_add)
            if diff_>0:
                h_add = '0'*diff_ + h_add
            # while len(h_add)<8:
            #     h_add = "0"+h_add
            binary_add = bin(int(h_add,16))
            binary_add = binary_add[2:]
            diff_2 = 32-len(binary_add)
            if diff_2>0:
                binary_add = "0"*diff_2+binary_add
            # print(self.no_tagbits)
            tag_add_1 = hex(int(binary_add[:self.no_tagbits[1]],2))
            index_no_1 = int(binary_add[self.no_tagbits[1]:self.no_tagbits[1]+self.no_indexbits[1]],2)

            if self.has_L2:
                tag_add_2 = hex(int(binary_add[:self.no_tagbits[2]],2))
                index_no_2 = int(binary_add[self.no_tagbits[2]:self.no_tagbits[2]+self.no_indexbits[2]],2)
            
            if self.inclusion_prop==0:
                self.L1_Cache_Mem[index_no_1],self.L1_timeCounter[index_no_1],self.L1_dirtyBits[index_no_1],hit_L1,wb_1 = self.ReplacementPolicy(self.L1_Cache_Mem,self.L1_timeCounter,self.L1_dirtyBits,tag_add_1,index_no_1,op,self.L1_assoc)
                self.Calculate_reads_writes(hit_L1,op,1)
                self.L1_writebacks += wb_1
                if self.has_L2 and hit_L1==False:
                    self.entered_L2 = True
                    t_op = op
                    if self.Change_File_Mode == True:
                        t_op = 'r'
                    self.L2_Cache_Mem[index_no_2],self.L2_timeCounter[index_no_2],self.L2_dirtyBits[index_no_2],hit_L2,wb_2 = self.ReplacementPolicy(self.L2_Cache_Mem,self.L2_timeCounter,self.L2_dirtyBits,tag_add_2,index_no_2,t_op,self.L2_Assoc)
                    self.entered_L2 = False
                    self.Calculate_reads_writes(hit_L2,'r',2)
                    self.Change_File_Mode = False
                    self.L2_writebacks += wb_2
            if self.inclusion_prop==1:
                self.L1_Cache_Mem[index_no_1],self.L1_timeCounter[index_no_1],self.L1_dirtyBits[index_no_1],hit_L1,wb_1 = self.ReplacementPolicy_Inclusion(self.L1_Cache_Mem,self.L1_timeCounter,self.L1_dirtyBits,tag_add_1,index_no_1,op,self.L1_assoc)
                self.Calculate_reads_writes(hit_L1,op,1)
                self.L1_writebacks += wb_1
                if self.has_L2 and hit_L1==False:
                    self.entered_L2 = True
                    t_op = op
                    if self.Change_File_Mode == True:
                        t_op = 'r'
                    self.L2_Cache_Mem[index_no_2],self.L2_timeCounter[index_no_2],self.L2_dirtyBits[index_no_2],hit_L2,wb_2 = self.ReplacementPolicy_Inclusion(self.L2_Cache_Mem,self.L2_timeCounter,self.L2_dirtyBits,tag_add_2,index_no_2,t_op,self.L2_Assoc)
                    self.entered_L2 = False
                    self.Calculate_reads_writes(hit_L2,'r',2)
                    self.Change_File_Mode = False
                    self.L2_writebacks += wb_2

    # Non inclusive replacement policy combining both LRU and FIFO 
    def ReplacementPolicy(self,cache_mem,cache_counter,cache_dirty,tag_add,index_no,f_op,assoc):
        lst_ = []
        lst_counter = []
        dirty_lst = []
        hit_ = False
        temp = 0
        if index_no not in cache_mem:
            lst_.append(tag_add)
            lst_counter.append(0)
            if f_op=='w':
                dirty_lst.append('D')
            if f_op=='r':
                dirty_lst.append('')
        elif index_no in cache_mem:
            lst_ = cache_mem[index_no]
            lst_counter = cache_counter[index_no]
            dirty_lst = cache_dirty[index_no]
            if tag_add in lst_:
                hit_ = True
                tag_pos = lst_.index(tag_add)
                if self.replacement_prop==0:
                    lst_counter[tag_pos] = max(lst_counter)+1
                if f_op=='w':
                    dirty_lst[tag_pos] = 'D'
            elif tag_add not in lst_:
                if len(lst_)<assoc:
                    lst_.append(tag_add)
                    lst_counter.append(max(lst_counter)+1)
                    if f_op=='w':
                        dirty_lst.append('D')
                    if f_op=='r':
                        dirty_lst.append('')
                elif len(lst_)==assoc:
                    min_ind = lst_counter.index(min(lst_counter))
                    wb_add = lst_[min_ind]
                    lst_[min_ind] = tag_add
                    lst_counter[min_ind] = max(lst_counter)+1
                    if dirty_lst[min_ind] == 'D':
                        temp +=1
                        dirty_lst[min_ind] = ''
                        if self.has_L2 and self.entered_L2==False:
                            l2_add,l2_index = self.Get_Add(wb_add,index_no,1)
                            self.entered_L2 = True
                            self.L2_Cache_Mem[l2_index],self.L2_timeCounter[l2_index],self.L2_dirtyBits[l2_index],hit_L2,wb_2 = self.ReplacementPolicy(self.L2_Cache_Mem,self.L2_timeCounter,self.L2_dirtyBits,l2_add,l2_index,'w',self.L2_Assoc)
                            self.Calculate_reads_writes(hit_L2,'w',2)
                            self.Change_File_Mode = True
                            self.entered_L2 = False
                            self.L2_writebacks += wb_2
                    if f_op=='w':
                        dirty_lst[min_ind] = 'D'
                    if f_op=='r':
                        dirty_lst[min_ind] = ''
        return lst_,lst_counter,dirty_lst,hit_,temp

    # inclusive replacement policy
    def ReplacementPolicy_Inclusion(self,cache_mem,cache_counter,cache_dirty,tag_add,index_no,f_op,assoc):
        lst_ = []
        lst_counter = []
        dirty_lst = []
        hit_ = False
        temp = 0
        if index_no not in cache_mem:
            lst_.append(tag_add)
            lst_counter.append(0)
            if f_op=='w':
                dirty_lst.append('D')
            if f_op=='r':
                dirty_lst.append('')
        elif index_no in cache_mem:
            lst_ = cache_mem[index_no]
            lst_counter = cache_counter[index_no]
            dirty_lst = cache_dirty[index_no]
            if tag_add in lst_:
                hit_ = True
                tag_pos = lst_.index(tag_add)
                if self.replacement_prop==0:
                    lst_counter[tag_pos] = max(lst_counter)+1
                    if self.entered_L2==False:
                        t_tag,t_ind = self.Get_Add(tag_add,index_no,1)
                        t_lst = self.L2_Cache_Mem[t_ind]
                        t_lst_counter = self.L2_timeCounter[t_ind]
                        t_pos = t_lst.index(t_tag)
                        t_lst_counter[t_pos] = max(t_lst_counter)+1
                        self.L2_timeCounter[t_ind] = t_lst_counter
                if f_op=='w':
                    dirty_lst[tag_pos] = 'D'
            elif tag_add not in lst_:
                if len(lst_)<assoc:
                    lst_.append(tag_add)
                    lst_counter.append(max(lst_counter)+1)
                    if f_op=='w':
                        dirty_lst.append('D')
                    if f_op=='r':
                        dirty_lst.append('')
                elif len(lst_)==assoc:
                    min_ind = lst_counter.index(min(lst_counter))
                    wb_add = lst_[min_ind]
                    lst_[min_ind] = tag_add
                    lst_counter[min_ind] = max(lst_counter)+1
                    if self.entered_L2 == True:
                        # Invalidating Block in L1
                        iv_tag,iv_ind = self.Get_Add(wb_add,index_no,2)
                        iv_lst = self.L1_Cache_Mem[iv_ind]
                        iv_lst_counter = self.L1_timeCounter[iv_ind]
                        iv_dirty_lst = self.L1_dirtyBits[iv_ind]
                        # f.write("l2 Tag = {} l2 index = {}\n".format(wb_add,index_no))
                        # f.write("Invalid Tag = {} Invalid index = {}\n".format(iv_tag,iv_ind))
                        # f.write("Invalid lst = {}\n".format(iv_lst))
                        # f.write("\n")
                        if iv_tag in iv_lst:
                            # print("removing")
                            iv_pos = iv_lst.index(iv_tag)
                            iv_lst.pop(iv_pos)
                            iv_lst_counter.pop(iv_pos)
                            iv_dirty_lst.pop(iv_pos)
                            self.L1_Cache_Mem[iv_ind]=iv_lst
                            self.L1_timeCounter[iv_ind] = iv_lst_counter
                            self.L1_dirtyBits[iv_ind] = iv_dirty_lst
                    if dirty_lst[min_ind] == 'D':
                        temp +=1
                        dirty_lst[min_ind] = ''
                        if self.has_L2 and self.entered_L2==False:
                            l2_add,l2_index = self.Get_Add(wb_add,index_no,1)
                            self.entered_L2 = True
                            self.L2_Cache_Mem[l2_index],self.L2_timeCounter[l2_index],self.L2_dirtyBits[l2_index],hit_L2,wb_2 = self.ReplacementPolicy_Inclusion(self.L2_Cache_Mem,self.L2_timeCounter,self.L2_dirtyBits,l2_add,l2_index,'w',self.L2_Assoc)
                            self.Calculate_reads_writes(hit_L2,'w',2)
                            self.Change_File_Mode = True
                            self.entered_L2 = False
                            self.L2_writebacks += wb_2
                    if f_op=='w':
                        dirty_lst[min_ind] = 'D'
                    elif f_op=='r':
                        dirty_lst[min_ind] = ''
        return lst_,lst_counter,dirty_lst,hit_,temp

    
    
    
    
    def Get_Add(self,tag_add,index_,cache_type):
        if cache_type==1:
            i = 2
        if cache_type==2:
            i = 1
        t1_len = len(str(index_))
        index_ = bin(index_)
        index_ = index_[2:]
        diff_ = self.no_indexbits[cache_type] - len(index_)
        if diff_>0:
            index_ = '0'*diff_+index_
        t_len = len(tag_add[2:])
        tag_add = bin(int(tag_add,16))
        tag_add = tag_add[2:]
        diff_2 = self.no_tagbits[cache_type] - len(tag_add)
        if diff_2>0:
            tag_add = '0'*diff_2+tag_add
        bb = tag_add+index_
        t_add = hex(int(bb[:self.no_tagbits[i]],2))
        t_index = int(bb[(self.no_tagbits[i]):(self.no_tagbits[i]+self.no_indexbits[i])],2)
        return t_add,t_index
    

    def Calculate_reads_writes(self,hit_status,f_m,Cache_type):
        if Cache_type==1:
            if f_m == 'r':
                self.L1_read += 1
            elif f_m=='w':
                self.L1_writes +=1
            if hit_status==False:
                if f_m == 'r':
                    self.L1_read_misses += 1
                elif f_m=='w':
                    self.L1_write_misses +=1 
                if self.has_L2:
                    self.L2_read += 1
        elif Cache_type == 2:
            if f_m=='w':
                self.L2_writes +=1
            if hit_status==False:
                if f_m == 'r':
                    self.L2_read_misses += 1
                elif f_m=='w':
                    # self.L2_read_misses += 1
                    self.L2_write_misses +=1 

    def printResults(self):
        self.Calculate_Miss_rate()
        print("===== Simulation results (raw) =====")
        print("a. number of L1 reads:        {}".format(self.L1_read))
        print("b. number of L1 read misses:  {}".format(self.L1_read_misses))
        print("c. number of L1 writes:       {}".format(self.L1_writes))
        print("d. number of L1 write misses: {}".format(self.L1_write_misses))
        print("e. L1 miss rate:              {}".format(self.l1_miss_rate))
        print("f. number of L1 writebacks:   {}".format(self.L1_writebacks))
        print("g. number of L2 reads:        {}".format(self.L2_read))
        print("h. number of L2 read misses:  {}".format(self.L2_read_misses))
        if self.has_L2:
            print("i. number of L2 writes:       {}".format(self.L2_writes))
        elif not self.has_L2:
            print("i. number of L2 writes:       {}".format(0))
        print("j. number of L2 write misses: {}".format(self.L2_write_misses))
        print("k. L2 miss rate:              {}".format(self.l2_miss_rate))
        print("l. number of L2 writebacks:   {}".format(self.L2_writebacks))
        print("m. total memory traffic:      {}".format(self.total_traffic))
    

    def Calculate_Miss_rate(self):
        self.l1_miss_rate = (self.L1_read_misses+self.L1_write_misses)/(self.L1_read+self.L1_writes)
        self.l2_miss_rate = 0
        self.total_traffic = self.L1_write_misses+self.L1_read_misses+self.L1_writebacks
        if self.has_L2:
            self.l2_miss_rate = self.L2_read_misses/self.L2_read
            if self.inclusion_prop==0:
                self.total_traffic = self.L2_read_misses+self.L2_write_misses+self.L2_writebacks
            elif self.inclusion_prop==1:
                self.total_traffic = self.L2_read_misses+self.L2_write_misses+self.L2_writebacks

        
         


                
        


