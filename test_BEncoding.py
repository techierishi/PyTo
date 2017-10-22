from unittest import TestCase
from BEncoding import Bdecode, Bencode
import os

validBEncodings = {
    ### INTEGERS
    b"i24e": 24,
    b"i-24e": -24,
    ### STRINGS
    b"4:spam": b"spam",
    # Empty string
    b"0:": b"",
    ### LISTS
    b"l4:spam4:spami42ee": [b"spam", b"spam", 42],
    # Empty list
    b"le": [],
    # List of a dictionary and a list
    b"ll4:spam4:spami42eed3:cow3:moo4:spam4:eggsee": [[b"spam", b"spam", 42], {b"cow": b"moo", b"spam": b"eggs"}],
    ### DICTIONARIES
    b"d3:cow3:moo4:spam4:eggse": {b"cow": b"moo", b"spam": b"eggs"},
    # Dictionary of list and dictionary
    b"d4:spaml4:spam4:spami42ee4:spomd3:cow3:moo4:spam4:eggsee": {b"spam": [b"spam", b"spam", 42],
                                                                  b"spom": {b"cow": b"moo", b"spam": b"eggs"}},
    # Empty dictionary
    b"de": {},
}

class test_Bdecode(TestCase):
    def test_Bdecode_success(self):
        for (key, value) in validBEncodings.items():
            with self.subTest(case=key, expected=value, result=Bdecode(key)):
                self.assertEqual(Bdecode(key), value)

    def test_Bdecode_failure(self):
         failCases = [
            # Invalid string lengths
            b"4:spa",
            b"2:spa"
            b"-1:x",
            b"-4:spam",
            b"0-4:spam",
            b"0:e",
            # Dictionary key must be a string
            b"di42e4:spame",
            # Dictionary with no terminating "e"
            b"d4:spami42e4:spomi43e"
            # Invalid integers
            b"i2Fe",
            b"ie",
            b"i42",
            b"i--23e",
            b"i1+1e",
            b"i1,2e",
            b"i1.2e",
            b"i1.0e",
            b"i1,0e",
            # List with no terminating "e"
            b"li42ei43e"
         ]
         for testCase in failCases:
            with self.subTest(testCase=testCase):
                with self.assertRaises(ValueError, msg="case '{0}'".format(testCase)):
                    print(Bdecode(testCase))


class test_Bencode(TestCase):
    def test_Bencode_success(self):
        for (key, value) in validBEncodings.items():
            with self.subTest(case=value, expected=key, result=Bencode(value)):
                self.assertEqual(Bencode(value), key)

    def test_Bencode_failure(self):
         failCases = [
            # Number but not an integer
            1.0,
            # String instead of a bytestring
            "a",
            # Dictionary keys must be strings
            {1: b"a", 2: b"b"},
         ]
         for testCase in failCases:
            with self.subTest(testCase=testCase):
                with self.assertRaises(ValueError, msg="case '{0}'".format(testCase)):
                    print(Bencode(testCase))


class test_Torrent(TestCase):
    def test_torrent_idempotence(self):
        # Decode whole torrent files
        os.chdir("./data/torrent files/")
        for file in os.listdir():
            filename = os.fsdecode(file)
            with open(filename, "rb") as f:
                with self.subTest(filename=filename):
                    s = f.read()
                    self.assertEqual(s, Bencode(Bdecode(s)))