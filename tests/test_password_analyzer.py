"""
Unit tests for password_analyzer.py

Run with:
    python -m pytest tests/
or:
    python -m unittest discover tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from password_analyzer import (
    check_length,
    check_character_types,
    check_common_patterns,
    check_common_password,
    score_password,
    classify_strength,
    get_feedback,
    analyze_password,
    MIN_LENGTH,
    GOOD_LENGTH,
)


class TestLengthCheck(unittest.TestCase):
    def test_short_password_fails_minimum(self):
        result = check_length("abc123")
        self.assertFalse(result["meets_minimum"])

    def test_exact_minimum_length_passes(self):
        result = check_length("a" * MIN_LENGTH)
        self.assertTrue(result["meets_minimum"])

    def test_good_length_bonus(self):
        result = check_length("a" * GOOD_LENGTH)
        self.assertTrue(result["meets_good_length"])


class TestCharacterTypes(unittest.TestCase):
    def test_detects_all_types(self):
        result = check_character_types("Ab1!")
        self.assertTrue(result["has_upper"])
        self.assertTrue(result["has_lower"])
        self.assertTrue(result["has_digit"])
        self.assertTrue(result["has_special"])

    def test_detects_missing_types(self):
        result = check_character_types("abcdefgh")
        self.assertFalse(result["has_upper"])
        self.assertFalse(result["has_digit"])
        self.assertFalse(result["has_special"])


class TestCommonPatterns(unittest.TestCase):
    def test_sequential_digits_detected(self):
        result = check_common_patterns("abcd1234xyz")
        self.assertTrue(result["sequential_digits"])

    def test_repeated_chars_detected(self):
        result = check_common_patterns("aaa12345")
        self.assertTrue(result["repeated_chars"])

    def test_keyboard_walk_detected(self):
        result = check_common_patterns("qwerty123")
        self.assertTrue(result["keyboard_walk"])

    def test_clean_password_no_false_positives(self):
        result = check_common_patterns("Xk9#mQ2p")
        self.assertFalse(result["sequential_digits"])
        self.assertFalse(result["repeated_chars"])
        self.assertFalse(result["keyboard_walk"])


class TestCommonPasswordList(unittest.TestCase):
    def test_known_common_password_flagged(self):
        self.assertTrue(check_common_password("password"))
        self.assertTrue(check_common_password("123456"))

    def test_case_insensitive_match(self):
        self.assertTrue(check_common_password("PASSWORD"))

    def test_uncommon_password_not_flagged(self):
        self.assertFalse(check_common_password("Xk9#mQ2pRt7!"))


class TestScoringAndClassification(unittest.TestCase):
    def test_classify_boundaries(self):
        self.assertEqual(classify_strength(0, 8), "Weak")
        self.assertEqual(classify_strength(3, 8), "Weak")
        self.assertEqual(classify_strength(5, 8), "Moderate")
        self.assertEqual(classify_strength(8, 8), "Strong")

    def test_common_password_forced_to_zero_score(self):
        result = score_password("password1")
        self.assertEqual(result["score"], 0)
        self.assertTrue(result["is_common"])


class TestPlanExamplePasswords(unittest.TestCase):
    """The three example passwords called out in the project plan."""

    def test_all_numeric_short_password_is_weak(self):
        result = analyze_password("12345678")
        self.assertEqual(result["strength"], "Weak")

    def test_common_capitalized_password_is_weak(self):
        # "Password1" looks varied but is a well-known common password.
        result = analyze_password("Password1")
        self.assertEqual(result["strength"], "Weak")

    def test_complex_password_is_strong(self):
        result = analyze_password("P@ssw0rd2026!")
        self.assertEqual(result["strength"], "Strong")


class TestFeedback(unittest.TestCase):
    def test_feedback_for_weak_password_mentions_length(self):
        feedback = get_feedback("abc")
        self.assertTrue(any("characters long" in tip for tip in feedback))

    def test_feedback_for_common_password_is_single_warning(self):
        feedback = get_feedback("123456")
        self.assertEqual(len(feedback), 1)
        self.assertIn("breach", feedback[0])

    def test_feedback_for_strong_password_is_positive(self):
        feedback = get_feedback("P@ssw0rd2026!")
        self.assertTrue(any("no major weaknesses" in tip for tip in feedback))


if __name__ == "__main__":
    unittest.main()
