import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Véges automata determinizálása")
    parser.add_argument("--input", required=True, help="A bemeneti fájl útvonala")
    parser.add_argument("--output", required=True, help="A kimeneti fájl útvonala")
    parser.add_argument("--det", action="store_true", help="Jelzi, hogy determinizálni kell az automatát")
    args = parser.parse_args()

    # Beolvasás
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Hiba: A megbelelő bemeneti fájl nem található: {args.input}", file=sys.stderr)
        sys.exit(1)

    if len(lines) < 4:
        print("Hiba: A bemeneti fájl szerkezete túl rövid.", file=sys.stderr)
        sys.exit(1)

    states = lines[0].split()
    alphabet = lines[1].split()
    initial_state = lines[2]
    final_states = set(lines[3].split())

    # Alapvető hibakezelés: Kezdő- és végállapotok érvényességének ellenőrzése
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
        
        if src not in states:
            print(f"Hiba: Az átmenet forrásállapota ({src}) nem érvényes.", file=sys.stderr)
            sys.exit(1)
        if dest not in states:
            print(f"Hiba: Az átmenet célállapota ({dest}) nem érvényes.", file=sys.stderr)
            sys.exit(1)
        if symbol not in alphabet:
            print(f"Hiba: Az átmenet szimbóluma ({symbol}) nincs az ábécében.", file=sys.stderr)
            sys.exit(1)
            
        key = (src, symbol)
        if key not in nfa_transitions:
            nfa_transitions[key] = set()
        nfa_transitions[key].add(dest)

    # Ha nincs megadva a --det kapcsoló, de a feladat kéri
    if not args.det:
        print("Figyelem: A --det kapcsoló nem lett megadva, de a program folytatja a feldolgozást.")

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
            
            # Ahol nincs átmenet, ott nem kerül az él felsorolásra
            if target_subset:
                t_frozenset = frozenset(target_subset)
                if t_frozenset not in state_map:
                    new_name = f"s{len(state_map)}"
                    state_map[t_frozenset] = new_name
                    discovered_subsets.append(t_frozenset)
                target_name = state_map[t_frozenset]
                dfa_transitions.append((current_name, symbol, target_name))

    # Állapotok és végállapotok numerikus sorrendbe rendezése
    dfa_states_sorted = sorted([state_map[s] for s in discovered_subsets], key=lambda x: int(x[1:]))
    
    dfa_final_states = []
    for subset in discovered_subsets:
        if any(s in final_states for s in subset):
            dfa_final_states.append(state_map[subset])
    dfa_final_states_sorted = sorted(list(set(dfa_final_states)), key=lambda x: int(x[1:]))

    # Átmenetek rendezése: előbb csomópont szerint, majd él címkéje szerint, majd célállomás szerint
    def transition_sort_key(t):
        src, symbol, dest = t
        return (int(src[1:]), symbol, int(dest[1:]))

    dfa_transitions_sorted = sorted(dfa_transitions, key=transition_sort_key)

    # Kiírás a kimeneti fájlba
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(" ".join(dfa_states_sorted) + "\n")
            f.write(" ".join(alphabet) + "\n")
            f.write(state_map[init_subset] + "\n")
            f.write(" ".join(dfa_final_states_sorted) + "\n")
            for src, symbol, dest in dfa_transitions_sorted:
                f.write(f"{src} {symbol} {dest}\n")
    except IOError:
        print(f"Hiba: Nem sikerült írni a kimeneti fájlba: {args.output}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()