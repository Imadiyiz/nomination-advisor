import time

from hand_evaluator import HandEvaluator
from main_mc import 

# Start time

strt_time = time.perf_counter()

results = HandEvaluator().estimate_optimal_move()

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