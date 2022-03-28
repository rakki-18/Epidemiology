from collections import defaultdict
import pandas as pd

def vaccination_strategy(model):
    contact_data = model.df
    contact_graph = defaultdict(list)
    vertices=[]
    vaccination_count = int(0.2 * model.metadata.shape[0])
    index=0
    while index < contact_data.shape[0]:
        id1=contact_data['Person 1'][index]
        id2=contact_data['Person 2'][index]
        if not(id1 in contact_graph.keys() and id2 in contact_graph[id1]):
          contact_graph[id1].append(id2)
          contact_graph[id2].append(id1)
        if id1 not in vertices:
          vertices.append(id1)
        if id2 not in vertices:
          vertices.append(id2)
        index+=1
    Time=0
      
    return findAP(contact_graph,vertices,Time)

def findAP(contact_graph,vertices,Time):
    visited = [False] * len(vertices)
    disc = [float("Inf")] * len(vertices)
    low = [float("Inf")] * len(vertices)
    parent = [-1] * len(vertices)
    AP = [False] * len(vertices)
    vaccinated=[]
    # to find articulation points 
    for i in range(len(vertices)):
        if visited[i] == False:
            APDetails(contact_graph, vertices, i, visited, parent, low, disc, AP,Time)
        for p, value in enumerate (AP):
            if value == True:
                vaccinated.append(vertices[p])
    return vaccinated
      
def APDetails(contact_graph, vertices, u, visited, parent, low, disc, AP, Time):

    #Count of children in current node 
    children = 0
 
    # Marking the current node as visited and print it
    visited[u]= True
 
    # Initialize discovery time and low value
    disc[u] = Time
    low[u] = Time
    Time += 1
 
    #Recursive execution for all the vertices adjacent to this vertex
    for v in contact_graph[vertices[u]]:
        if visited[vertices.index(v)] == False:
            parent[vertices.index(v)] = u
            children += 1
            APDetails(contact_graph, vertices, vertices.index(v), visited, parent, low, disc, AP,Time)

            low[u] = min(low[u], low[vertices.index(v)])
            # print(children)
            # print(parent[u])
            # print(low[u])
            # print(low[vertices.index(v)])
            # u is a Cut Vertex in following cases 
            # if,u is root of DFS tree & has two or more chilren. 
            if parent[u] == -1 and children > 1: 

                AP[u] = True
            # If, u is not root & low value of one of its child 
            # is more than discovery value of vertex u. 
            if parent[u] != -1 and low[vertices.index(v)] >= disc[u]: 
                AP[u] = True  
                          
        elif vertices.index(v) != parent[u]: 
            # Update low value of u for parent function calls.
            low[u] = min(low[u], disc[vertices.index(v)])

