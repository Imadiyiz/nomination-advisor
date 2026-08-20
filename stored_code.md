### Weighted bid decision making

        # Plays postively if bot has less than 3 strong cards
        bid_to_confirm = (
            len(strong_cards) 
            if len(strong_cards) > 2 
            else random.choices(
                (0,1,2),
                weights=LOW_HAND_BID_WEIGHTS,
                k=1)
            [0]
         ) # more biased towards 0