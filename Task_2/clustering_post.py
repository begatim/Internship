from openalea.mtg.mtg import *
from openalea.mtg.algo import ancestors
from openalea.mtg.io import *
from openalea.mtg.traversal import *
from scoop import futures, shared
from itertools import cycle
import numpy as np 
import math
class Priority_queue:
    def __init__(self,weight,ordering="max"):
        self.heapList = [0]
        self.currentSize = 0
        self.weight = weight
        self.ordering = ordering
    
        

    def Empty(self):
        return self.currentSize == 0

    def percUp_max(self,i):
        while i // 2 > 0:
            if self.weight[self.heapList[i]] > self.weight[self.heapList[i // 2]]:
                #Swap places
                tmp = self.heapList[i // 2]
                self.heapList[i // 2] = self.heapList[i]
                self.heapList[i] = tmp 
            i = i // 2

    
    
    def percDown_max(self,i):
        while (i * 2) <= self.currentSize:
            mc = self.maxChild(i)
            if self.weight[self.heapList[i]] < self.weight[self.heapList[mc]]:
                tmp = self.heapList[i]
                self.heapList[i] = self.heapList[mc]
                self.heapList[mc] = tmp
            i = mc
    
    def maxChild(self,i):
        if i * 2 + 1 > self.currentSize:
            return i * 2
        else:
            if self.heapList[i*2] > self.heapList[i*2+1]:
                return i * 2
            else:
                return i * 2 + 1

    def append(self,x):
        #Insert the element at the end of the list 
        self.heapList.append(x)
        #Increment the size variable
        self.currentSize = self.currentSize + 1 
        self.percUp_max(self.currentSize)

    
    def pop(self):
        retval = self.heapList[1]
        if self.ordering == "max":
            self.heapList[1] = self.heapList[self.currentSize]
        self.currentSize = self.currentSize - 1
        self.heapList.pop()        
        return retval
        
    
    def last(self):
        #Return the last element without removing from the queue
        retval = self.heapList[self.currentSize]
        return retval
    
    def size(self):
        return self.currentSize
    
 


"""
#Algorithm 2
"""
import pdb as pd
#Clustering using post order traversal with priority queu
def SFC_FF(tree,p):
    vtx_id = tree.root
    C = [[] for i in range(p)]
    weight = np.zeros(len(tree))
    visited = set([])
    def order_children(vid):
        ordered = []
        #Sort the children of a node using the priority queue
        p_queue = Priority_queue(weight)
        for vid in tree.children(vid):
            p_queue.append(vid)
        while p_queue.size() > 0:
            node = p_queue.pop()
            ordered.append(node)
        return ordered

    for v in post_order(tree,tree.root):
        weight[v] = 1 + sum([weight[vid] for vid in tree.children(v)])
    
    c = int(len(tree)/p)
    
    
    queue = [vtx_id]
    
    counter = 0
    while queue:
        vtx_id = queue[-1]
        for vid in order_children(vtx_id):
            if vid not in visited:
                queue.append(vid)
                break
        else: # no child or all have been visited
            counter += 1
            visited.add(vtx_id)
            C[math.ceil(counter/c)-1].append(vtx_id)
            queue.pop()
    return C



from scipy.stats import poisson, binom 

my_mtg = MTG()
dist = poisson(1., loc=1).rvs
random_tree(my_mtg,my_mtg.root, nb_children=dist,nb_vertices=99)
#random_tree(my_mtg1,my_mtg1.root, nb_children=dist,nb_vertices=99)

#my_mtg  = simple_tree(Mtg, Mtg.root,nb_children = 4, nb_vertices=100)

clusters = SFC_FF(my_mtg,10)
#clusters1 = SFC_FF(my_mtg1,10)
for i in range(10):
    #print("---------------------------Cluster---------------",i)
    #print("Cluster",i,"for SFC_FF")
    #print(clusters1[i])
    print("Cluster",i,"for best fit clustering")
    print("---------------------------------------------------")
    print(clusters[i])
"""

weight = np.zeros(len(my_mtg))
for v in post_order(my_mtg,my_mtg.root):
    weight[v] = 1 + sum([weight[vid] for vid in my_mtg.children(v)])

A = list(post_order(my_mtg,my_mtg.root))

Q = Priority_queue(weight)
for i in range(15):
    Q.append(A[i])

while Q.size() > 0:
    node = Q.pop()
    print("Node from the queue",node,"with size",weight[node])
"""