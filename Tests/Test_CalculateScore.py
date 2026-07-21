# Contents of the Test_CalculateScore.py file

from main_mc import calculate_score
import pytest
import random

class Test_Calculate_Score():
    
    def test(self):
        
        assert calculate_score(0, 0) == 10
        assert calculate_score(3, 3) == 13
        assert calculate_score(7, 7) == 17
        assert calculate_score(8, 8) == 36

        assert calculate_score(3, 4) == 3
        assert calculate_score(7, 8) == 7
        assert calculate_score(8, 7) == 8
           
    
