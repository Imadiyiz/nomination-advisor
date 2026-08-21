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