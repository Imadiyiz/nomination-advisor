from main_mc import estimate_optimal_move, my_player, root_state
import time

# Start time

strt_time = time.perf_counter()

move_estimates = {}
move_estimates[my_player] = estimate_optimal_move(
    root_state, N_rollouts=100, perspective=my_player)


for i, v in move_estimates.items():  # noqa: PERF102

    print(f"{my_player}'s hand ", root_state.hands[my_player])
    print("Win Percentage per Card", list(v["win_percentages"]))
    print("Highest Percentage Card", max(v["win_percentages"]), '\n')
    print("Optimal Card", v["optimal_move"])
    print("Highest Card Probability", v["optimal_move_probability"])
    print("Least Optimal Card", v["least_optimal_move"])
    print("Lowest Card Probability", v["lowest_move_probability"])

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