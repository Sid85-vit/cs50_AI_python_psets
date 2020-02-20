import tictactoe as ttt

start = ttt.initial_state()
print(f"start player is: {ttt.player(start)}")
print(f"possible positions: {ttt.actions(start)}")