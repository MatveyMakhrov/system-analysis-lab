#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <algorithm>

std::vector<std::vector<int>> csvToAdjMatrix(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open the file: " + filename);
    }

    std::string line;
    std::vector<std::pair<int, int>> edges;
    int maxNode = 0;

    while (std::getline(file, line)) {
        if (line.empty()) continue;
        std::stringstream ls(line);
        std::string uStr, vStr;
        if (std::getline(ls, uStr, ',') && std::getline(ls, vStr)) {
            int u = std::stoi(uStr);
            int v = std::stoi(vStr);
            edges.push_back({ u, v });
            maxNode = std::max({ maxNode, u, v });
        }
    }

    std::vector<std::vector<int>> adj(maxNode, std::vector<int>(maxNode, 0));

    for (auto [u, v] : edges) {
        adj[u - 1][v - 1] = 1;
        adj[v - 1][u - 1] = 1;
    }

    return adj;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Using: " << argv[0] << " <csv-file>\n";
        return 1;
    }

    try {
        auto adj = csvToAdjMatrix(argv[1]);
        int n = adj.size();

        std::cout << "  ";
        for (int j = 0; j < n; j++) {
            std::cout << static_cast<char>('A' + j) << " ";
        }
        std::cout << "\n";

        for (int i = 0; i < n; i++) {
            std::cout << static_cast<char>('A' + i) << " ";
            for (int j = 0; j < n; j++) {
                std::cout << adj[i][j] << " ";
            }
            std::cout << "\n";
        }
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
