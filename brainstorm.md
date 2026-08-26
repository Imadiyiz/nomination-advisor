### File for me to brainstorm ideas and let them out of my head

19/08/26

Currently working on the heuristics system within the monte carlo simulation, I want the bot to be able know the EV for each move and how it affects their final score. I am torn between making the bot work with its parameters or to simply just follow the monte carlo simulation EV. I could do both and see which one exceeds the baseline model. In the baseline model it is completely random after playing the perspective move. I will need to fix the baseline model as things would have changed since I changed cards from tuples to int.

21/08/26

P calculation

Goal: Ensure strong card d

Want strong cards to be above hand size

just trump 

13/52 = 1/4

3 players 6 cards

18/4 = 4.5 strong cards on average

trump and ace

3 players 6 cards

16/52 = 4/13 = 72/13 = 5.54

create the equation

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

I currently have a circular dependency within my architecture, in order to estimate a move, there must be initial bids to play for, however depending on how accurate I want these bids to be I will need to simulate games randomly to assess what the bot should expect to play given their hand strength.

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


Random thought, if theres a tiebreaker during the round instead of completely gaining an advantage with lucj
why not let the winner of the coin toss, choose whether to go first or to decide trump, before viewing cards obviously
Just makes more sense than getting both via coin toss. Seems like too big of an advantage.