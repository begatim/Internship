
"""Implementation of a number of MTG clustering algorithms"""

from Queue import *

def Best_Fit_Clustering_Paper(T, p, alpha):
    ''' Clustering Trees based on the paper of Hambrusch and Liu

        :Parameters:
         - `T` (Tree) The tree which we want to cluster
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
        :Returns:
            All the clusters as a list of lists of all the nodes of the tree
        :Returns Type:
            List
        '''
    cluster = T.property('cluster')
    is_root = T.property('is_root')
    C = [[] for i in range(p)]
    remain = 0
    weight = np.zeros(len(T))
    weight = weight.astype(int)
    for v in post_order(T, T.root):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])
    color = set()
    #color = T.property('color')
    c = int(len(T)/p)

    def Best_Fit(remain, first_time, Q, last_cluster, cluster_index):

        sub = None
        index = 0
        if last_cluster:
            sub = T.root

        elif first_time:
            for v in post_order2(T, T.root, pre_order_filter=lambda v: v not in color):
                print(v)
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
                    for v in pre_order(T, Q[i]):
                        if T.parent(v) != None:
                            if weight[v] <= remain - index and weight[T.parent(v)] > remain - index:
                                Q[weight[v]] = v

                    Q[i] = None
                    i = i-1

            remove_weight = index

            for w in list(ancestors(T, sub)):
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
                    for v in post_order(T, Q[i]):
                        if T.parent(v) != None:
                            if weight[v] <= remain - index and weight[T.parent(v)] > remain - index:
                                Q[weight[v]] = v
                    Q[i] = None
                    i = i - 1

            remove_weight = index

            for w in list(ancestors(T, sub)):
                weight[w] = weight[w] - remove_weight

        if sub != T.root:
            color.add(sub)# = sub
            sub_tree_found = list(post_order2(T, sub, pre_order_filter=lambda v: v not in color))
            # T.remove_tree(sub)
            for v in sub_tree_found:
                cluster[v] = cluster_index
        elif sub == T.root:
            #color[T.root] = T.root
            sub_tree_found = list(post_order2(T, sub, pre_order_filter=lambda v: v not in color))
            for v in sub_tree_found:
                cluster[v] = cluster_index
        return sub_tree_found

    remain = 0

    for i in range(p):
        target = c
        remain = target
        first_time = True
        last_cluster = False
        Qu = [None for i in range(remain+1)]
        while len(C[i]) < (1 - alpha/2)*target:
            if i == p-1:
                last_cluster = True

            sub = Best_Fit(remain, first_time, Qu, last_cluster, i)
            if sub == None:
                break
            remain = remain - len(sub)
            C[i] += sub
            first_time = False
    return C


def Best_Fit_Clustering(T, c_omponent, p, alpha):
    ''' Clustering Trees based on the paper of Hambrusch and Liu but modified for better performance

        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - 'c_omponent' - The component of the MTG from which we start traversing
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
        :Returns:
            All the clusters as a list of lists of all the nodes of the tree
        :Returns Type:
            List
    '''
    C = [[] for i in range(p)]
    cluster = T.property('cluster')
    remain = 0
    weight = np.zeros(len(T))
    for v in post_order(T, c_omponent):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])

    c = int(len(T)/p)
    color = set()

    def Best_Fit(remain, first_time, Q, last_cluster, cluster_index):

        sub = None
        if last_cluster:
            sub = c_omponent

        elif first_time:
            for vid in post_order2(T, c_omponent, pre_order_filter=lambda v: v not in color):
                if T.parent(vid) != None:
                    if weight[vid] <= remain and weight[T.parent(vid)] > remain:
                        Q.append(vid)
                        if weight[vid] + 1 > remain:
                            break

            if Q.size() > 0:
                sub = Q.pop()

                index = weight[sub]

                if remain - index > 0:
                    while weight[Q.last()] > remain - index:
                        node = Q.pop()
                        for v in pre_order(T, node):
                            if T.parent(v):
                                if weight[v] <= remain - index and weight[T.parent(v)] > remain - index:
                                    Q.append(v)

                for w in list(ancestors(T, sub)):
                    weight[w] = weight[w] - index

        else:

            sub = Q.pop()
            index = weight[sub]

            if remain - index > 0:
                while weight[Q.last()] > remain - index:
                    node = Q.pop()
                    for v in pre_order(T, node):
                        if T.parent(v):
                            if weight[v] <= remain - index and weight[T.parent(v)] > remain - index:
                                Q.append(v)

            remove_weight = weight[sub]

            for w in list(ancestors(T, sub)):
                weight[w] = weight[w] - remove_weight

        if sub != c_omponent:
            color.add(sub)
            sub_tree_found = list(pre_order2(
                T, sub, pre_order_filter=lambda v: v not in color))
            for v in sub_tree_found:
                cluster[v] = cluster_index
            # T.remove_tree(sub)
        elif sub == c_omponent:
            sub_tree_found = list(pre_order2(
                T, c_omponent, pre_order_filter=lambda v: v not in color))
        return sub_tree_found

    for i in range(p):
        Qu = Priority_queue(weight)

        target = c
        remain = target
        first_time = True
        last_cluster = False
        while len(C[i]) <= (1 - alpha/2)*target:

            if i == p-1:
                last_cluster = True
            if remain < 1:
                break

            sub = Best_Fit(remain, first_time, Qu, last_cluster, cluster_index)

            remain = remain - len(sub)

            C[i] += sub

            first_time = False
    return C


def First_Fit_Clustering(tree, c_omponent, p):
    ''' Clustering Trees based on the paper of Hambrusch and Liu but modified for better performance

        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - 'c_omponent' - The component of the MTG from which we start traversing
         - `p`  (int) - The number of clusters we want to fill
        :Returns:
            All the clusters as a list of lists of all the nodes of the tree
        :Returns Type:
            List
    '''
    cluster = T.property('cluster')
    vtx_id = c_omponent
    C = [[] for i in range(p)]
    weights = np.zeros(len(tree))
    for v in post_order(tree, c_omponent):
        weights[v] = 1 + sum([weights[vid] for vid in tree.children(v)])

    visited = set([])

    def order_children(vid):
        ordered = []
        p_queue = Priority_queue(weights)
        for vid in tree.children(vid):
            p_queue.append(vid)
        while p_queue.size() > 0:
            node = p_queue.pop()
            ordered.append(node)
        return ordered

    c = int(len(tree)/p)

    queue = [vtx_id]

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
            C[math.ceil(counter/c)-1].append(vtx_id)
            cluster[vtx_id] = math.ceil(counter/c)-1
            queue.pop()
    return C


def Best_Fit_Clustering_1(T, c_omponent, p, alpha):
    ''' Clustering Trees based on the paper of Hambrusch and Liu but modified for better performance
        Improvemnt of the function Best_Fit_Clustering, so that it does not change the structure of the tree during processing
        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - 'c_omponent' - The component of the MTG from which we start traversing
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
        :Returns:
            All the clusters as a list of lists of all the nodes of the tree
        :Returns Type:
            List
    '''
    cluster = T.property('cluster')
    color = T.property('color')
    C = [[] for i in range(p)]
    weight = np.zeros(len(T))
    for v in post_order(T, c_omponent):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])

    c = int(len(T)/p)
    #color = set()

    def Best_Fit(remain, Q, last_cluster, cluster_index):
        sub = None
        if last_cluster:
            sub = c_omponent
        else:
            for vid in post_order2(T, c_omponent, pre_order_filter=lambda v:v not in color):
                if T.parent(vid) != None:
                    if weight[vid] <= (1+alpha)*remain and weight[T.parent(vid)] > remain + alpha:
                        Q.append(vid)
                        if weight[vid] > (1-alpha/2)*remain:
                            break

            if Q.size() > 0:
                sub = Q.pop()
                index = weight[sub]
                for w in list(ancestors(T, sub)):
                    weight[w] = weight[w] - index

        if sub != c_omponent:
            color[sub] = 0
            sub_tree_found = list(post_order2(T, sub, pre_order_filter=lambda v: v not in color))
            for v in sub_tree_found:
                cluster[v] = cluster_index
        elif sub == c_omponent:
            color[c_omponent] = 0
            sub_tree_found = list(post_order2(T, c_omponent, pre_order_filter=lambda v: v not in color))
            for v in sub_tree_found:
                cluster[v] = cluster_index
        return sub_tree_found
    last_cluster = False
    for i in range(p):
        Qu = Priority_queue(weight)
        target = c
        if i == p-1:
            last_cluster = True

        C[i] += Best_Fit(target, Qu, last_cluster, i)

    return C


def Best_Fit_Clustering_MTG(T, p, alpha):
    ''' Clustering MTG(Tree) based on the paper of Hambrusch and Liu but modified for better performance

        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
        :Returns:
            All the clusters as a list of lists of all the nodes of the tree
        :Returns Type:
            List
    '''
    cluster = T.property('cluster')
    C = [[] for i in range(p)]

    remain = 0

    weight = np.zeros(len(T))
    internode_root = T.roots(T.max_scale())

    a = T.roots(T.max_scale())
    c_omponent = a[0]

    weight = np.zeros(len(T))
    for v in post_order(T, c_omponent):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])

    c = int(len(T)/p)
    color = set()

    def Best_Fit(remain, Q, last_cluster, cluster_index):

        sub = None
        if last_cluster:
            sub = c_omponent

        else:
            for vid in post_order2(T, c_omponent, pre_order_filter=lambda v: v not in color):
                if T.parent(vid) != None:
                    if weight[vid] <= (1+alpha)*remain and weight[T.parent(vid)] > remain + alpha:
                        Q.append(vid)
                        if weight[vid] > (1-alpha/2)*remain:
                            break

            if Q.size() > 0:
                sub = Q.pop()
                index = weight[sub]
                for w in list(ancestors(T, sub)):
                    weight[w] = weight[w] - index
        if sub != c_omponent:
            color.add(sub)
            sub_tree_found = list(post_order2(
                T, sub, pre_order_filter=lambda v: v not in color))
            for v in sub_tree_found:
                cluster[v] = cluster_index
        elif sub == c_omponent:
            sub_tree_found = list(post_order2(
                T, c_omponent, pre_order_filter=lambda v: v not in color))
            for v in sub_tree_found:
                cluster[v] = cluster_index
        return sub_tree_found

    remain = 0
    last_cluster = False
    for i in range(p):
        Qu = Priority_queue(weight)
        target = c
        if i == p-1:
            last_cluster = True
        sub = Best_Fit(target, Qu, last_cluster, i)
        C[i] += sub
    return C


def Best_Fit_Clustering_2(T, c_omponent, p, alpha):
    ''' Clustering Trees based on the paper of Hambrusch and Liu but modified for better performance
    Now, it uses level-order traversal instead of post-order to find the trees

        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - 'c_omponent' - The component of the MTG from which we start traversing
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
        :Returns:
            All the clusters as a list of lists of all the nodes of the tree
        :Returns Type:
            List
    '''
    C = [[] for i in range(p)]
    color = T.property('cluster')
    remain = 0

    weight = np.zeros(len(T))
    for v in post_order(T, c_omponent):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])
    cluster = T.property('cluster')
    c = int(len(T)/p)

    def Best_Fit(remain, Q, last_cluster, cluster_index):
        sub = None
        if last_cluster:
            sub = c_omponent
        else:
            for vid in level_order(T, c_omponent, visitor_filter=lambda v: v not in color):
                if T.parent(vid) != None:
                    if weight[vid] <= (1+alpha)*remain and weight[T.parent(vid)] > remain + alpha:
                        Q.append(vid)
                        if weight[vid] > (1-alpha/2)*remain:
                            break

            if Q.size() > 0:
                sub = Q.pop()
                index = weight[sub]
                for w in list(ancestors(T, sub)):
                    weight[w] = weight[w] - index

        if sub != c_omponent:
            color.add(sub)
            sub_tree_found = list(post_order2(
                T, sub, pre_order_filter=lambda v: v not in color))
            for v in sub_tree_found:
                cluster[v] = cluster_index
            # T.remove_tree(sub)
        elif sub == c_omponent:
            sub_tree_found = list(post_order2(
                T, c_omponent, pre_order_filter=lambda v: v not in color))
        return sub_tree_found
    remain = 0
    last_cluster = False
    for i in range(p):
        Qu = Priority_queue(weight)
        target = c
        if i == p-1:
            last_cluster = True

        sub = Best_Fit(target, Qu, last_cluster, i)
        C[i] += sub
    return C


def Best_Fit_Clustering_MTG_1(T, p, alpha):
    ''' Clustering MTG(Tree) based on the paper of Hambrusch and Liu but modified for better performance
    Now it uses level order instead of post order for finding the good subtrees

        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
        :Returns:
            All the clusters as a list of lists of all the nodes of the tree
        :Returns Type:
            List
    '''
    cluster = T.property('cluster')
    C = [[] for i in range(p)]

    remain = 0

    internode_root = T.roots(T.max_scale())

    a = T.roots(T.max_scale())
    c_omponent = a[0]

    weight = T.property('weight')
    for v in post_order(T, c_omponent):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])

    c = int(len(T)/p)
    color = set()

    def BF(remain, Q, last_cluster):

        sub = None

        if last_cluster:
            sub = c_omponent

        else:

            for vid in level_order(T, c_omponent, pre_visitor_filter=lambda v: v not in color):
                if T.parent(vid) != None:
                    if weight[vid] <= (1+alpha)*remain and weight[T.parent(vid)] > remain + alpha:
                        Q.append(vid)
                        if weight[vid] > (1-alpha/2)*remain:
                            break

            if Q.size() > 0:
                sub = Q.pop()
                index = weight[sub]
                for w in list(ancestors(T, sub)):
                    weight[w] = weight[w] - index

        if sub != c_omponent:
            color.add(sub)
            sub_tree_found = list(post_order2(
                T, sub, pre_order_filter=lambda v: v not in color))
            for v in sub_tree_found:
                cluster[v] = cluster_index
            T.remove_tree(sub)
        elif sub == c_omponent:
            sub_tree_found = list(post_order2(
                T, c_omponent, pre_order_filter=lambda v: v not in color))
            for v in sub_tree_found:
                cluster[v] = cluster_index
        return sub_tree_found

    remain = 0
    last_cluster = False
    for i in range(p):
        Qu = Priority_queue(weight)

        target = c
        if i == p-1:
            last_cluster = True

        sub = BF(target, Qu, last_cluster)
        C[i] += sub
    return C


"""
Experimental work
"""


def Best_Fit_Clustering_3(T, c_omponent, p, alpha):
    ''' Clustering MTG(Tree) based on the paper of Hambrusch and Liu but modified for better performance
    Find as many subtrees as possible by just one traversal using the level-order traversal

        :Parameters:
         - `T` (MTG) The MTG(Tree) which we want to cluster
         - `p`  (int) - The number of clusters we want to fill
         - 'alpha' (float) - The parameter which controls the difference on size between different clusters
        :Returns:
            All the clusters as a list of lists of all the nodes of the tree
        :Returns Type:
            List
    '''
    C = [[] for i in range(p)]
    cluster = T.property('cluster')
    # Create an empty queue for level order traversal
    queue = []

    # Enqueue Root and initialize height
    # Add first the children of the root into the queue
    queue.append(c_omponent)
    node = queue.pop(0)
    for vid in T.children(node):
        queue.append(vid)

    remain = 0

    weight = T.property('weight')
    for v in post_order(T, c_omponent):
        weight[v] = 1 + sum([weight[vid] for vid in T.children(v)])
    c = int(len(T)/p)

    def Best_Fit(remain, Q, last_cluster):

        sub = None

        if last_cluster:
            sub = c_omponent

        else:
            if len(queue) > 0:
                while len(queue) > 0:
                    node = queue.pop(0)
                    if weight[node] <= (1+alpha)*remain and weight[node] > (1-alpha/2)*remain:
                        sub = node
                        print("Found a good fit")
                        break
                    if weight[node] > (1+alpha)*remain:
                        print("Filling the queue")
                        for vid in T.children(node):
                            queue.append(vid)
            else:
                print("Entered else")
                queue.append(c_omponent)
                while len(queue) > 0:
                    node = queue.pop(0)
                    print("Node ", node, "with weight ", weight[node])
                    if weight[node] <= (1+alpha)*remain and weight[node] > (1-alpha/2)*remain:
                        print("Found a good fit")
                        sub = node
                        break
                    if weight[node] > (1+alpha)*remain:
                        print("Filling the queue")
                        for vid in T.children(node):
                            queue.append(vid)

        index = weight[sub]
        for w in list(ancestors(T, sub)):
            weight[w] = weight[w] - index

        if sub != c_omponent:
            sub_tree_found = list(post_order(T, sub))
            T.remove_tree(sub)
        elif sub == c_omponent:
            # ,pre_order_filter = lambda v: v not in color))
            sub_tree_found = list(post_order2(T, c_omponent))
        return sub_tree_found

    remain = 0
    last_cluster = False
    for i in range(p):
        Qu = Priority_queue(weight)

        target = c
        if i == p-1:
            last_cluster = True
        sub = Best_Fit(target, Qu, last_cluster)
        C[i] += sub
    return C
