#include <iostream>
#include <vector>
#include <tuple>
#include <string>
#include <sstream>
#include <set>
#include <algorithm>
#include <functional>
#include <fstream>

using namespace std;

using Matrix = vector<vector<bool>>;
using Result = tuple<Matrix, Matrix, Matrix, Matrix, Matrix>;

Result main_func(const string& s, const string& e) {
    vector<pair<int, int>> edges;
    stringstream ss(s);
    string line;
    while (getline(ss, line, '\n')) {
        if (line.empty()) continue;
        replace(line.begin(), line.end(), ',', ' ');
        stringstream ls(line);
        int a, b;
        ls >> a >> b;
        edges.emplace_back(a, b);
    }

    set<int> vertices;
    for (const auto& [a, b] : edges) {
        vertices.insert(a);
        vertices.insert(b);
    }

    int n = *max_element(vertices.begin(), vertices.end());
    vector<vector<int>> g(n + 1);
    for (const auto& [a, b] : edges)
        g[a].push_back(b);

    vector<int> depth(n + 1, -1);
    vector<int> parent(n + 1, -1);
    int root = stoi(e);

    function<void(int, int, int)> dfs = [&](int v, int p, int d) {
        depth[v] = d;
        parent[v] = p;
        for (int to : g[v])
            dfs(to, v, d + 1);
        };
    dfs(root, -1, 0);

    Matrix r1(n, vector<bool>(n, false));
    Matrix r2(n, vector<bool>(n, false));
    Matrix r3(n, vector<bool>(n, false));
    Matrix r4(n, vector<bool>(n, false));
    Matrix r5(n, vector<bool>(n, false));

    for (const auto& [a, b] : edges)
        r1[a - 1][b - 1] = true;

    for (const auto& [a, b] : edges)
        r2[b - 1][a - 1] = true;

    vector<vector<bool>> ancestor(n, vector<bool>(n, false));
    function<void(int, int)> mark = [&](int v, int anc) {
        for (int to : g[v]) {
            ancestor[anc - 1][to - 1] = true;
            mark(to, anc);
        }
        };
    for (int v : vertices)
        mark(v, v);

    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            if (ancestor[i][j] && !r1[i][j])
                r3[i][j] = true;

    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            if (r3[j][i])
                r4[i][j] = true;

    for (int i : vertices)
        for (int j : vertices)
            if (i != j && depth[i] == depth[j] && depth[i] != -1)
                r5[i - 1][j - 1] = true;

    return { r1, r2, r3, r4, r5 };
}


int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: ./task1 <csv_string_or_filename>\n";
        return 1;
    }

    string arg = argv[1];
    string csv_data;
    string root = "1";

    ifstream fin(arg);
    if (fin.good()) {
        stringstream buffer;
        buffer << fin.rdbuf();
        csv_data = buffer.str();
        fin.close();
    }
    else {
        csv_data = arg;
        size_t pos = 0;
        while ((pos = csv_data.find("\\n", pos)) != string::npos) {
            csv_data.replace(pos, 2, "\n");
            pos += 1;
        }
        replace(csv_data.begin(), csv_data.end(), ';', '\n');
    }

    auto [r1, r2, r3, r4, r5] = main_func(csv_data, root);

    auto print = [](const Matrix& m, const string& name) {
        cout << name << ":\n";
        for (const auto& row : m) {
            for (bool v : row)
                cout << (v ? "1 " : "0 ");
            cout << '\n';
        }
        cout << '\n';
        };

    print(r1, "r1 (relation of direct control)");
    print(r2, "r2 (relation of direct subordination)");
    print(r3, "r3 (relation of indirect control)");
    print(r4, "r4 (relation of indirect subordination)");
    print(r5, "r5 (relation of subordination at the same level)");

    return 0;
}
