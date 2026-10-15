import sys
from project.problem import Problem

class VegesAutomataProblem(Problem):
    
    def initialize_parser(self, parser):
        # Csak a --det argumentumot adjuk hozzá, elkerülve a már létező opciók (pl. --check) ütközését
        # Ellenőrizzük, hogy létezik-e már, hogy ne dobjon ArgumentError-t
        existing_actions = [action.dest for action in parser._actions]
        if 'det' not in existing_actions:
            parser.add_argument('--det', action='store_true', help='Determinizálás opció')

    def is_chosen_problem(self, args):
        # Akkor fut le, ha a --det kapcsoló meg van adva
        return getattr(args, 'det', False)

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
        nfa_transitions = {}
        for line_idx, line in enumerate(lines[4:], start=5):
            parts = line.split()
            if len(parts) != 3:
                print(f"Hiba: Hibás átmenet formátum a(z) {line_idx}. sorban: {line}", file=sys.stderr)
                sys.exit(1)
            src, symbol, dest = parts
            
            if src not in states or dest not in states or symbol not in alphabet:
                print(f"Hiba: Érvénytelen állapot vagy szimbólum az átmenetben: {line}", file=sys.stderr)
                sys.exit(1)
                
            key = (src, symbol)
            if key not in nfa_transitions:
                nfa_transitions[key] = set()
            nfa_transitions[key].add(dest)

        # Determinizálás (Hatványhalmaz-konstrukció)
        init_subset = frozenset([initial_state])
        state_map = {init_subset: 's0'}
        discovered_subsets = [init_subset]
        dfa_transitions = []

        idx = 0
        while idx < len(discovered_subsets):
            current_subset = discovered_subsets[idx]
            idx += 1
            current_name = state_map[current_subset]

            for symbol in alphabet:
                target_subset = set()
                for s in current_subset:
                    if (s, symbol) in nfa_transitions:
                        target_subset.update(nfa_transitions[(s, symbol)])
                
                if target_subset:
                    t_frozenset = frozenset(target_subset)
                    if t_frozenset not in state_map:
                        new_name = f"s{len(state_map)}"
                        state_map[t_frozenset] = new_name
                        discovered_subsets.append(t_frozenset)
                    target_name = state_map[t_frozenset]
                    dfa_transitions.append((current_name, symbol, target_name))

        # Rendezések a megadott szabályok szerint
        dfa_states_sorted = sorted([state_map[s] for s in discovered_subsets], key=lambda x: int(x[1:]))
        
        dfa_final_states = []
        for subset in discovered_subsets:
            if any(s in final_states for s in subset):
                dfa_final_states.append(state_map[subset])
        dfa_final_states_sorted = sorted(list(set(dfa_final_states)), key=lambda x: int(x[1:]))

        def transition_sort_key(t):
            src, symbol, dest = t
            return (int(src[1:]), symbol, int(dest[1:]))

        dfa_transitions_sorted = sorted(dfa_transitions, key=transition_sort_key)

        # Kiírás a kimeneti fájlba
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(" ".join(dfa_states_sorted) + "\n")
                f.write(" ".join(alphabet) + "\n")
                f.write(state_map[init_subset] + "\n")
                f.write(" ".join(dfa_final_states_sorted) + "\n")
                for src, symbol, dest in dfa_transitions_sorted:
                    f.write(f"{src} {symbol} {dest}\n")
        except IOError:
            print(f"Hiba: Nem sikerült írni a kimeneti fájlba: {output_path}", file=sys.stderr)
            sys.exit(1)