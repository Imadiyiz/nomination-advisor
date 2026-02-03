from .StepManager import *


class PlayerSetupFlow:
    """
    Handles the flow of steps to configure player selections
    """
    def __init__(self):
        
        self.context = {
            "num_players": 0, 
            "player_names": []
            }
        
        self.stepManager = StepManager()
    
    def run(self):
        #step 1: number of players

        while True:
            print("ENTER THE FOLLOWING PLAYERS IN THE PLAYING ORDER")
            result = self.stepManager.run_step(NumPlayerStep())
            if result != 'BACK':
                self.context['num_players'] = result
                break

        #step 2: iterate players
        while len(self.context['player_names']) < self.context['num_players']:
            clear_screen(0)
            print(f"\nConfiguring player {len(self.context['player_names']) + 1}")

            # runs the player name step and returns a string
            name = self.stepManager.run_step(PlayerNameStep())

            # removes the player name input if back is selected
            if name == 'BACK':
                if self.context["player_names"]:
                    self.context["player_names"].pop()
                continue
            
            # runs the opponent boolean step and returns a boolean
            is_opponent_response = self.stepManager.run_step(OpponentBooleanStep())
            if is_opponent_response == "BACK":
                continue

            if is_opponent_response in ('y', ''):
                is_opponent = True
            else:
                is_opponent = False
                
            self.context["player_names"].append({
                "name": name, 
                "opponent": is_opponent
            })
            
        return self.context
    
    def remove_duplicates(self, input_players: list):

        # Initialise the name count dictionary to determine whether a player_name is a duplicate
        names_count = {}
        unique_player_names = []

        for player_name in input_players:
            
            #validation to avoid duplicate names
            if player_name not in names_count:
                names_count[player_name] = 0
            else:
                names_count[player_name] += 1
                player_name = f"{player_name}{names_count[player_name] + 1}"
            
            unique_player_names.append(player_name)

        return unique_player_names


         