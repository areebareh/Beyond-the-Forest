import unittest
from unittest.mock import patch
import game_engine as ge

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        ge.reset_game()

    def test_set_player_name(self):
        ge.set_player_name("Areeba")
        self.assertEqual(ge.player_name, "Areeba")

    def test_get_status_initial(self):
        status = ge.get_status()
        self.assertEqual(status["location"], "Forest Entrance")
        self.assertEqual(status["health"], 100)
        self.assertEqual(status["inventory"], [])

    def test_move_valid(self):
        self.assertIn("Deep Forest", ge.move("north"))
        self.assertEqual(ge.current_location, "Deep Forest")

    def test_move_invalid(self):
        self.assertEqual(ge.move("west"), "You can't go that way.")
        self.assertEqual(ge.current_location, "Forest Entrance")

    def test_use_item_with_medkit(self):
        ge.inventory.append("Medkit")
        ge.player_health = 80
        result = ge.use_item()
        self.assertEqual(result, "You used a Medkit. Health restored by 20 points.")
        self.assertEqual(ge.player_health, 100)

    def test_use_item_without_medkit(self):
        result = ge.use_item()
        self.assertEqual(result, "You don't have a Medkit.")

    @patch("random.random", return_value=0.4)
    def test_encounter_monster_occurs(self, mock_random):
        ge.current_location = "Deep Forest"
        self.assertIn(ge.encounter_monster(), ge.monsters["Deep Forest"])

    @patch("random.random", return_value=0.9)
    def test_encounter_monster_none(self, mock_random):
        ge.current_location = "Deep Forest"
        self.assertIsNone(ge.encounter_monster())

    @patch("random.random", return_value=0.5)
    def test_fight_success(self, mock_random):
        ge.inventory.clear()
        msg = ge.fight("Goblin")
        self.assertIn("defeated", msg)
        self.assertIn("Medkit", ge.inventory)

    @patch("random.random", return_value=0.8)
    @patch("random.randint", return_value=20)
    def test_fight_failure(self, mock_randint, mock_random):
        ge.player_health = 100
        msg = ge.fight("Wolf")
        self.assertIn("lost 20 health", msg)
        self.assertEqual(ge.player_health, 80)

    def test_has_won_true(self):
        ge.current_location = "Riverbank"
        ge.inventory.append("Medkit")
        self.assertTrue(ge.has_won())

    def test_has_won_false(self):
        self.assertFalse(ge.has_won())

    def test_is_alive_true(self):
        ge.player_health = 50
        self.assertTrue(ge.is_alive())

    def test_is_alive_false(self):
        ge.player_health = 0
        self.assertFalse(ge.is_alive())

if __name__ == "__main__":
    unittest.main()
