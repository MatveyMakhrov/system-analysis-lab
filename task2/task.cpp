#include <vector>
#include <string>
#include <sstream>
#include <cmath>
#include <tuple>
#include <algorithm>
#include <map>
#include <set>
#include <fstream>
#include <iostream>

using namespace std;

vector<pair<int, int>> readCSV(const string& filepath) {
    vector<pair<int, int>> edges;
    ifstream file(filepath);
    string line;

    if (!file.is_open()) {
        cerr << "File opening error: " << filepath << endl;
        return edges;
    }

    while (getline(file, line)) {
        if (line.empty()) continue;
        size_t pos = line.find(',');
        if (pos != string::npos) {
            int from = stoi(line.substr(0, pos));
            int to = stoi(line.substr(pos + 1));
            edges.push_back({ from, to });
        }
    }

    file.close();
    return edges;
}

tuple<float, float> task(const string& filepath, const string& e) {
    vector<pair<int, int>> edges = readCSV(filepath);
    int root = stoi(e);

    set<int> nodes_set;
    for (const auto& edge : edges) {
        nodes_set.insert(edge.first);
        nodes_set.insert(edge.second);
    }

    vector<int> nodes(nodes_set.begin(), nodes_set.end());
    int n = nodes.size();

    map<int, int> node_to_index;
    for (int i = 0; i < n; i++) {
        node_to_index[nodes[i]] = i;
    }

    vector<vector<bool>> adj(n, vector<bool>(n, false));
    for (const auto& edge : edges) {
        int from_idx = node_to_index[edge.first];
        int to_idx = node_to_index[edge.second];
        adj[from_idx][to_idx] = true;
    }

    vector<vector<bool>> r1 = adj;

    vector<vector<bool>> r2(n, vector<bool>(n, false));
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            r2[i][j] = adj[j][i];
        }
    }

    vector<vector<bool>> r3(n, vector<bool>(n, false));
    vector<vector<bool>> reachable = adj;
    for (int k = 0; k < n; k++) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (reachable[i][k] && reachable[k][j]) {
                    reachable[i][j] = true;
                }
            }
        }
    }
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            r3[i][j] = reachable[i][j] && !adj[i][j] && (i != j);
        }
    }

    vector<vector<bool>> r4(n, vector<bool>(n, false));
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            r4[i][j] = r3[j][i];
        }
    }

    vector<vector<bool>> r5(n, vector<bool>(n, false));

    map<int, int> level;
    level[root] = 0;
    bool changed = true;
    while (changed) {
        changed = false;
        for (const auto& edge : edges) {
            if (level.count(edge.first) && !level.count(edge.second)) {
                level[edge.second] = level[edge.first] + 1;
                changed = true;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i != j && level[nodes[i]] == level[nodes[j]]) {
                r5[i][j] = true;
            }
        }
    }

    vector<vector<int>> l(n, vector<int>(5, 0));

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (r1[i][j]) l[i][0]++;
            if (r2[i][j]) l[i][1]++;
            if (r3[i][j]) l[i][2]++;
            if (r4[i][j]) l[i][3]++;
            if (r5[i][j]) l[i][4]++;
        }
    }

    double total_entropy = 0.0;
    int max_possible_connections = n - 1;

    for (int i = 0; i < n; i++) {
        for (int rel = 0; rel < 5; rel++) {
            if (l[i][rel] > 0) {
                double probability = static_cast<double>(l[i][rel]) / max_possible_connections;
                double entropy = -probability * log2(probability);
                total_entropy += entropy;
            }
        }
    }

    double c = 1.0 / (exp(1) * log(2));
    double reference_entropy = c * n * 5;
    double normalized_complexity = total_entropy / reference_entropy;

    total_entropy = round(total_entropy * 10) / 10;
    normalized_complexity = round(normalized_complexity * 10) / 10;

    return make_tuple(static_cast<float>(total_entropy), static_cast<float>(normalized_complexity));
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "Usage " << argv[0] << " <path_csv_file> <root_node>" << endl;
        return 1;
    }

    string filepath = argv[1];
    string root = argv[2];

    auto result = task(filepath, root);
    cout << "Entropy: " << get<0>(result) << ", Normalized complexity: " << get<1>(result) << endl;

    return 0;
}