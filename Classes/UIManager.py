# Contents of the UIManager python file

class UIManager:
    """
    Manages UI elements containing CLI and future GUI outputs
    """

    def get_player_input(self, prompt: str) -> str:
        return input(prompt)
    
    def display_message(self, message:str):
        print(message)