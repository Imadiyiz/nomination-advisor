### Organising my thoughts = Seperating immediate coding concerns and future concerns


### Immediate issues

- [ ] Tie-breaking resolves to last match in dict iteration order in both estimator functions.

### Next Step

I want to make the trick evaluation in EOM by making the articifical players in a simulation play towards their bid. They should be aggressive when they can win tricks and passive when they want to lose tricks.

- [ ] Added Heuristics when choosing card for AI during rollout

I want to turn the main_mc.py script into a class to follow best principles and avoid repeating the parameters. This would be called HandEvaluator which would be initialised with a root_state, perspective and belief model. 

- [X] Successfully implemented the class HandEvaluator (Do First)

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


# Quality of life changes to make to the Game CLI

Formatting in general
Some duplicate messages
Make the player to play explicit
Make it clear the cards should be redealt
No idea what the total score is when bidding or playing the game
Should be clear in the bidding phase
Unplayable cards should be alerted, potentially red in color

Round order is not clear as round score changes based on score not order
A pointer icon on top of the player playing would solve this

Unable to put lowercase for initial of cards in the round gameplay screen for other player

Choose card should display [1] instead of [1-1] when selecting (Once len gets to 1 just show 1)

Must indicate that the cards should be redealt for x amount of cards before the winner of the previous round is able to decide the new trump