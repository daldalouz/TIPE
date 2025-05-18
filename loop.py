# -*- coding: utf-8 -*-
import subprocess
import time
import threading
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Paramètres
SCRIPT = "NewTest.py"
NB_EXECUTIONS = 50
TIMEOUT_SILENCE = 10  # secondes d'inactivité avant kill
KEYWORD = "Ronde"
RESULTS_FILE = "resultats.txt"

def run_once(result_file, iteration):
    process = subprocess.Popen(
        ["python", SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    output_lines = []
    last_output_time = time.time()
    stop_event = threading.Event()

    def read_output():
        nonlocal last_output_time
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                print(line)
                output_lines.append(line)
                last_output_time = time.time()
        stop_event.set()

    reader_thread = threading.Thread(target=read_output)
    reader_thread.start()

    while not stop_event.is_set():
        time.sleep(0.1)
        if time.time() - last_output_time > TIMEOUT_SILENCE:
            print("Inactivité détectée. Fin du processus.")
            process.terminate()
            break

    reader_thread.join()
    process.wait()

    # Trouver la dernière ligne contenant "ronde"
    last_index = None
    for i in reversed(range(len(output_lines))):
        if KEYWORD.lower() in output_lines[i].lower():
            last_index = i
            break

    # Récupérer cette ligne + la ligne qui la précède si elle existe
    lines_to_save = []
    if last_index is not None:
        if last_index > 0:
            lines_to_save.append(output_lines[last_index - 1])
        lines_to_save.append(output_lines[last_index])

    # Écriture immédiate
    result_file.write(f"\n=== Exécution {iteration + 1} ===\n")
    if lines_to_save:
        for line in lines_to_save:
            result_file.write(line + "\n")
    else:
        result_file.write("Aucune ligne contenant 'ronde'.\n")
    result_file.flush()

# Boucle principale
with open(RESULTS_FILE, "w", encoding="utf-8") as f:
    for i in range(NB_EXECUTIONS):
        print(f"\n=== Exécution {i + 1} ===")
        run_once(f, i)
