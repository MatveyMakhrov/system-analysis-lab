import json
import sys
from typing import List, Dict


def membership_function(x: float, points: List[List[float]]) -> float:
    """
    Кусочно-линейная функция принадлежности
    """
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        if x1 <= x <= x2:
            if x1 == x2:
                return max(y1, y2)
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

    return 0.0


def main(
    temperature_json: str,
    control_json: str,
    rules_json: str,
    temperature_value: float
) -> float:
    """
    Алгоритм нечеткого управления (Мамдани)
    """

    temp_data = json.loads(temperature_json)["температура"]
    control_data = json.loads(control_json)["температура"]
    rules = json.loads(rules_json)

    temp_memberships: Dict[str, float] = {}
    for term in temp_data:
        temp_memberships[term["id"]] = membership_function(
            temperature_value, term["points"]
        )

    control_min = min(p[0] for t in control_data for p in t["points"])
    control_max = max(p[0] for t in control_data for p in t["points"])

    step = 0.01
    s_values = []
    s = control_min
    while s <= control_max:
        s_values.append(round(s, 4))
        s += step

    aggregated = {s: 0.0 for s in s_values}

    for temp_term, control_term in rules:
        activation = temp_memberships.get(temp_term, 0.0)
        if activation == 0:
            continue

        control_def = next(
            t for t in control_data if t["id"] == control_term
        )

        for s in s_values:
            mu = membership_function(s, control_def["points"])
            aggregated[s] = max(
                aggregated[s],
                min(activation, mu)
            )

    max_mu = max(aggregated.values())
    for s in sorted(aggregated):
        if aggregated[s] == max_mu:
            return float(s)

    return 0.0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Использование:\n"
            "python task.py <temperature.json> <control.json> <rules.json> <temperature_value>"
        )
        sys.exit(1)

    temp_path = sys.argv[1]
    control_path = sys.argv[2]
    rules_path = sys.argv[3]
    temperature_value = float(sys.argv[4])

    with open(temp_path, "r", encoding="utf-8") as f:
        temperature_json = f.read()

    with open(control_path, "r", encoding="utf-8") as f:
        control_json = f.read()

    with open(rules_path, "r", encoding="utf-8") as f:
        rules_json = f.read()

    result = main(
        temperature_json,
        control_json,
        rules_json,
        temperature_value
    )

    print(result)
