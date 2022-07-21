# Unit tests for Game 1
# Backend

import unittest
import numpy as np
from app.workers.game1_worker import get_image, generate_plot, game1_worker
from app.workers.game3_worker import weighing_options, signal_model, get_image_json, get_bargraph_json, game3_worker
from app.workers.game5_worker import * 


class TestGame1Workers(unittest.TestCase):
    def test_function1(self):
        x = 0
        y = 0
        np.testing.assert_almost_equal(x,y)

