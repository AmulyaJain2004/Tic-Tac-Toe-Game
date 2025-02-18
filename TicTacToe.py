import tkinter as tk
from tkinter import messagebox
import csv
import pandas as pd
import matplotlib.pyplot as plt


class TicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe Menu")
        self.window['bg'] = "yellow"

        self.label = tk.Label(self.window, text="Choose Game Mode", font=('Arial', 20))
        self.label.pack(pady=20)

        self.single_player_button = tk.Button(self.window, text="Single Player Mode", font=('Arial', 16),
                                              command=self.single_player_mode)
        self.single_player_button.pack(pady=10)

        self.multiplayer_button = tk.Button(self.window, text="Multiplayer Mode", font=('Arial', 16),
                                            command=self.multiplayer_mode)
        self.multiplayer_button.pack(pady=10)

        self.scoreboard_button = tk.Button(self.window, text="Scoreboard", font=('Arial', 16),
                                           command=self.show_scoreboard)
        self.scoreboard_button.pack(pady=10)

        self.analysis_button = tk.Button(self.window, text="Analysis", font=('Arial', 16),
                                         command=self.analyze_data)
        self.analysis_button.pack(pady=10)

        self.board = None
        self.buttons = []
        self.game_over = False
        self.mode = None
        self.turn = None

    def single_player_mode(self):
        self.mode = 1
        self.turn = 1
        self.window.destroy()
        self.main()

    def multiplayer_mode(self):
        self.mode = 2
        self.turn = 1
        self.window.destroy()
        self.main()

    def main(self):
        # Create a new game instance
        self.board = TicTacToeBoard(self.mode)
        self.board.create_board()

    def analyze_data(self):
        analyzer = DataAnalyzer()
        analyzer.analyze_and_plot()

    def show_scoreboard(self):
        scoreboard = Scoreboard()
        scoreboard.display()

    def run(self):
        self.window.mainloop()


class TicTacToeBoard:
    def __init__(self, mode):
        self.board = [0] * 9
        self.buttons = []
        self.mode = mode
        self.game_over = False
        self.turn = 1 if mode == 2 else 1

        self.window = tk.Tk()
        self.window.title("Tic Tac Toe")

    def create_board(self):
        for i in range(9):
            row = i // 3
            col = i % 3
            button = tk.Button(self.window, text="", font=('Arial', 20), width=5, height=2,
                               command=lambda idx=i: self.button_click(idx))
            button.grid(row=row, column=col, padx=5, pady=5)
            self.buttons.append(button)

        self.window.mainloop()

    def button_click(self, index):
        if not self.game_over:
            if self.board[index] == 0:
                if self.mode == 1:
                    self.user_turn(index)
                    self.comp_turn()
                else:
                    self.user_turn(index) if self.turn == 1 else self.user2_turn(index)
                if self.analyze_board() != 0:
                    self.game_over = True
                elif self.mode == 2:
                    self.toggle_turn()

    def toggle_turn(self):
        self.turn = 2 if self.turn == 1 else 1

    def user_turn(self, pos):
        if self.board[pos] != 0:
            print("Wrong Move")
            return False
        self.board[pos] = -1
        self.update_board()

    def user2_turn(self, pos):
        if self.board[pos] != 0:
            print("Wrong Move")
            return False
        self.board[pos] = 1
        self.update_board()

    def comp_turn(self):
        pos = -1
        value = -2
        for i in range(0, 9):
            if self.board[i] == 0:
                self.board[i] = 1
                score = -self.min_max(-1)
                self.board[i] = 0
                if score > value:
                    value = score
                    pos = i
        self.board[pos] = 1
        self.update_board()

    def min_max(self, player):
        x = self.analyze_board()
        if x != 0:
            return x * player
        pos = -1
        value = -2
        for i in range(0, 9):
            if self.board[i] == 0:
                self.board[i] = player
                score = -self.min_max(-player)
                self.board[i] = 0
                if score > value:
                    value = score
                    pos = i
        if pos == -1:
            return 0
        return value

    def analyze_board(self):
        cb = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
        for i in range(0, 8):
            if self.board[cb[i][0]] != 0 and self.board[cb[i][0]] == self.board[cb[i][1]] == self.board[cb[i][2]]:
                return self.board[cb[i][0]]
        return 0

    def update_board(self):
        for i in range(9):
            if self.board[i] == -1:
                self.buttons[i].config(text="X", state="disabled", bg="lightblue", fg="black")
            elif self.board[i] == 1:
                self.buttons[i].config(text="O", state="disabled", bg="lightgreen", fg="black")

        x = self.analyze_board()
        if x == 0:
            print("Draw!")
        elif x == -1:
            print("Player X Wins!!! O Looses!")
        elif x == 1:
            print("Player O Wins!!! X Looses!")

        if x != 0:
            messagebox.showinfo("Game Over", "Player X Wins!!! O Looses!" if x == -1 else
                                                  "Player O Wins!!! X Looses!" if x == 1 else
                                                  "It's a Draw!")

            self.update_scoreboard("Player X" if x == -1 else "Player O" if x == 1 else "Draw")

    def update_scoreboard(self, winner):
        with open('scoreboard.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if winner == "Draw":
                writer.writerow(["Game is draw"])
            else:
                loser = "Player O" if winner == "Player X" else "Player X"
                writer.writerow([f"{winner} won and {loser} lost"])


class DataAnalyzer:
    def analyze_and_plot(self):
        df = pd.read_csv('scoreboard.csv', header=None, names=['Outcome'])
        df[['Winner', 'Loser']] = df['Outcome'].str.split(' won and ', expand=True)
        winner_counts = df['Winner'].value_counts()
        total_games = winner_counts.sum()
        win_percentages = (winner_counts / total_games) * 100

        plt.figure(figsize=(8, 8))
        plt.pie(win_percentages, labels=win_percentages.index, autopct='%1.1f%%', startangle=140)
        plt.title('Win Percentage')
        plt.axis('equal')
        plt.show()


class Scoreboard:
    def display(self):
        with open('scoreboard.csv', mode='r') as file:
            scoreboard_data = file.readlines()

        scoreboard_window = tk.Tk()
        scoreboard_window.title("Scoreboard")

        label = tk.Label(scoreboard_window, text="Previous Outcomes", font=('Arial', 20))
        label.pack(pady=20)

        text_widget = tk.Text(scoreboard_window, width=40, height=10)
        text_widget.pack(padx=10, pady=10)

        for outcome in scoreboard_data:
            text_widget.insert(tk.END, outcome.strip() + '\n')

        text_widget.config(state=tk.DISABLED)

        scoreboard_window.mainloop()


if __name__ == "__main__":
    game = TicTacToe()
    game.run()
