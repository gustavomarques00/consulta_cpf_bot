# start_extracao.py

import sys
import os

# Garante que a raiz do projeto esteja no path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from services import processador_cpfs

if __name__ == "__main__":
    processador_cpfs.main()
