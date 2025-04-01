# scripts/limpar_cache.py

import os
import shutil

from colorama import init, Fore

init(autoreset=True)

paths = [
    "session",
    "session.session",
    "session.json",
    "shared/data/request_count.txt",
    "shared/data/request_date.txt",
    "shared/data/request_log.json",
    "downloads",
    "scripts/arquivos/processados",
]

for path in paths:
    if os.path.isfile(path):
        os.remove(path)
        print(Fore.YELLOW + f"🧹 Arquivo removido: {path}")
    elif os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)
        print(Fore.CYAN + f"🧼 Pasta limpa: {path}")

print(Fore.GREEN + "✅ Limpeza completa.")
