import sys
from project.problem import Problem

class VegesAutomataProblem(Problem):
    
    def initialize_parser(self, parser):
        # Hozzáadjuk a --mini argumentumot a minimalizáláshoz
        existing_actions = [action.dest for action in parser._actions]
        if 'mini' not in existing_actions:
            parser.add_argument('--mini', action='store_true', help='Determinizmus és minimalizálás opció')

    def is_chosen_problem(self, args):
        # Akkor fut le, ha a --mini kapcsoló meg van adva
        return getattr(args, 'mini', False)

    def run(self, args):
        input_path = args.input
        output_path = args.output

        if not input_path or not output_path:
            print("Hiba: Hiányzó input vagy output fájl.", file=sys.stderr)
            sys.exit(1)

        # Beolvasás
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Hiba: A bemeneti fájl nem található: {input_path}", file=sys.stderr)
            sys.exit(1)

        if len(lines) < 4:
            print("Hiba: A bemeneti fájl szerkezete túl rövid.", file=sys.stderr)
            sys.exit(1)

        states = lines[0].split()
        alphabet = lines[1].split()
        initial_state = lines[2]
        final_states = set(lines[3].split())

        # Hibakezelés: Kezdő- és végállapotok érvényessége
        if initial_state not in states:
            print(f"Hiba: A kezdőállapot ({initial_state}) nincs benne az érvényes állapotok között.", file=sys.stderr)
            sys.exit(1)
        for fs in final_states:
            if fs not in states:
                print(f"Hiba: A végállapot ({fs}) nincs benne az érvényes állapotok között.", file=sys.stderr)
                sys.exit(1)

        # Átmenetek beolvasása és validálása
        transitions = {s: {} for s in states}
        for line_idx, line in enumerate(lines[4:], start=5):
            parts = line.split()
            if len(parts) != 3:
                print(f"Hiba: Hibás átmenet formátum a(z) {line_idx}. sorban: {line}", file=sys.stderr)
                sys.exit(1)
            src, symbol, dest = parts
            
            if src not in states or dest not in states or symbol not in alphabet:
                print(f"Hiba: Érvénytelen állapot vagy szimbólum az átmenetben: {line}", file=sys.stderr)
                sys.exit(1)
                
            transitions[src][symbol] = dest

        # DFA Minimalizálás (Moore-algoritmus / Partíció-finomítás)
        final_set = final_states & set(states)
        non_final_set = set(states) - final_set

        P = []
        if final_set:
            P.append(final_set)
        if non_final_set:
            P.append(non_final_set)

        while True:
            new_P = []
            for group in P:
                splits = {}
                for s in group:
                    # Aláírás (signature) meghatározása az átmenetek célcsoportjai alapján
                    signature = tuple(
                        next((i for i, g in enumerate(P) if transitions[s].get(sym) in g), -1)
                        for sym in alphabet
                    )
                    if signature not in splits:
                        splits[signature] = set()
                    splits[signature].add(s)
                new_P.extend(splits.values())
            
            if len(new_P) == len(P):
                break
            P = new_P

        # Állapotok elnevezése az összevont csoportok legkisebb indexe alapján
        group_to_name = {}
        for group in P:
            min_idx = min(int(s[1:]) for s in group)
            group_name = f"s{min_idx}"
            for s in group:
                group_to_name[s] = group_name

        mini_states = sorted(list(set(group_to_name.values())), key=lambda x: int(x[1:]))
        mini_initial = group_to_name[initial_state]
        
        mini_final_states = sorted(
            list(set(group_to_name[s] for s in final_states if s in group_to_name)),
            key=lambda x: int(x[1:])
        )

        # Új átmenetek generálása
        mini_transitions = set()
        for group in P:
            rep = sorted(list(group), key=lambda x: int(x[1:]))[0]
            src_name = group_to_name[rep]
            for sym in alphabet:
                if sym in transitions[rep]:
                    dest = transitions[rep][sym]
                    dest_name = group_to_name[dest]
                    mini_transitions.add((src_name, sym, dest_name))

        def transition_sort_key(t):
            src, symbol, dest = t
            return (int(src[1:]), symbol, int(dest[1:]))

        mini_transitions_sorted = sorted(list(mini_transitions), key=transition_sort_key)

        # Kiírás a kimeneti fájlba
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(" ".join(mini_states) + "\n")
                f.write(" ".join(alphabet) + "\n")
                f.write(mini_initial + "\n")
                f.write(" ".join(mini_final_states) + "\n")
                for src, symbol, dest in mini_transitions_sorted:
                    f.write(f"{src} {symbol} {dest}\n")
        except IOError:
            print(f"Hiba: Nem sikerült írni a kimeneti fájlba: {output_path}", file=sys.stderr)
            sys.exit(1)