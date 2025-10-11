from Level import Level

LEVELS = [
    Level(
        name="Level 1: Accept 101",
        type = "Starter",
        description="Build a Turing Machine that accepts the string 101.",
        alphabet=["0", "1", "_"],
        objective="Accept exactly the word 101 and reject all others.",
        correct_examples=["101"],
        wrong_examples=["0", "1", "10", "11", "100", "110", "111", "000", "001", "010", "1011", "1010", "0101", "1010101"]
    ),
    Level(
        name="Level 2: No 001",
        type = "Starter",
        description="Accept binary strings that do not contain the substring 001.",
        alphabet=["0", "1", "_"],
        objective="Reject any input containing '001'.",
        correct_examples=["0", "1", "00", "01", "10", "11", "000", "010", "100", "101", "110", "111"],
        wrong_examples=["001", "1001", "0001", "0010", "101001"]
    ),
    Level(
        name="Level 3: Count 1s",
        type = "Starter",
        description="Accept strings with exactly three 1s.",
        alphabet=["0", "1", "_"],
        objective="Accept if there are exactly three '1's in the input.",
        correct_examples=["111", "1011", "000110001", "100000000101", "110001", "010101", "0111", "111000"],
        wrong_examples=["", "0", "1", "11", "1111", "000", "1000", "0001", "1010", "1100", "0011", "0110"]
    ),
    Level(
        name="Level 4: Palindrome",
        type = "Starter",
        description="Accept binary palindromes.",
        alphabet=["0", "1", "_"],
        objective="Accept if the input reads the same forwards and backwards.",
        correct_examples=["", "0", "1", "00", "11", "101", "010", "111", "000", "1001", "0110"],
        wrong_examples=["01", "10", "001", "110", "100", "011", "1010", "1100"]
    ),
    Level(
        name="Level 5: Letters",
        type = "Starter",
        description="Accept strings that contain the letter A followed by B.",
        alphabet=["A", "B", "C", "_"],
        objective="Accept if 'A' appears before 'B' in the string.",
        correct_examples=["AB", "ACB", "AAB", "CBA", "AAACCCBBB"],
        wrong_examples=["BA", "BCA", "CBA", "BBB", "CCC", "C"]
    ),
    Level(
        name="Level 6: Even 0s",
        type = "Starter",
        description="Accept binary strings with an even number of 0s.",
        alphabet=["0", "1", "_"],
        objective="Accept if the count of '0's is even, reject otherwise.",
        correct_examples=["1", "11", "111", "00", "11", "101", "1100", "1001", "0110"],
        wrong_examples=["0", "10", "01", "000", "100", "010", "001", "1110", "1010", "1101"]
    ),
]