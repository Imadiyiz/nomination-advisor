# Decisions

Here I can explain my decisions 

Removed Table as it is a second source of truth

Removed Card as there was too much redundancy with gamestate's tuple cardInts

REmoved playerstate manager as the players are no longer the source of truth
They do not need to be rotated as the gamestate will do this

removed score_hand function from game_manager as it was redundant given that game_state handles scoring

Removed materialised player card