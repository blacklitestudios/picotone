#include <cstdlib>

int main() {
    // 1. Use absolute paths for everything.
    // 2. Point directly to the python binary inside the venv.
    // 3. Use && so the command stops if the 'cd' fails.
    std::system("cd /Users/kgvadmin/Documents/GitHub/nafchalica && ./venv/bin/python3 main.py"); 

    return 0;
}