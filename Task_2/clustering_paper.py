from openalea.mtg.mtg import *
from openalea.mtg.algo import ancestors
from openalea.mtg.io import *
from openalea.mtg.traversal import *
from scoop import futures, shared
from itertools import cycle
import numpy as np 
import math

class Priority_queue:
    def __init__(self,weights,ordering="max"):
        self.heapList = [0]
        self.currentSize = 0
        self.weights = weights
        self.ordering = ordering

    def Empty(self):
        return self.currentSize == 0

    def percUp(self,i):
        while i // 2 > 0:
          if self.weights[self.heapList[i]] > self.weights[self.heapList[i // 2]]:
             tmp = self.heapList[i // 2]
             self.heapList[i // 2] = self.heapList[i]
             self.heapList[i] = tmp
          i = i // 2

    def append(self,k):
      self.heapList.append(k)
      self.currentSize = self.currentSize + 1
      self.percUp(self.currentSize)

    def percDown(self,i):
      while (i * 2) <= self.currentSize:
          mc = self.maxChild(i)
          if self.weights[self.heapList[i]] < self.weights[self.heapList[mc]]:
              tmp = self.heapList[i]
              self.heapList[i] = self.heapList[mc]
              self.heapList[mc] = tmp
          i = mc

    def maxChild(self,i):
      if i * 2 + 1 > self.currentSize:
          return i * 2
      else:
          if self.weights[self.heapList[i*2]] > self.weights[self.heapList[i*2+1]]:
              return i * 2
          else:
              return i * 2 + 1

    def pop(self):
      retval = self.heapList[1]
      if self.ordering == "max":
        self.heapList[1] = self.heapList[self.currentSize]
      self.currentSize = self.currentSize - 1
      self.heapList.pop()
      self.percDown(1)
      return retval

      
    def size(self):
      return self.currentSize
    
    def last(self):
        return self.heapList[1]



def cluster_1(T,p,alpha):
    #Initialize the cluster
    C = [[] for i in range(p)]
    #Initialize the remain value
    remain = 0
    #Initialize the array of weights
    weight = np.zeros(len(T))
    weight = weight.astype(int)
    
    #Compute the weights for all the nodes, only once
    for v in post_order(T,T.root):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])
    
        
    
    #Define the size of the cluster
    c = int(len(T)/p)
    
    def BF(remain,first_time,Q,last_cluster):
        #Add into the queue only subtrees of size that have not been added before
        sub = None
        index = 0
        if last_cluster:
            sub = T.root
        
        elif first_time:
            
            
            #Fill the queue by traversing the tree and finding the subtrees of size less than remain
            for v in post_order(T,T.root):
                #Check if it is maxima else set it as a maximum
                if T.parent(v):
                    if weight[v] <= remain and weight[T.parent(v)] > remain:
                        #Found a maximal subtree and added it to the queue
                        if Q[weight[v]] == None:
                            Q[weight[v]] = v
                        #Check if it is optimal
                        if weight[v] <= remain and weight[v] + 1 > remain:    
                            break
            #Enter else only if we finish the for loop without finding a best fit subtree
            
            i = len(Q) - 1
            while i > 1:
                if Q[i] != None:
                    index = i
                    sub = Q[index]
                    Q[i] = None
                    break 
                i = i - 1
            
            
            #Update the queue
            
            i = index - 1
            if remain - index > 0:
                while i > remain - index:
                    for v in pre_order(T,Q[i]):
                        if T.parent(v):
                            if weight[v] < remain -index and weight[T.parent(v)] > remain - index:
                                Q[weight[v]] = v
                                
                    Q[i] = None
                    i = i-1
            
            
            remove_weight = index
        
            for w in list(ancestors(T,sub)):
                weight[w] = weight[w] - remove_weight
           
        else:
            i = remain
            while i > 0:
                if Q[i] != None:
                    index = i
                    sub = Q[i] 
                    Q[i] = None
                    break 

                i = i - 1
            #Weight of the founded subtree
            
            #Update the queue
            i = index
            if remain - index > 0:
                while i > remain - index:
                    for v in pre_order(T,Q[i]):
                        if T.parent(v):
                            if weight[v] < remain - index and weight[T.parent(v)] > remain - index:
                                Q[weight[v]] = v
                    Q[i] = None
                    i = i - 1    
    
            remove_weight = index
          
            for w in list(ancestors(T,sub)):
                weight[w] = weight[w] - remove_weight
        #Remove the founded subtree

        if sub != T.root:
            sub_tree_found = list(post_order(T,sub))
            T.remove_tree(sub)
        elif sub == T.root:
            sub_tree_found = list(post_order(T,sub))
        return sub_tree_found
        
    remain = 0
    
    for i in range(p):
        #For each cluster initialize the queue from the begining
        
        
        target = c
        remain = target
        first_time = True
        last_cluster = False
        Qu = [None for i in range(remain+1)]
        while len(C[i]) < (1 - alpha/2)*target:
            if i == p-1:
                last_cluster = True
            
            #Fills the queue if first time and searches for subtree if second time
            sub = BF(remain,first_time,Qu,last_cluster)
            if sub == None:
                break
            remain = remain - len(sub)
            C[i] += sub
            first_time = False
    return C







from scipy.stats import poisson, binom 

my_mtg = MTG()
dist = poisson(1., loc=1).rvs
random_tree(my_mtg,my_mtg.root, nb_children=dist,nb_vertices=9999)
#random_tree(my_mtg1,my_mtg1.root, nb_children=dist,nb_vertices=99)

#my_mtg  = simple_tree(Mtg, Mtg.root,nb_children = 4, nb_vertices=100)

clusters = SFC_BF(my_mtg,100,0)
#clusters1 = SFC_FF(my_mtg1,10)
for i in range(100):
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