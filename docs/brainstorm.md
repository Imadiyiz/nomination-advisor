### File for me to brainstorm ideas and let them out of my head

19/08/26

Currently working on the heuristics system within the monte carlo simulation, I want the bot to be able know the EV for each move and how it affects their final score. I am torn between making the bot work with its parameters or to simply just follow the monte carlo simulation EV. I could do both and see which one exceeds the baseline model. In the baseline model it is completely random after playing the perspective move. I will need to fix the baseline model as things would have changed since I changed cards from tuples to int.

21/08/26

P calculation

Goal: Ensure strong card d

Want strong cards to be above hand size

SC = Strong Cards 
TC = Total Cards = 52
PC = Played Cards 
HS = Hand Size 

SC = X

FORMULA
PC(X/TC) > HS

X / TC > HS/PC

X > (TC*HS)/PC

# bug fixing
x > (52 * 8) / 48

X > (52 * 6)/18
X > 17.3

Need a function which will try its best to make SCs slightly above handsize
increase SC by 1 by decreasing threshold for trump cards
increase SC by 3 by decreasing threshold for high cards (be careful that high card threshold is never below trump)

Default is 18 strong cards as this is the lowest int value that is that satisfies the formula

# heuristics class
V1 HeuristicClass

parameters = {
    "aggression": 0.45, # How often they are to bid higher than their random expected value
    "belief_in_opponents": 0.90, # how likely they are to believe the players who
    bid before them are successful
    "adaptability": 0.75, # How often the parameters change based on new information,
    "risk_tolerance": 0.1 # Decides when to make risky plays, with limited information 
    ""
}

### Architecture thoughts

TO ESTIMATE NAIVE MOVE
ES = Expected Score

RANDOM MC ROADMAP

1. Bots bid based on strong cards in hand
2. Perform MC using each legal move in hand 
3. The simulator should let bots play random legal moves
5. Once MC is performed the move with the greatest ES should be chosen 

NAIVE MC ROADMAP

2. Bots bid based on strong cards in hand
3. Perform MC using each legal move in hand
4. The simulator should let bots play towards their bid
5. Once MC is performed the move with the greatest ES should be chosen 

CURRENT THOUGHTS;

Hand evaluator is just not fitting in with the current artchitecture, it just feels awkward all the time. I do not want bot to be tightly coupled with HandEvaluator. I wanted to calculate what every MC bot player should bid however, they will all need their own individual HE instance

I dont know how the calculate expected score truly works with math given to me by AI


Random thought, if theres a tiebreaker during the round instead of completely gaining an advantage with luck
why not let the winner of the coin toss, choose whether to go first or to decide trump, before viewing cards obviously
Just makes more sense than getting both via coin toss. Seems like too big of an advantage.

Currently refactoring some parts of gamestate so that it is immutable and does the job it was designed to do, although it has been a steep learning curve doing the testing, I wish I put more effort into doing it before as it exposed me to future headaches which I can now avoid. I truly understand the code better and my diagnostic skills have improved tremendously through this project.

16/09/26

Currently refactoring game manager to incorporate game_state correctly, bumped into lots of errors and bugs

21/09/26

Refactoring Game_manager still, running into decisions that need to be made. I quickly justify a decision and then leave it, then I come back to it and wonder why I did it. I need to either write it down, or make it more explicit the reason as to why I am doing things.

 Still going through game_manager and I need to seperate core flow from assistant flow however, I have made progress. Very realistic for me to have a CPU playthrough as well as sim and Assistant. Assistant is obviously done, sim is also done, and single player would need slight configuration.

23/09/26

I have run into an issue with get_legal_moves, it works, however, it assumes that the player's cards are in the state.hands set, however, for opponent humans that is not the case. I will create a helper class which has the similar logic to the current get_legal_moves however, it must keep track of the suits played. Actually this is very similar to belief model. The issue of this is where is this going to be stored and how is it going to be keep in sync during the round and discarded at the end of the round.

I want to add logging to gamestate, it could incorporate every action performed since I have created the actions dataclass.


DECISION -> ACTION -> EXECUTION -> GAMESTATE

This is the architecture I am trying to implement, I have made progress today but have lost focus and become veryy frustrated witb the task of incorporating the three game modes. Now there are two game modes where the player will be able to view bots play the game. Now that I think of it, sim is diffeent to single player, and the diffeerence is the verbpse natire of the two. Sim would only output the winners and the scoes, not what p2 bid on round 2.

I am mid way through game_engine refactoring to round_manager. The actions are being abstracted into the actions file, wheer theu can be later seperated further by directory.

24/09/26

VERBOSE LIST

SIM NOTHING VERBOSE

ASSISTANT EVERYTHING VERBOSE AND SINGLE PLAYER EVERYTHING VERBOSE

They are not the same

FLOW

FB = Feedback
RT = Retrace (Must be able to go back and edit valid answers)
WLC = Welcome
E = Enter (So that player can acknowledge they are happy with their previous input)

ASSISTANT

WLC TO GAME 
HOW MANY PLAYERS SETUP (RT)
FB
LOOP PLAYER.LEN TIMES
    PLAYER X NAME (RT)
    FB
    PERSPECTIVE PLAYER? (RT)
    FB
E

STATEMENT ASSIGN CARDS
LOOP MAX_CARD TIMES
    ASSIGN CARD TO PERSPECTIVE HAND (RT)
    FB
E

RANDOM TRUMP ASSIGNED
E

STATEMENT BIDDING ROUND
LOOP PLAYER.LEN TIMES
    PLAYER BID AMOUNT? (RT)
    FB
E

STATEMENT PLAY ROUND

SHOW MENU ETC (SAME FLOW AS CURRENTLY IMPLEMENTED)

LOOP MAX_CARDS TIMES
    PERSPECTIVE SELECTS INDEX OF CARD THEY WANT TO PLAY
    FB
    PLAYER TYPES INITIALS OF CARD THEY WANT TO PLAY (RT)
    FB
    MENU/TRICK UPDATES
    E

ROUND SCORES DISPLAYED
TOTAL SCORES DISPLAYED
E

TRUMP DECIDED
FB
TRUMP SELECTION  # Should not be able to change trump once chosen
FB

LOOP BACK TO BIDDING ROUND UNTIL 6 ROUNDS HAVE COMPLETED

END CREDITS AND ASK TO SEND BACK TO MAIN MENU


**SINGLE_PLAYER**

WLC TO GAME 
HOW MANY PLAYERS SETUP (RT)
FB
LOOP PLAYER.LEN TIMES
    BOT X NAME (RT)
    FB
    BOT TYPE (RT)
    FB
    PERSPECTIVE PLAYER? (RT)
    FB
E

STATEMENT ASSIGN CARDS
ASSIGN RANDOM CARDS TO ALL PLAYERS
FB PERSPECTIVE HAND
E


RANDOM TRUMP ASSIGNED
E

STATEMENT BIDDING ROUND
LOOP PLAYER.LEN TIMES
    PLAYER BID AMOUNT? (RT)
    FB
    PERSPECTIVE BID? # No BACKTRACKING
    FB
E

STATEMENT PLAY ROUND

SHOW MENU ETC (SAME FLOW AS CURRENTLY IMPLEMENTED)

LOOP MAX_CARDS TIMES
    PERSPECTIVE SELECTS INDEX OF CARD THEY WANT TO PLAY
    FB
    BOT PLAYS THEIR CARD
    FB
    MENU/TRICK UPDATES
    E

ROUND SCORES DISPLAYED
TOTAL SCORES DISPLAYED
E

TRUMP DECIDER
FB
TRUMP SELECTION  # Should not be able to change trump once chosen
FB

LOOP BACK TO BIDDING ROUND UNTIL 6 ROUNDS HAVE COMPLETED

END CREDITS AND ASK TO SEND BACK TO MAIN MENU


**SIM**

ASSIGN BOTS AND THEIR TYPES FROM SCRIPT

ONLY OUTPUT SCORES



