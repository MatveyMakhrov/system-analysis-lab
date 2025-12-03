import json
import sys
import os
import re
from collections import defaultdict

def parse_ranking(ranking):
    result = []
    for item in ranking:
        if isinstance(item, list):
            result.append([str(x) for x in item])
        else:
            result.append([str(item)])
    return result

def compare_pair(obj1, obj2, ranking):

    pos1 = pos2 = -1
    cluster1 = cluster2 = None
    
    for i, cluster in enumerate(ranking):
        if obj1 in cluster:
            pos1 = i
            cluster1 = cluster
        if obj2 in cluster:
            pos2 = i
            cluster2 = cluster
    
    if pos1 == -1 or pos2 == -1:
        return 0
    
    if pos1 < pos2:
        return 1
    elif pos1 > pos2:
        return -1
    else:
        return 0

def build_consensus_ranking(ranking1, ranking2):
    all_objects = set()
    for cluster in ranking1:
        all_objects.update(cluster)
    for cluster in ranking2:
        all_objects.update(cluster)
    
    all_objects = sorted(all_objects, key=lambda x: (int(x) if x.isdigit() else x))
    
    n = len(all_objects)
    comparison = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i == j:
                comparison[i][j] = 0
                continue
            
            obj_i = all_objects[i]
            obj_j = all_objects[j]
            
            comp1 = compare_pair(obj_i, obj_j, ranking1)
            comp2 = compare_pair(obj_i, obj_j, ranking2)
            
            if comp1 == comp2:
                comparison[i][j] = comp1
            elif comp1 == 0 and comp2 != 0:
                comparison[i][j] = comp2
            elif comp2 == 0 and comp1 != 0:
                comparison[i][j] = comp1
            elif comp1 == -comp2:
                comparison[i][j] = 0
            else:
                comparison[i][j] = 0
    
    clusters = []
    visited = [False] * n
    
    for i in range(n):
        if visited[i]:
            continue
        
        current_cluster = [i]
        visited[i] = True
        
        for j in range(n):
            if not visited[j]:
                if comparison[i][j] == 0 and comparison[j][i] == 0:
                    can_add = True
                    for k in current_cluster:
                        if comparison[k][j] != 0 or comparison[j][k] != 0:
                            can_add = False
                            break
                    
                    if can_add:
                        current_cluster.append(j)
                        visited[j] = True
        
        cluster_objects = [all_objects[idx] for idx in current_cluster]
        cluster_objects = sorted(cluster_objects, key=lambda x: (int(x) if x.isdigit() else x))
        clusters.append(cluster_objects)
    
    m = len(clusters)
    graph = [[] for _ in range(m)]
    in_degree = [0] * m
    
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            
            i_better_j = True
            for obj_i in clusters[i]:
                idx_i = all_objects.index(obj_i)
                for obj_j in clusters[j]:
                    idx_j = all_objects.index(obj_j)
                    if comparison[idx_i][idx_j] != 1:
                        i_better_j = False
                        break
                if not i_better_j:
                    break
            
            if i_better_j:
                graph[i].append(j)
                in_degree[j] += 1
    
    from collections import deque
    queue = deque([i for i in range(m) if in_degree[i] == 0])
    ordered_indices = []
    
    while queue:
        current = queue.popleft()
        ordered_indices.append(current)
        
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    final_ranking = []
    for idx in ordered_indices:
        cluster = clusters[idx]
        if len(cluster) == 1:
            item = cluster[0]
            final_ranking.append(int(item) if item.isdigit() else item)
        else:
            cluster_items = [int(x) if x.isdigit() else x for x in cluster]
            final_ranking.append(sorted(cluster_items))
    
    return final_ranking

def fix_json_string(json_str):
    fixed = re.sub(r',\s*([\]}])', r'\1', json_str)
    
    in_string = False
    escape = False
    result = []
    
    for char in fixed:
        if escape:
            escape = False
            result.append(char)
        elif char == '\\':
            escape = True
            result.append(char)
        elif char == '"':
            in_string = not in_string
            result.append(char)
        elif char == "'" and not in_string:
            result.append('"')
        else:
            result.append(char)
    
    return ''.join(result)

def load_input(input_str):
    if os.path.exists(input_str):
        with open(input_str, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            fixed_content = fix_json_string(content)
            return json.loads(fixed_content)
    
    try:
        return json.loads(input_str)
    except json.JSONDecodeError:
        fixed_str = fix_json_string(input_str)
        return json.loads(fixed_str)

def main(json_str1, json_str2):
    ranking1 = load_input(json_str1)
    ranking2 = load_input(json_str2)
    
    r1 = parse_ranking(ranking1)
    r2 = parse_ranking(ranking2)
    
    consensus = build_consensus_ranking(r1, r2)
    
    return json.dumps(consensus, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python task.py '<ранжировка1>' '<ранжировка2>'")
        sys.exit(1)
    
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    
    for i, arg in enumerate([arg1, arg2]):
        if arg.startswith("'") and arg.endswith("'"):
            if i == 0:
                arg1 = arg[1:-1]
            else:
                arg2 = arg[1:-1]
        elif arg.startswith('"') and arg.endswith('"'):
            if i == 0:
                arg1 = arg[1:-1]
            else:
                arg2 = arg[1:-1]
    
    try:
        result = main(arg1, arg2)
        print(result)
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)