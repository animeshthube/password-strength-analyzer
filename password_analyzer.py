"""
Password Strength Analyzer
============================
A small, dependency-free tool that scores a password's strength based
on length, character variety, and common weak patterns, then returns
a Weak / Moderate / Strong rating plus actionable feedback.

Usage (CLI):
    python password_analyzer.py                  # interactive prompt
    python password_analyzer.py --password "abc"  # check one password directly
    python password_analyzer.py --demo            # run the built-in example set

Usage (as a library):
    from password_analyzer import analyze_password
    result = analyze_password("P@ssw0rd2026!")
    print(result["strength"], result["score"])
"""

import argparse
import getpass
import os
import re
import string

# ---------------------------------------------------------------------------
# Step 1: Rules / individual checks
# ---------------------------------------------------------------------------

MIN_LENGTH = 8
GOOD_LENGTH = 12  # length that earns a bonus point

SPECIAL_CHARS = string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~


def check_length(password: str) -> dict:
    """Checks password length against minimum and 'good' thresholds."""
    length = len(password)
    return {
        "length": length,
        "meets_minimum": length >= MIN_LENGTH,
        "meets_good_length": length >= GOOD_LENGTH,
    }


def check_character_types(password: str) -> dict:
    """Checks which character types are present in the password."""
    return {
        "has_upper": any(c.isupper() for c in password),
        "has_lower": any(c.islower() for c in password),
        "has_digit": any(c.isdigit() for c in password),
        "has_special": any(c in SPECIAL_CHARS for c in password),
    }


def check_common_patterns(password: str) -> dict:
    """Flags common weak patterns: sequential digits/letters, repeated
    characters, and keyboard-walk patterns."""
    lowered = password.lower()

    sequential_digits = any(
        seq in lowered for seq in ["0123", "1234", "2345", "3456", "4567",
                                     "5678", "6789", "9876", "8765", "7654",
                                     "6543", "5432", "4321", "3210"]
    )
    sequential_letters = any(
        seq in lowered for seq in ["abcd", "bcde", "cdef", "qwer", "asdf",
                                     "zxcv"]
    )
    repeated_chars = bool(re.search(r"(.)\1{2,}", password))  # e.g. "aaa", "111"
    keyboard_walk = any(
        walk in lowered for walk in ["qwerty", "asdfgh", "zxcvbn", "qazwsx"]
    )

    return {
        "sequential_digits": sequential_digits,
        "sequential_letters": sequential_letters,
        "repeated_chars": repeated_chars,
        "keyboard_walk": keyboard_walk,
    }


def check_common_password(password: str, common_list_path: str = None) -> bool:
    """Checks the password (case-insensitive) against a list of known
    common/breached passwords. Returns True if it's a common password."""
    if common_list_path is None:
        common_list_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "common_passwords.txt"
        )
    try:
        with open(common_list_path, "r") as f:
            common_passwords = {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        common_passwords = set()

    return password.lower() in common_passwords


# ---------------------------------------------------------------------------
# Step 2: Scoring
# ---------------------------------------------------------------------------

def score_password(password: str) -> dict:
    """Combines all checks into a single numeric score (0-8) and returns
    the full breakdown used to compute it."""
    length_info = check_length(password)
    types_info = check_character_types(password)
    pattern_info = check_common_patterns(password)
    is_common = check_common_password(password)

    score = 0
    if length_info["meets_minimum"]:
        score += 1
    if length_info["meets_good_length"]:
        score += 1
    if types_info["has_upper"]:
        score += 1
    if types_info["has_lower"]:
        score += 1
    if types_info["has_digit"]:
        score += 1
    if types_info["has_special"]:
        score += 1

    # bonus point for having 3+ character types AND meeting min length
    type_count = sum([types_info["has_upper"], types_info["has_lower"],
                       types_info["has_digit"], types_info["has_special"]])
    if type_count >= 3 and length_info["meets_minimum"]:
        score += 1

    # penalties
    if pattern_info["sequential_digits"] or pattern_info["sequential_letters"]:
        score -= 1
    if pattern_info["repeated_chars"]:
        score -= 1
    if pattern_info["keyboard_walk"]:
        score -= 1
    if is_common:
        score = 0  # a known common/breached password is always Weak, full stop

    score = max(0, min(score, 8))

    return {
        "score": score,
        "max_score": 8,
        "length_info": length_info,
        "types_info": types_info,
        "pattern_info": pattern_info,
        "is_common": is_common,
    }


def classify_strength(score: int, max_score: int = 8) -> str:
    """Maps a numeric score to Weak / Moderate / Strong."""
    pct = score / max_score
    if pct < 0.4:
        return "Weak"
    elif pct < 0.75:
        return "Moderate"
    else:
        return "Strong"


# ---------------------------------------------------------------------------
# Step 3: Feedback
# ---------------------------------------------------------------------------

def get_feedback(password: str, breakdown: dict = None) -> list:
    """Generates a list of actionable suggestions for improving the
    password. Accepts a pre-computed breakdown (from score_password) to
    avoid re-running the checks, or computes it if not provided."""
    if breakdown is None:
        breakdown = score_password(password)

    suggestions = []
    length_info = breakdown["length_info"]
    types_info = breakdown["types_info"]
    pattern_info = breakdown["pattern_info"]

    if breakdown["is_common"]:
        suggestions.append("This password appears in common breach lists — avoid it entirely.")
        return suggestions  # no point suggesting tweaks to a known-bad password

    if not length_info["meets_minimum"]:
        suggestions.append(f"Make it at least {MIN_LENGTH} characters long.")
    elif not length_info["meets_good_length"]:
        suggestions.append(f"Consider {GOOD_LENGTH}+ characters for stronger protection.")

    if not types_info["has_upper"]:
        suggestions.append("Add at least one uppercase letter (A-Z).")
    if not types_info["has_lower"]:
        suggestions.append("Add at least one lowercase letter (a-z).")
    if not types_info["has_digit"]:
        suggestions.append("Add at least one number (0-9).")
    if not types_info["has_special"]:
        suggestions.append("Add at least one special character (e.g. ! @ # $ %).")

    if pattern_info["sequential_digits"] or pattern_info["sequential_letters"]:
        suggestions.append("Avoid sequential patterns like '1234' or 'abcd'.")
    if pattern_info["repeated_chars"]:
        suggestions.append("Avoid repeating the same character 3+ times in a row.")
    if pattern_info["keyboard_walk"]:
        suggestions.append("Avoid keyboard-walk patterns like 'qwerty' or 'asdfgh'.")

    if not suggestions:
        suggestions.append("Looks good — no major weaknesses detected.")

    return suggestions


# ---------------------------------------------------------------------------
# Public API: analyze_password() ties everything together
# ---------------------------------------------------------------------------

def analyze_password(password: str) -> dict:
    """Runs the full analysis pipeline and returns a single result dict
    with score, strength rating, breakdown, and feedback."""
    breakdown = score_password(password)
    strength = classify_strength(breakdown["score"], breakdown["max_score"])
    feedback = get_feedback(password, breakdown)

    return {
        "password_length": len(password),
        "score": breakdown["score"],
        "max_score": breakdown["max_score"],
        "strength": strength,
        "breakdown": breakdown,
        "feedback": feedback,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

STRENGTH_COLORS = {
    "Weak": "\033[91m",      # red
    "Moderate": "\033[93m",  # yellow
    "Strong": "\033[92m",    # green
}
RESET_COLOR = "\033[0m"


def print_result(password: str, result: dict, mask: bool = True):
    shown = ("*" * len(password)) if mask else password
    color = STRENGTH_COLORS.get(result["strength"], "")
    print(f"\nPassword: {shown}")
    print(f"Score:    {result['score']} / {result['max_score']}")
    print(f"Strength: {color}{result['strength']}{RESET_COLOR}")
    print("Feedback:")
    for tip in result["feedback"]:
        print(f"  - {tip}")


def run_demo():
    examples = ["12345678", "Password1", "P@ssw0rd2026!"]
    print("=== Password Strength Analyzer: Demo ===")
    for pw in examples:
        result = analyze_password(pw)
        print_result(pw, result, mask=False)
    print()


def main():
    parser = argparse.ArgumentParser(description="Password Strength Analyzer")
    parser.add_argument("--password", "-p", help="Password to check (will be shown in terminal)")
    parser.add_argument("--demo", action="store_true", help="Run the built-in example set")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if args.password:
        result = analyze_password(args.password)
        print_result(args.password, result, mask=False)
        return

    # interactive mode — hide input using getpass
    try:
        pw = getpass.getpass("Enter a password to check (input hidden): ")
    except Exception:
        pw = input("Enter a password to check: ")
    result = analyze_password(pw)
    print_result(pw, result, mask=True)


if __name__ == "__main__":
    main()
