from main_mc import estimate_optimal_move, my_player, root_state

move_estimates = {}
move_estimates[my_player] = estimate_optimal_move(
    root_state, N_rollouts=100, perspective=my_player)

print(f"Move estimation for {my_player}:")

for i, v in move_estimates.items():  # noqa: PERF102

    print(f"{my_player}'s hand ", root_state.hands[my_player])
    print("Win Percentage per Card", list(v["win_percentages"]))
    print("Highest Percentage Card", max(v["win_percentages"]), '\n')
    print("Optimal Card", v["optimal_move"])
    print("Highest Card Probability", v["optimal_move_probability"])
    print("Least Optimal Card", v["least_optimal_move"])
    print("Lowest Card Probability", v["lowest_move_probability"])
