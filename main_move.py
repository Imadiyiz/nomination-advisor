import time

from main_mc import estimate_optimal_move, my_player, root_state

# Start time

strt_time = time.perf_counter()

results = estimate_optimal_move(
    root_state, N_rollouts=500, perspective=my_player)

win_percentage_list = list(results["win_percentages"])
maximum_win_card_percentage = max(
    win_percentage_list,
    key=lambda x:x[1]
    )


sorted_win_percentage_list = sorted(win_percentage_list,
                                    key=lambda x:x[1],
                                    reverse=True)

print(" ")
print(f"{my_player}'s hand ", root_state.hands[my_player])
print("Win Percentage per Card:\n\n", "".join(f"{r}\n " for r in sorted_win_percentage_list))
print("Highest Percentage Card", maximum_win_card_percentage, '\n')
print("Optimal Card", results["optimal_move"])
print("Highest Card Probability", results["optimal_move_probability"])
print("Least Optimal Card", results["least_optimal_move"])
print("Lowest Card Probability", results["lowest_move_probability"])

# End time
end_time = time.perf_counter()
print(f"Execution time: {end_time - strt_time:.2f} seconds")


# Mostly working now, just need some quality of life changes, the main bug was the logic
# I need to estabbllish that the assigned leader is the first player to play however, this should be derived not set manuyally
# e.g first player to play in trump tuple otherwise first player in player order
# Furthermore the core logic was wrong as you should only be able to simulate after what you have played,
# Not just randomly simulate what is going to happen as this is a not realistic. 
# The core principle of the game means you have information before you play unless you are first,
# However that already worked so I was getting stressed over fixing something that didn;t need fixing.