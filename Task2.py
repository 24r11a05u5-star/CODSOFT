import math

# --- System Constants ---
VIRUS = 'V'     # Human Player
FIREWALL = 'F'  # AI Player
EMPTY = '0'     # Empty Server Node

class CyberTicTacToe:
    def __init__(self):
        # A 1D list representing our 3x3 server grid
        self.server_grid = [EMPTY for _ in range(9)]

    def render_system(self):
        print("\n--- SERVER CLUSTER STATUS ---")
        for row in [self.server_grid[i*3:(i+1)*3] for i in range(3)]:
            print(" | ".join(row))
        print("-----------------------------\n")

    def available_nodes(self):
        return [i for i, node in enumerate(self.server_grid) if node == EMPTY]

    def empty_nodes_exist(self):
        return EMPTY in self.server_grid

    def check_breach(self, player):
        # All possible winning lines in a 3x3 grid
        win_states = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Horizontal
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Vertical
            [0, 4, 8], [2, 4, 6]             # Diagonal
        ]
        for state in win_states:
            if all(self.server_grid[node] == player for node in state):
                return True
        return False

    def minimax_protocol(self, is_maximizing):
        # Terminal states (The base cases for our recursion)
        if self.check_breach(FIREWALL):
            return 1  # AI Wins
        elif self.check_breach(VIRUS):
            return -1 # Human Wins
        elif not self.empty_nodes_exist():
            return 0  # Draw

        if is_maximizing:
            best_score = -math.inf
            for node in self.available_nodes():
                self.server_grid[node] = FIREWALL
                score = self.minimax_protocol(False)
                self.server_grid[node] = EMPTY
                best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for node in self.available_nodes():
                self.server_grid[node] = VIRUS
                score = self.minimax_protocol(True)
                self.server_grid[node] = EMPTY
                best_score = min(score, best_score)
            return best_score

    def best_ai_move(self):
        best_score = -math.inf
        optimal_node = None
        
        for node in self.available_nodes():
            # Simulate the move
            self.server_grid[node] = FIREWALL
            # Calculate the score for this move
            score = self.minimax_protocol(False)
            # Undo the move
            self.server_grid[node] = EMPTY
            
            if score > best_score:
                best_score = score
                optimal_node = node
                
        return optimal_node

    def execute_breach(self):
        print("SYSTEM ONLINE. YOU ARE THE VIRUS (V). INFILTRATE THE SERVERS (0-8).")
        self.render_system()

        while self.empty_nodes_exist():
            # 1. Human Turn
            valid_move = False
            while not valid_move:
                try:
                    move = int(input("Target Server Node (0-8): "))
                    if move in self.available_nodes():
                        self.server_grid[move] = VIRUS
                        valid_move = True
                    else:
                        print("Node occupied or invalid. Try again.")
                except ValueError:
                    print("Invalid input. Use integers 0-8.")

            self.render_system()
            if self.check_breach(VIRUS):
                print("CRITICAL FAILURE: SYSTEM BREACHED. VIRUS WINS.")
                return
            if not self.empty_nodes_exist():
                break

            # 2. AI Turn
            print("FIREWALL ANALYZING THREATS...")
            ai_move = self.best_ai_move()
            self.server_grid[ai_move] = FIREWALL
            print(f"FIREWALL DEPLOYED AT NODE {ai_move}.")
            
            self.render_system()
            if self.check_breach(FIREWALL):
                print("THREAT NEUTRALIZED: FIREWALL WINS.")
                return

        print("STALEMATE: SYSTEM QUARANTINED. IT'S A TIE.")

if __name__ == '__main__':
    defense_system = CyberTicTacToe()
    defense_system.execute_breach()