from Level import Level

LEVELS = [
    Level(
        name="How to Play",
        type = "Tutorial",
        description="Learn the core mechanics of building a Turing Machine.",
        detailedDescription="Build a Turing machine that accepts any binary words that arent empty.",
        alphabet=["0", "1", "_"],
        objective="Accept all binary words except the empty word.",
        mode="accept",
        correct_examples=["1", "0"],
        wrong_examples=[""]
    ),
    Level(
        name="How to Play 2: Transformations",
        type = "Tutorial",
        description="Learn the core mechanics of building a Turing Machine that transforms input.",
        detailedDescription="Build a Turing machine that transforms all binary elements to blank. So for example 101 becomes ___",
        alphabet=["0", "1", "_"],
        objective="Accept if the length of the input is even, reject otherwise.",
        mode="transform",
        transform_tests=[ {"input": "101", "output": ""}, {"input": "1", "output": ""}, {"input": "0", "output": ""}, {"input": "", "output": ""} ]
    ),
    Level(
        name="Level 1: Accept 101",
        type = "Starter",
        description="Build a Turing Machine that only accepts the string 101.",
        detailedDescription="Turing machine accepts string 101 while rejecting all others, for example: 0, 1, 10..etc",
        alphabet=["0", "1", "_"],
        objective="Accept exactly the word 101 and reject all others.",
        mode="accept",
        correct_examples=["101"],
        wrong_examples=["0", "1", "10", "11", "100", "110", "111", "000", "001", "010", "1011", "1010", "0101", "1010101"]
    ),
    Level(
        name="Level 2: No 001",
        type = "Starter",
        description="Accept binary strings that do not contain the substring 001.",
        detailedDescription="Turing machine accepts any binary string that does not contain the substring '001'. For example, it should accept '0', '1', '00', '01', '10', '11', '000', '010', etc., but reject '001', '1001', '0001', etc.",
        alphabet=["0", "1", "_"],
        objective="Reject any input containing '001'.",
        mode="accept",
        correct_examples=["0", "1", "00", "01", "10", "11", "000", "010", "100", "101", "110", "111"],
        wrong_examples=["001", "1001", "0001", "0010", "101001"]
    ),
    Level(
        name="Level 3: Count 1s",
        type = "Starter",
        description="Accept strings with exactly three 1s.",
        detailedDescription="Turing machine accepts strings with exactly three 1s while rejecting all others. For example, it should accept '111', '1011', '000110001', etc., but reject '', '0', '1', '11', '1111', etc.",
        alphabet=["0", "1", "_"],
        objective="Accept if there are exactly three '1's in the input.",
        mode="accept",
        correct_examples=["111", "1011", "000110001", "100000000101", "110001", "010101", "0111", "111000"],
        wrong_examples=["", "0", "1", "11", "1111", "000", "1000111", "0001", "1010", "1100", "0011", "0110"]
    ),
    Level(
        name="Level 4: Palindrome",
        type = "Starter",
        description="Accept binary palindromes.",
        detailedDescription="Turing machine accepts binary palindromes such as '', '0', '1', '00', '11', '101', '010', etc., while rejecting non-palindromic strings like '01', '10', '001', etc.",
        alphabet=["0", "1", "_"],
        objective="Accept if the input reads the same forwards and backwards.",
        mode="accept",
        correct_examples=["", "0", "1", "00", "11", "101", "010", "111", "000", "1001", "0110"],
        wrong_examples=["01", "10", "001", "110", "100", "011", "1010", "1100"]
    ),
    Level(
        name="Level 5: Letters",
        type = "Starter",
        description="Accept strings that contain the letter A followed by B.",
        detailedDescription="Turing machine accepts strings where 'A' appears before 'B', such as 'AB', 'ACB', 'AAB', etc., while rejecting strings where 'B' appears before 'A' or where 'A' is absent, such as 'BA', 'BCA', 'CBA', etc.",
        alphabet=["A", "B", "C", "_"],
        objective="Accept if 'A' appears before 'B' in the string.",
        mode="accept",
        correct_examples=["AB", "ACB", "AAB", "CCCCABBBBBCCB", "AAACCCBBB"],
        wrong_examples=["BA", "BCA", "CBA", "BBB"]
    ),
    Level(
        name="Level 6: Even 0s",
        type = "Starter",
        description="Accept binary strings with an even number of 0s.",
        detailedDescription="Turing machine accepts binary strings that contain an even number of '0's, such as '11', '00', '1100', '1010', etc., while rejecting strings with an odd number of '0's like '0', '10', '01', '000', etc.",
        alphabet=["0", "1", "_"],
        objective="Accept if the count of '0's is even, reject otherwise.",
        mode="accept",
        correct_examples=["1100","1", "11", "111", "00", "11", "101", "1100", "1001", "0110"],
        wrong_examples=["0", "10", "01", "000", "100", "010", "001", "1110", "1010", "1101"]
    ),
    Level(
        name="Transforming: Flip 0s and 1s",
        type = "Medium",
        description="Flip all 0s to 1s and all 1s to 0s in a binary string.",
        detailedDescription="Turing machine transforms a binary string by flipping all '0's to '1's and all '1's to '0's. For example, it should transform '1010' to '0101', '111000' to '000111', and '000' to '111'. Can be achieved with using write.",
        alphabet=["0", "1", "_"],
        objective="Accept if the count of '0's is even, reject otherwise.",
        mode="transform",
        transform_tests= [ {"input": "1010", "output": "0101"} , {"input": "111000", "output": "000111"}, {"input": "000", "output": "111"}, {"input": "1", "output": "0"}, {"input": "", "output": ""} ]
    ),
    Level(
        name="Transforming: Add 1",
        type = "Medium",
        description="Add 1 to a binary number.",
        detailedDescription="Turing machine adds 1 to a binary number represented as a string. For example, it should transform '101' to '110', '111' to '1000', and '0' to '1', Etc..",
        alphabet=["0", "1", "_"],
        objective="Transform the binary number by adding 1.",
        mode="transform",
        transform_tests= [ {"input": "101", "output": "110"} , {"input": "111", "output": "1000"}, {"input": "0", "output": "1"}, {"input": "1101", "output": "1110"}, {"input": "10011", "output": "10100"} ]
    ),
    Level(
        name="Transforming: Reverse String",
        type = "Hard",
        description="Reverse the input string.",
        detailedDescription="Turing machine reverses the input string. For example, it should transform 'abcde' to 'edcba', 'dab' to 'bad', the logic is simple but it requires alot of states.",
        alphabet=["a", "b", "c", "d", "e", "_"],
        objective="Reverse the input string.",
        mode="transform",
        transform_tests= [ {"input": "abc", "output": "cba"} , {"input": "bad", "output": "dab"}, {"input": "deeb", "output": "beed"}, {"input": "dada", "output": "adad"}, {"input": "ada", "output": "ada"} ]
    ),
]