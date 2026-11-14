import sys
import re
from project.problem import Problem

class AndroidLogcatProblem(Problem):

    def initialize_parser(self, parser):
        # Hozzáadjuk a --rgx argumentumot, ha még nincs benne
        existing_actions = [action.dest for action in parser._actions]
        if 'rgx' not in existing_actions:
            parser.add_argument('--rgx', type=int, choices=[1, 2, 3, 4, 5], help='Android logcat regex feladat sorszáma (1-5)')

    def is_chosen_problem(self, args):
        # Akkor fut le, ha a --rgx paraméter értéke 1 és 5 közé esik
        return getattr(args, 'rgx', None) in [1, 2, 3, 4, 5]

    def run(self, args):
        input_path = args.input
        output_path = args.output

        if not input_path or not output_path:
            print("Hiba: Hiányzó input vagy output fájl.", file=sys.stderr)
            sys.exit(1)

        # Beolvasás
        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Hiba: A bemeneti fájl nem található: {input_path}", file=sys.stderr)
            sys.exit(1)

        output_lines = []
        rgx_num = args.rgx

        if rgx_num == 1:
            # 1. Feladat: 10 alpont, soronként egy darab számmal a kimeneten
            p1 = re.compile(r'^10-15')
            p2 = re.compile(r'^10-15 10:18:51')
            p3 = re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}:51')
            p4 = re.compile(r'^[0-9-]+ [0-9:.]+ +\d+ +\d+ [IDVEFAW] +[^:]*lowmemorykiller[^:]*:', re.IGNORECASE)
            p5 = re.compile(r'^[0-9-]+ 10:18:51\.\d+ +221 +')
            p6 = re.compile(r'^[0-9-]+ [0-9:.]+ +\d+ +\d+ E ')
            p7 = re.compile(r'^[0-9-]+ [0-9:.]+ +\d+ +\d+ W +[^:]*PackageManager[^:]*:', re.IGNORECASE)
            p8 = re.compile(r'^[0-9-]+ [0-9:.]+ +\d+ +\d+ D .*ExoPlayer')
            p9 = re.compile(r'^[0-9-]+ [0-9:.]+ +\d+ +\d+ [EW] .*\.java:')
            p10 = re.compile(r'^[0-9-]+ [0-9:.]+ +\d+ +\d+ [IDVEFAW] +[^:]+: .*Thread')

            c1 = sum(1 for line in lines if p1.search(line))
            c2 = sum(1 for line in lines if p2.search(line))
            c3 = sum(1 for line in lines if p3.search(line))
            c4 = sum(1 for line in lines if p4.search(line))
            c5 = sum(1 for line in lines if p5.search(line))
            c6 = sum(1 for line in lines if p6.search(line))
            c7 = sum(1 for line in lines if p7.search(line))
            c8 = sum(1 for line in lines if p8.search(line))
            c9 = sum(1 for line in lines if p9.search(line))
            c10 = sum(1 for line in lines if p10.search(line))

            output_lines = [str(c1), str(c2), str(c3), str(c4), str(c5), str(c6), str(c7), str(c8), str(c9), str(c10)]

        elif rgx_num == 2:
            # 2. Feladat: Az összes hiba (E sorok) származási helye (.java fájlnevek) előfordulási sorrendben
            error_pattern = re.compile(r'^[0-9-]+ [0-9:.]+ +\d+ +\d+ E ')
            java_file_pattern = re.compile(r'([A-Za-z0-9_]+\.java)')

            for line in lines:
                if error_pattern.search(line):
                    matches = java_file_pattern.findall(line)
                    for m in matches:
                        output_lines.append(m)

        elif rgx_num == 3:
            # 3. Feladat: Különböző process id-k megőrizve az első előfordulás sorrendjét
            seen_pids = set()
            pid_extract_pattern = re.compile(r'^[0-9-]+ [0-9:.]+ +([0-9]+)')

            for line in lines:
                m = pid_extract_pattern.search(line)
                if m:
                    pid = m.group(1)
                    if pid not in seen_pids:
                        seen_pids.add(pid)
                        output_lines.append(pid)

        elif rgx_num == 4:
            # 4. Feladat: A legtöbb errort tartalmazó process. Forma: PID=xx (xx errors)
            error_pattern = re.compile(r'^[0-9-]+ [0-9:.]+ +([0-9]+) +\d+ E ')
            error_counts = {}

            for line in lines:
                m = error_pattern.search(line)
                if m:
                    pid = m.group(1)
                    error_counts[pid] = error_counts.get(pid, 0) + 1

            if error_counts:
                max_errors = max(error_counts.values())
                max_pids = sorted([pid for pid, count in error_counts.items() if count == max_errors], key=lambda x: int(x) if x.isdigit() else x)
                for max_pid in max_pids:
                    err_label = "error" if max_errors == 1 else "errors"
                    output_lines.append(f"PID={max_pid} ({max_errors} {err_label})")
            else:
                output_lines.append("PID=None (0 errors)")

        elif rgx_num == 5:
            # 5. Feladat: Fő szálon történt hibák száma (amikor a PID és TID megegyezik)
            equal_thread_error_pattern = re.compile(r'^[0-9-]+ [0-9:.]+ +([0-9]+) +\1 +E ')
            count = sum(1 for line in lines if equal_thread_error_pattern.search(line))
            output_lines.append(str(count))

        # Eredmények kiírása a kimeneti fájlba
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(output_lines) + ("\n" if output_lines else ""))
        except IOError:
            print(f"Hiba: Nem sikerült írni a kimeneti fájlba: {output_path}", file=sys.stderr)
            sys.exit(1)