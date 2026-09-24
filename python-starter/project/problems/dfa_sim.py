import sys
from typing import Dict, Tuple, Set
from project.problem import Problem


class DFA:
    def __init__(self, filename: str):
        self.states: Set[str] = set()
        self.alphabet: Set[str] = set()
        self.start_state: str = ""
        self.accept_states: Set[str] = set()
        self.transitions: Dict[Tuple[str, str], str] = {}
        
        self._load_from_file(filename)

    def _load_from_file(self, filename: str) -> None:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Hiba: A '{filename}' fájl nem található.", file=sys.stderr)
            sys.exit(1)

        if len(lines) < 4:
            print("Hiba: Érvénytelen bemeneti fájl formátum.", file=sys.stderr)
            sys.exit(1)

        self.states = set(lines[0].split())
        self.alphabet = set(lines[1].split())
        self.start_state = lines[2].strip()
        self.accept_states = set(lines[3].split())

        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                from_state, symbol, to_state = parts
                self.transitions[(from_state, symbol)] = to_state

    def accepts(self, word: str) -> bool:
        current_state = self.start_state
        
        for char in word:
            if (current_state, char) not in self.transitions:
                return False
            current_state = self.transitions[(current_state, char)]

        return current_state in self.accept_states


class DFASimulationProblem(Problem):
    def initialize_parser(self, parser):
        # Hozzáadjuk a feladatspecifikus --check kapcsolót
        parser.add_argument('--check', help='Vesszővel elválasztott szavak ellenőrzésre')

    def is_chosen_problem(self, args) -> bool:
        # Ha megadták a --check argumentumot, akkor ezt a feladatot futtatjuk
        return getattr(args, 'check', None) is not None

    def run(self, args):
        dfa = DFA(args.input)
        words = args.check.split(",")

        results = []
        for word in words:
            if dfa.accepts(word):
                results.append("IGEN")
            else:
                results.append("NEM")

        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                for res in results:
                    f.write(res + "\n")
        except IOError as e:
            print(f"Hiba a kimeneti fájl írásakor: {e}", file=sys.stderr)
            sys.exit(1)