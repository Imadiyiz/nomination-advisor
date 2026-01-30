# CLI Nomination Card Game

A command-line, text-based card game inspired by the game Nomination Whist.
Players take turns bidding, playing cards, and scoring points across multiple rounds.
The game runs entirely in the terminal and requires no graphical interface.

### Features

Text-based CLI gameplay

Multiple players (Human / Computer)

Round-based structure with bidding, playing, and scoring phases

Deterministic game flow suitable for testing

### Requirements

Python 3.10+ (recommended)

Compatible with Windows, macOS, and Linux

### Installation

Clone the repository:

git clone https://github.com/Imadiyiz/Nomination

### Create a virtual environment (Optional):

python -m venv venv

#### Activate it:

##### Windows:

venv\Scripts\activate

##### macOS / Linux:

source venv/bin/activate


### Install dependencies:

pip install -r requirements.txt

### Running the Game

##### Start the game from the project root:

python main.py

##### or, if required on your system:

python3 main.py

##### Follow the on-screen prompts to:

Enter player details

Place bids

Play cards

View round results and final scores

### Testing

This project uses pytest.

Run all tests from the project root:

pytest

### Notes

This game is designed for terminal play and does not include a GUI.

Input validation is handled at runtime via CLI prompts.

The codebase is structured to support future extensions (AI players, rule variants).

### License

This project is provided for educational purposes.
