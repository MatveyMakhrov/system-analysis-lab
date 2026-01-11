import json
import sys
import os
import re
from collections import deque

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
            return json.loads(fix_json_string(content))

    try:
        return json.loads(input_str)
    except json.JSONDecodeError:
        return json.loads(fix_json_string(input_str))


def extract_objects(ranking):
    objects = []
    for item in ranking:
        if isinstance(item, list):
            objects.extend(item)
        else:
            objects.append(item)
    return objects


def build_preference_matrix(ranking, objects):
    n = len(objects)
    matrix = [[0] * n for _ in range(n)]

    obj_to_pos = {}
    pos = 0

    for cluster in ranking:
        cluster_objects = cluster if isinstance(cluster, list) else [cluster]
        for obj in cluster_objects:
            obj_to_pos[obj] = pos
            pos += 1

    for i in range(n):
        for j in range(n):
            if obj_to_pos[objects[i]] >= obj_to_pos[objects[j]]:
                matrix[i][j] = 1

    for i in range(n):
        matrix[i][i] = 1

    return matrix


def find_contradiction_core(matrix1, matrix2, objects):
    n = len(objects)
    core = []

    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            if (matrix1[i][j] == 1 and matrix2[j][i] == 1) or \
               (matrix1[j][i] == 1 and matrix2[i][j] == 1):
                pair = sorted([objects[i], objects[j]])
                if pair not in core:
                    core.append(pair)

    return core


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

    for i, cluster in enumerate(ranking):
        if obj1 in cluster:
            pos1 = i
        if obj2 in cluster:
            pos2 = i

    if pos1 == pos2:
        return 0
    if pos1 < pos2:
        return 1
    if pos1 > pos2:
        return -1
    return 0


def build_consensus_ranking(r1, r2):
    all_objects = sorted(
        {x for c in r1 + r2 for x in c},
        key=lambda x: int(x) if x.isdigit() else x
    )

    n = len(all_objects)
    comparison = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            c1 = compare_pair(all_objects[i], all_objects[j], r1)
            c2 = compare_pair(all_objects[i], all_objects[j], r2)
            comparison[i][j] = c1 if c1 == c2 else 0

    visited = [False] * n
    clusters = []

    for i in range(n):
        if visited[i]:
            continue
        group = [i]
        visited[i] = True
        for j in range(n):
            if not visited[j] and comparison[i][j] == 0 and comparison[j][i] == 0:
                group.append(j)
                visited[j] = True
        clusters.append(group)

    graph = [[] for _ in clusters]
    indeg = [0] * len(clusters)

    for i in range(len(clusters)):
        for j in range(len(clusters)):
            if i == j:
                continue
            better = True
            for a in clusters[i]:
                for b in clusters[j]:
                    if comparison[a][b] != 1:
                        better = False
                        break
            if better:
                graph[i].append(j)
                indeg[j] += 1

    q = deque(i for i in range(len(indeg)) if indeg[i] == 0)
    order = []

    while q:
        v = q.popleft()
        order.append(v)
        for u in graph[v]:
            indeg[u] -= 1
            if indeg[u] == 0:
                q.append(u)

    result = []
    for idx in order:
        cluster = [all_objects[i] for i in clusters[idx]]
        cluster = [int(x) if x.isdigit() else x for x in cluster]
        result.append(cluster[0] if len(cluster) == 1 else sorted(cluster))

    return result


def main(arg1, arg2):
    ranking1 = load_input(arg1)
    ranking2 = load_input(arg2)

    objects = extract_objects(ranking1)

    m1 = build_preference_matrix(ranking1, objects)
    m2 = build_preference_matrix(ranking2, objects)

    contradiction_core = find_contradiction_core(m1, m2, objects)

    r1 = parse_ranking(ranking1)
    r2 = parse_ranking(ranking2)
    consensus = build_consensus_ranking(r1, r2)

    return json.dumps({
        "contradiction_core": contradiction_core,
        "consensus_ranking": consensus
    }, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python task.py <ранжировка1> <ранжировка2>")
        sys.exit(1)

    print(main(sys.argv[1], sys.argv[2]))
