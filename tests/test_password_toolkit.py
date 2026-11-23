import string
import unittest

from password_toolkit import AMBIGUOUS, estimate_strength, generate


class PasswordToolkitTests(unittest.TestCase):
    def test_requested_length(self):
        self.assertEqual(len(generate(24)), 24)

    def test_every_enabled_class_is_represented(self):
        for _ in range(100):
            password = generate(20)
            self.assertTrue(any(c in string.ascii_lowercase for c in password))
            self.assertTrue(any(c in string.ascii_uppercase for c in password))
            self.assertTrue(any(c in string.digits for c in password))
            self.assertTrue(any(c in string.punctuation for c in password))

    def test_exclude_ambiguous_characters(self):
        password = generate(40, exclude_ambiguous=True)
        self.assertFalse(any(c in AMBIGUOUS for c in password))

    def test_respects_disabled_classes(self):
        password = generate(30, use_digits=False, use_symbols=False)
        self.assertTrue(all(c.isalpha() for c in password))

    def test_rejects_impossible_requests(self):
        with self.assertRaises(ValueError):
            generate(8, use_upper=False, use_lower=False, use_digits=False, use_symbols=False)
        with self.assertRaises(ValueError):
            generate(2)

    def test_strength_scale(self):
        self.assertEqual(estimate_strength("abc")[0], "weak")
        self.assertIn(estimate_strength("Tr0ub4dor&3xKq")[0], ("good", "strong"))

    def test_common_password_is_capped_as_weak(self):
        label, bits = estimate_strength("Password123")
        self.assertEqual(label, "weak")
        self.assertLessEqual(bits, 10)


if __name__ == "__main__":
    unittest.main()
