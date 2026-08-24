### Organising my thoughts = Seperating immediate coding concerns and future concerns


### Immediate issues

- [ ] Tie-breaking resolves to last match in dict iteration order in both estimator functions.

### Next Step

I want to make the trick evaluation in EOM by making the articifical players in a simulation play towards their bid. They should be aggressive when they can win tricks and passive when they want to lose tricks. I have taken this a step further and tried to make the AI even smarter by having adjustable parameters. Essentially I am pivoting away from the imperfect information agent assistant and moving more towards having a strong AI that will help the player in real time.

Progress update: I can use the determine baseline bid using strong cards estimation, to generate bids to play towards in the calculated simulator rollout

- [ ] Added Heuristics when choosing card for AI during rollout (In progress)

I need to simulate the rest of the round/game after selecting a move to observe whether it is the best move for the situation, playing a card that makes you win another trick after achieving your bid is not ideal.

- [ ] Extended the simulation of the estimate_optimal_move to include the following tricks/rounds

### Future Steps

I would like to implement the move evaluation and bidding evaluation into the CLI game. This will hopefully give the perspective player an edge during the game. 

- [ ] Integrated the bidding evaluator into the CLI game
- [ ] Integrated the move evaluator into the CLI game

I want the bid evaluator to be aware of the global score in order to cut a deficit between perspective and the points leader in order to minimise the deficit or maxmimise the lead. Must also remember that bid evaulator must omit the banned bid.

- [ ] Inegrated global score awareness within the the bid evaluator

GameManager is working as a Super class as it is performing too much within itself. It has so much responsibility that I haven;t refactored as the code works. Unfortunately, making changes are quite expensive timewise and mentally.

- [ ] Refactored the GameManager class in order to seperate logic and make the class's methods have a single purpose.

I thought about changing the way cards are calculated. Currently they are assigned values via a map to value based on their initials, whereas they could simply be a number, which could be divided into suits depending on whether they mod to 0 via a number mapped to a suit. e.g 40 could be 10S and 44 could be JS. However, upon my research performing mod operations isn't constant time complexity therefore, I do not think it is worth the refactor. I will need to test the time taken by the code in order to determine it.

Additionslly I need to spend the time creating tests for my classes as they are not robust. It would have been nice to be writing tests and program simultaneuously however, this can't always be done. One class I need to focus on the most is the gamestate class as it is the backbone of my Monte Carlo simulation.

[ ] Created unit tests for GameState class

move = random.choice(tuple(legal_moves)) # change this 
LN 29 in Rollout simulator - Could potentially make it smarter using desired_move() function to use gamestate to work out whether its in the best interest to the player to win the hand

I have done some research on Game Theory and have come across terms such as Nash Equillibrium (No regrettable moves), backwards induction (deducing the optimal move by backtracking from the outcome) and subgame perfection in imperfect information games. Currently I am running a PIMC (Perfect Information Monte Carlo) simulation. The issues with this strategy is that it is non-local, therefore it does not account for the fact that opponents choicces are also information and may forecast what they are due to play in the future. Additionally Strategy fusion is an issue, as PIMC assumes that in each sampled world you'll see the outcome before needing to act again but this is not the case, as the information will not be present in a real game until the cards are played. Overreates plays which only work when you 'peek'.

### Key points

Continue to update this file to reduce mental workload - Programming is difficult with a large mental workload, more planning and forward thinking can reduce this, making the process more enjoyable.

Explain why decisions were made or not made as this will improve your decision making skills in the future.

When will you know that the evaluator actually gives you an edge and isn't just luck? How do you come up with concrete evidence that the evaluator gives humans on average a 15% edge compared to humans without the evaluator?

A: I will do my own personal testing, to see if I can beat my friends over the span of maybe 10 games. Despite the small sample size I will know whether my actual decision making and the evaluator's decision making is different and whether the evaluator's option provides a winning outcome. As in I will be to get a sense of whether the evaluator's points are sane or whether they are random or follow a certain pattern. It will also be interesting to see if my friends have a different approach when playing a robot as I have previously played over 200 games with them.
For a more mathematical approach I could perform an experiment where I perform n_rollouts for each unqiue possible hand, and determine whether there are any hidden patterns by plotting the distributions in an excel speadsheet or matplot on python.


CHANGE THOUGHT PROCESS

CARD     WIN TRICK    MAKE BID    FINAL SCORE
──────────────────────────────────────────────
A♠          92%          18%          4.2
K♦          61%          54%         12.8
7♣          23%          71%         15.4
4♥          11%          63%         13.1

This is more insightful compared to simulating to the end of the trick

A good developer knows how to stay in scope. I keep changing every 2-3 hours. At this project was a local multiplayer CLI Game, then it turned into an online multiplayer GUI game, then it turned back to a single-player IRL CLI game , then it became ta single-player IRL CLI game with extra information given to perspective using a Monte-Carlo Simulation for predicting bids and winning tricks, now it has turned to a similar game with a heuristic bots instead of playing random moves within the MC rollot. All these changes have been made over the course of 12 months and have all been justified, at least at the time of the decision, but now I want to make a conscious effort to stop changing things. I will finish the basic heuristic bot, and then branch the project into two.

First there will be the original CLI game with boosted information.
Then I will make a second version where a single player can play against a variety of computer bots.

### Quality of life changes to make to the Game CLI

Formatting in general
Some duplicate messages
Make the player to play explicit
Make it clear the cards should be redealt
No idea what the total score is when bidding or playing the game
Should be clear in the bidding phase
Unplayable cards should be alerted, potentially red in color

Round order is not clear as round score changes based on score not order
A pointer icon on top of the player playing would solve this

Must indicate that the cards should be redealt for x amount of cards before the winner of the previous round is able to decide the new trump

Need to clear screen before playing the game

Make it clear who determines Trump for next round when there is a draw, should be ranndom. Could simulate automatically on the computer, as a card does not have to be drawn.

Need to clarify with Jay about the rule of cutting trump, is it possible to deal that card for the subsequent round or do we omit it. Irl I believe we redeal it but in the game I assumed you removed it from the deck.

Could make the back system work by each move being added to the stack and then when that sequence has finshed just reset the stack. After each step in the step the previous step can be saved within the stack, therefore if the user goes back then the most recent action can be removed from the stack and the gamestate that was previously on the stack will be used.

### Known issues

The sampling in belief model is not fairly distributed as first players to sample have a larger pool of cards to sample from, across multiple rollouts this makes the last player to sample from the deck of cards less liikely to obtain certain cards that the previous players are forced to take

Formatting this needs work choose cards [1-1]
Rule for following suits needs to be adhered