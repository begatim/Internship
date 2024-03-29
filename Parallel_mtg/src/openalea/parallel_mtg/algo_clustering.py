
"""Implementation of a number of Tree clustering algorithms to benchmark the algorithms in terms of distributed computing performance"""

from openalea.parallel_mtg.tools import *

def Best_Fit_Clustering(T, p, alpha):
    ''' Clustering Trees based on the paper of Hambrusch and Liu

        :Parameters:
         - `T` (Tree) The tree which we want to cluster
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
         :Returns:
            None
         :Result: Writes directly into the MTG dicitionary the enries of "cluster" and "sub_tree", the first one gives a dictionary with all the nodes as keys and cluster id as values.
                 The sub_tree contains all subtree roots founded during clusters as keys and their cluster_id as values
        '''
    
    remain = 0
    
    weight = {}
    
    internode_root = T.roots(T.max_scale())
    c_omponent = internode_root[0]
    for v in post_order(T,c_omponent):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])
    
    c = int(len(T)/p)
    sub_tree = T.property('sub_tree')
    cluster = T.property('cluster')
    
    def Best_Fit(remain,first_time,Q,last_cluster,cluster_index):
       
        sub = None
        index = 0
        if last_cluster:
            sub = c_omponent
        
        elif first_time:
            for v in post_order2(T,c_omponent,pre_order_filter = lambda v: v not in sub_tree):
                if T.parent(v) != None:
                    if weight[v] <= remain and weight[T.parent(v)] > remain:
                        if Q[weight[v]] == None:
                            Q[weight[v]] = v
                        if weight[v] <= remain and weight[v] + 1 > remain:    
                            break

            i = len(Q) - 1
            while i > 1:
                if Q[i] != None:
                    index = i
                    sub = Q[index]
                    Q[i] = None
                    break 
                i = i - 1
            
            i = index - 1
            if remain - index > 0:
                while i > remain - index:
                    for v in pre_order(T,Q[i]):
                        if T.parent(v) != None:
                            if weight[v] <= remain -index and weight[T.parent(v)] > remain - index:
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
            
            i = index
            if remain - index > 0:
                while i > remain - index:
                    for v in post_order2(T,Q[i],pre_order_filter = lambda v: v not in sub_tree):
                        if T.parent(v) != None:
                            if weight[v] <= remain - index and weight[T.parent(v)] > remain - index:
                                Q[weight[v]] = v
                    Q[i] = None
                    i = i - 1    
    
            remove_weight = index
          
            for w in list(ancestors(T,sub)):
                weight[w] = weight[w] - remove_weight
       

        if sub != c_omponent:
            sub_tree[sub] = cluster_index
            sub_tree_found = list(post_order2(T,sub,pre_order_filter = lambda v: v not in sub_tree))
            for v in sub_tree_found:
                cluster[v] = cluster_index
            
        elif sub == c_omponent:
            sub_tree[sub] = cluster_index
            sub_tree_found = list(post_order2(T,sub,pre_order_filter = lambda v: v not in sub_tree))
            for v in sub_tree_found:
                cluster[v] = cluster_index
        return sub_tree_found
        
    remain = 0
    
    for i in reversed(range(p)):
        target = c
        remain = target
        first_time = True
        last_cluster = False
        Qu = [None for i in range(remain+1)]
        while remain > 1:
            if i == 0:
                last_cluster = True
            
            sub = Best_Fit(remain,first_time,Qu,last_cluster,i)
            if sub == None:
                break
            remain = remain - len(sub)
            
            first_time = False

def First_Fit_Clustering(T,p):
    ''' Clustering Trees based on the paper of Hambrusch and Liu but modified for better performance

        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - `p`  (int) - The number of clusters we want to fill
        :Returns:
            None
        :Result: Writes directly into the MTG dicitionary the enries of "cluster" and "sub_tree", the first one gives a dictionary with all the nodes as keys and cluster id as values.
                 The sub_tree contains all subtree roots founded during clusters as keys and their cluster_id as values
            
    '''
    cluster = T.property('cluster')
    sub_tree = T.property('sub_tree')
    internode_root = T.roots(T.max_scale())
    c_omponent = internode_root[0]
    vtx_id = c_omponent
    weights = {}
    
    for v in post_order(T, c_omponent):
        weights[v] = 1 + sum([weights[vid] for vid in T.children(v)])
    weights_copy = weights
    visited = set([])

    def order_children(vid):
        ordered = []
        p_queue = Priority_queue(weights)
        for vid in T.children(vid):
            p_queue.append(vid)
        while p_queue.size() > 0:
            node = p_queue.pop()
            ordered.append(node)
        return ordered

    c = int(len(T)/p)

    queue = [vtx_id]
    local_weight = c
    counter = 0
    while queue:
        vtx_id = queue[-1]
        for vid in order_children(vtx_id):
            if vid not in visited:
                queue.append(vid)
                break
        else:
            
            counter += 1
            visited.add(vtx_id)
            if math.ceil(counter/c) - 1 >= p:
                cluster[vtx_id] = 0
            else:
                cluster[vtx_id] = p - 1 - (math.ceil(counter/c) - 1)
            if vtx_id != c_omponent:
                #Check if it is a sub_tree root
                if weights_copy[T.parent(vtx_id)] > local_weight or (math.ceil((counter+1)/c) != math.ceil(counter/c)):
                    if p - 1 - (math.ceil(counter/c) - 1) > 0:
                        sub_tree[vtx_id] = p - 1 - (math.ceil(counter/c) - 1)
                        remove_weight = weights_copy[vtx_id]
                        local_weight -= weights_copy[vtx_id]
                        if (math.ceil((counter+1)/c) != math.ceil(counter/c)):
                            local_weight = c
                        for w in list(ancestors(T, vtx_id)):
                            weights_copy[w] = weights_copy[w] - remove_weight
            elif vtx_id == c_omponent:
                sub_tree[vtx_id] = 0
               
            queue.pop()
    
def Best_Fit_Clustering_post_order(T,p, alpha):
    ''' Clustering Trees based on the paper of Hambrusch and Liu but modified for better performance
        Improvemnt of the function Best_Fit_Clustering, so that it does not change the structure of the tree during processing
        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
         :Returns:
            None
         :Result: Writes directly into the MTG dicitionary the enries of "cluster" and "sub_tree", the first one gives a dictionary with all the nodes as keys and cluster id as values.
            The sub_tree contains all subtree roots founded during clusters as keys and their cluster_id as values
    '''
    cluster = T.property('cluster')
    sub_tree = T.property('sub_tree')
   
    weight = {}
    internode_root = T.roots(T.max_scale())
    c_omponent = internode_root[0]
    for v in post_order(T, c_omponent):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])
    
    c = int(len(T)/p)

    def Best_Fit(remain, Q, last_cluster, cluster_index):
        sub = None
        if last_cluster:
            sub = c_omponent
        else:
            for vid in post_order2(T, c_omponent, pre_order_filter=lambda v:v not in sub_tree):
                if T.parent(vid) != None:
                    if weight[vid] <= (1+alpha)*remain and weight[T.parent(vid)] > remain*(1 + alpha):
                        Q.append(vid)
                        if weight[vid] > (1-alpha/2)*remain:
                            break

            if Q.size() > 0:
                sub = Q.pop()
                index = weight[sub]
                for w in list(ancestors(T, sub)):
                    weight[w] = weight[w] - index

        sub_tree[sub] = cluster_index
        for v in post_order2(T, sub, pre_order_filter=lambda v: v not in sub_tree):
            cluster[v] = cluster_index
        
    last_cluster = False
    for i in reversed(range(p)):
        Qu = Priority_queue(weight)
        target = c
        if i == 0:
            last_cluster = True

        Best_Fit(target, Qu, last_cluster, i)





def Best_Fit_Clustering_level_order(T,p, alpha):
    ''' Clustering Trees based on the paper of Hambrusch and Liu but modified for better performance
    Now, it uses level-order traversal instead of post-order to find the trees

        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
         :Returns:
            None
         :Result: Writes directly into the MTG dicitionary the enries of "cluster" and "sub_tree", the first one gives a dictionary with all the nodes as keys and cluster id as values.
            The sub_tree contains all subtree roots founded during clusters as keys and their cluster_id as values
    '''
    weight = {}
    internode_root = T.roots(T.max_scale())
    c_omponent = internode_root[0]
    for v in post_order(T, c_omponent):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])
    cluster = T.property('cluster')
    sub_tree = T.property('sub_tree')
    c = int(len(T)/p)

    def Best_Fit(remain, Q, last_cluster, cluster_index):
        sub = None
        if last_cluster:
            sub = c_omponent
        else:
            for vid in level_order2(T, c_omponent, visitor_filter=lambda v: v not in sub_tree):

                if T.parent(vid) != None:
                    if weight[vid] <= (1+alpha)*remain and weight[T.parent(vid)] > remain*(1 + alpha):
                        Q.append(vid)
                        if weight[vid] > (1-alpha/2)*remain:
                            break

            if Q.size() > 0:
                sub = Q.pop()
                index = weight[sub]
                for w in list(ancestors(T, sub)):
                    weight[w] = weight[w] - index

        
        sub_tree[sub] = cluster_index
        for v in post_order2(T, sub, pre_order_filter=lambda v: v not in sub_tree):
            cluster[v] = cluster_index
        
    
    last_cluster = False
    for i in reversed(range(p)):
        Qu = Priority_queue(weight)
        target = c
        if i == 0:
            last_cluster = True

        Best_Fit(target, Qu, last_cluster, i)




"""
Experimental work
"""
def First_Fit_Clustering_level_order(T,p,alpha):
    ''' Clustering Trees based on the paper of Hambrusch and Liu but modified for better performance
    Now, it uses level-order traversal instead of post-order to find the trees

        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
         :Returns:
            None
         :Result: Writes directly into the MTG dicitionary the enries of "cluster" and "sub_tree", the first one gives a dictionary with all the nodes as keys and cluster id as values.
            The sub_tree contains all subtree roots founded during clusters as keys and their cluster_id as values
    '''
    cluster = T.property('cluster')
    sub_tree = T.property('sub_tree')
    c_omponent = T.component_roots(T.root)[0]
    vtx_id = c_omponent
    weights = np.zeros(len(T))
    for v in post_order(T,c_omponent):
        weights[v] = 1 + sum([weights[vid] for vid in T.children(v)])
    weights_copy = weights
    visited = set([])
    queue = [vtx_id]
    c = int(len(T)/p)
    remain = c
    cluster_considered = p-1
    
    while queue:
        
        vtx_id = queue.pop()
        for vid in T.children(vtx_id):
            if weights[vid] >= (1-alpha/2)*remain and weights[vid] <= (1+alpha)*remain:
                sub_tree[vid] = cluster_considered
                cluster_considered -= 1
            
            elif cluster_considered == 0:
                sub_tree[c_omponent] = cluster_considered
                break
            
            else:
                queue.append(vid)
    if cluster_considered != 0:
        sub_tree[c_omponent] = 0
    
    for node in sub_tree:
        for v in post_order2(T, node, pre_order_filter=lambda v: v not in sub_tree):
            cluster[v] = sub_tree[node]
    

            


        




