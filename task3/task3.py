import json
import sys

def main(json_str1, json_str2):
    """
    Находит ядро противоречий между двумя ранжировками
    
    Args:
        json_str1 (str): JSON-строка с первой ранжировкой
        json_str2 (str): JSON-строка со второй ранжировкой
        
    Returns:
        str: JSON-строка с ядром противоречий
    """
    # Парсим JSON-строки в списки
    ranking1 = json.loads(json_str1)
    ranking2 = json.loads(json_str2)
    
    # Получаем плоские списки объектов для обеих ранжировок
    objects = extract_objects(ranking1)
    
    # Строим матрицы предпочтений
    matrix1 = build_preference_matrix(ranking1, objects)
    matrix2 = build_preference_matrix(ranking2, objects)
    
    # Находим ядро противоречий
    contradiction_core = find_contradiction_core(matrix1, matrix2, objects)
    
    # Возвращаем результат в формате JSON
    return json.dumps(contradiction_core)

def extract_objects(ranking):
    """Извлекает все объекты из ранжировки в плоский список"""
    objects = []
    for item in ranking:
        if isinstance(item, list):
            # Это кластер - добавляем все элементы кластера
            objects.extend(item)
        else:
            # Это одиночный объект
            objects.append(item)
    return objects

def build_preference_matrix(ranking, objects):
    """
    Строит матрицу предпочтений для данной ранжировки
    
    Матрица M такая, что M[i][j] = 1, если объект i не хуже объекта j
    (объект i лучше или неразличим с объектом j)
    """
    n = len(objects)
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    
    # Создаем словарь для быстрого доступа к позициям объектов
    obj_to_pos = {}
    pos = 0
    
    # Проходим по ранжировке и определяем отношения предпочтения
    for cluster in ranking:
        if isinstance(cluster, list):
            # Кластер - все объекты в кластере неразличимы
            cluster_objects = cluster
        else:
            # Одиночный объект
            cluster_objects = [cluster]
        
        # Записываем позиции объектов
        for obj in cluster_objects:
            obj_to_pos[obj] = pos
            pos += 1
    
    # Заполняем матрицу предпочтений
    for i in range(n):
        for j in range(n):
            obj_i = objects[i]
            obj_j = objects[j]
            
            pos_i = obj_to_pos[obj_i]
            pos_j = obj_to_pos[obj_j]
            
            # Объект i не хуже объекта j, если его позиция >= позиции j
            # (в нашей нумерации чем правее, тем лучше)
            if pos_i >= pos_j:
                matrix[i][j] = 1
            else:
                matrix[i][j] = 0
    
    # Диагональ всегда 1 (объект не хуже себя самого)
    for i in range(n):
        matrix[i][i] = 1
    
    return matrix

def find_contradiction_core(matrix1, matrix2, objects):
    """
    Находит ядро противоречий между двумя матрицами предпочтений
    
    Ядро противоречий - это пары объектов, для которых эксперты
    имеют противоположные мнения
    """
    n = len(objects)
    contradiction_pairs = []
    
    # Проверяем все пары объектов
    for i in range(n):
        for j in range(n):
            if i != j:  # Не сравниваем объект с самим собой
                # Противоречие возникает, когда в одной матрице i не хуже j,
                # а в другой j не хуже i, но не одновременно
                condition1 = matrix1[i][j] == 1 and matrix2[j][i] == 1
                condition2 = matrix1[j][i] == 1 and matrix2[i][j] == 1
                
                if condition1 or condition2:
                    # Нашли противоречие - добавляем пару
                    pair = sorted([objects[i], objects[j]])
                    if pair not in contradiction_pairs:
                        contradiction_pairs.append(pair)
    
    return contradiction_pairs

if __name__ == "__main__":
    # Чтение аргументов командной строки
    if len(sys.argv) != 3:
        print("Использование: python task.py <json_str1> <json_str2>")
        sys.exit(1)
    
    json_str1 = sys.argv[1]
    json_str2 = sys.argv[2]
    
    result = main(json_str1, json_str2)
    print(result)