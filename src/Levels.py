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
        correct_examples=["1", "0", "1100", "101", "111", "000", "1001", "0110"],
        wrong_examples=[""]
    ),
    Level(
        name="How to Play 2: Transformations",
        type = "Tutorial",
        description="Learn the core mechanics of building a Turing Machine that transforms input.",
        detailedDescription="Build a Turing machine that transforms all binary elements to blank. So for example 101 becomes ___",
        alphabet=["0", "1", "_"],
        objective="Turn all 0s and 1s to _",
        mode="transform",
        transform_tests=[ {"input": "101", "output": ""}, {"input": "1", "output": ""}, {"input": "0", "output": ""}, {"input": "", "output": ""} ]
    ),
    Level(
        name="How to Play 3: Double Tape",
        type = "Tutorial",
        description="Learn the core mechanics of building a Two-Tape Turing Machine.",
        detailedDescription="Build a Two-Tape Turing machine that copies the input from the first tape to the second tape. So for example 101 becomes 101 on the second tape.",
        alphabet=["0", "1", "_"],
        objective="Copy the input from the first tape to the second tape.",
        mode="transform",
        transform_tests=[ {"input": "101", "output": "101"}, {"input": "1", "output": "1"}, {"input": "0", "output": "0"}, {"input": "", "output": ""} ],
        double_tape=True
    ),
    Level(
        name="Flip 0s and 1s",
        type = "Starter",
        description="Flip all 0s to 1s and all 1s to 0s in a binary string.",
        detailedDescription="Turing machine transforms a binary string by flipping all '0's to '1's and all '1's to '0's. For example, it should transform '1010' to '0101', '111000' to '000111', and '000' to '111'. Can be achieved with using write.",
        alphabet=["0", "1", "_"],
        objective="Accept if the count of '0's is even, reject otherwise.",
        mode="transform",
        transform_tests= [ {"input": "1010", "output": "0101"} , {"input": "111000", "output": "000111"}, {"input": "000", "output": "111"}, {"input": "1", "output": "0"}, {"input": "", "output": ""} ]
    ),
    Level(
        name="Accept 101",
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
        name="No 001",
        type = "Starter",
        description="Accept binary strings that do not contain the substring 001.",
        detailedDescription="Turing machine accepts any binary string that does not contain the substring '001'. For example, it should accept '0', '1', '00', '01', '10', '11', '000', '010', etc., but reject '001', '1001', '0001', etc.",
        alphabet=["0", "1", "_"],
        objective="Reject any input containing '001'.",
        mode="accept",
        correct_examples=["110","0", "1", "00", "01", "10", "11", "000", "010", "100", "101", "111"],
        wrong_examples=["001", "1001", "0001", "0010", "101001"]
    ),
    Level(
        name="Count 1s",
        type = "Starter",
        description="Accept strings with exactly three 1s.",
        detailedDescription="Turing machine accepts strings with exactly three 1s while rejecting all others. For example, it should accept '111', '1011', '000110001', etc., but reject '', '0', '1', '11', '1111', etc.",
        alphabet=["0", "1", "_"],
        objective="Accept if there are exactly three '1's in the input.",
        mode="accept",
        correct_examples=["1011","111", "000110001", "100000000101", "110001", "010101", "0111", "111000"],
        wrong_examples=["", "0", "1", "11", "1111", "000", "1000111", "0001", "1010", "1100", "0011", "0110"]
    ),
    Level(
        name="Letters",
        type = "Starter",
        description="Accept strings where ALL A's come before ALL B's. Like ACCB but not BACA.",
        detailedDescription="Turing machine accepts strings where 'A' appears before 'B', such as 'AB', 'ACB', 'AAB', etc., while rejecting strings where 'B' appears before 'A' or where 'A' is absent, such as 'BA', 'BCA', 'CBA', etc.",
        alphabet=["A", "B", "C", "_"],
        objective="Accept if 'A' appears before 'B' in the string.",
        mode="accept",
        correct_examples=["AB", "ACB", "AAB", "CCCCABBBBBCCB", "AAACCCBBB"],
        wrong_examples=["BA", "BCA", "CBA", "BBB"]
    ),
    Level(
        name="Even 0s",
        type = "Starter",
        description="Accept binary strings with an even number of 0s.",
        detailedDescription="Turing machine accepts binary strings that contain an even number of '0's, such as '11', '00', '1100', '1010', etc., while rejecting strings with an odd number of '0's like '0', '10', '01', '000', etc.",
        alphabet=["0", "1", "_"],
        objective="Accept if the count of '0's is even, reject otherwise.",
        mode="accept",
        correct_examples=["1100","1", "11", "111", "00", "11", "1010", "1100", "1001", "0110"],
        wrong_examples=["0", "10", "01", "000", "1110", "1101", "1010101", "00000"]
    ),
    Level(
        name="Palindrome",
        type = "Medium",
        description="Accept binary palindromes.",
        detailedDescription="Turing machine accepts binary palindromes such as '', '0', '1', '00', '11', '101', '010', etc., while rejecting non-palindromic strings like '01', '10', '001', etc.",
        alphabet=["0", "1", "_"],
        objective="Accept if the input reads the same forwards and backwards.",
        mode="accept",
        correct_examples=["0110","", "0", "1", "00", "11", "101", "010", "111", "000", "1001"],
        wrong_examples=["01", "10", "001", "110", "100", "011", "1010", "1100"]
    ),
    Level(
        name="Binaries: Add 1",
        type = "Medium",
        description="Add 1 to a binary number.",
        detailedDescription="Turing machine adds 1 to a binary number represented as a string. For example, it should transform '101' to '110', '111' to '1000', and '0' to '1', Etc..",
        alphabet=["0", "1", "_"],
        objective="Transform the binary number by adding 1.",
        mode="transform",
        transform_tests= [ {"input": "101", "output": "110"} , {"input": "111", "output": "1000"}, {"input": "0", "output": "1"}, {"input": "1101", "output": "1110"}, {"input": "10011", "output": "10100"} ]
    ),
    Level(
        name="Binaries: Subtract 1",
        type = "Medium",
        description="Subtract 1 from a binary number.",
        detailedDescription="Turing machine subtracts 1 from a binary number represented as a string. For example, it should transform '110' to '101', '1000' to '111', and '1' to '', Etc..",
        alphabet=["0", "1", "_"],
        objective="Transform the binary number by subtracting 1.",
        mode="transform",
        transform_tests= [ {"input": "110", "output": "101"} , {"input": "1000", "output": "111"}, {"input": "1", "output": ""}, {"input": "1110", "output": "1101"}, {"input": "10100", "output": "10011"} ]
    ),
    Level(
        name="N repetitions",
        type="Medium",
        description="Accept strings of the form 0^n1^n (n 0s followed by n 1s).",
        detailedDescription="Turing machine accepts strings that consist of '0's followed by '1's, where the number of '0's is equal to the number of '1's. For example, it should accept '0011', '000111', and '', while rejecting strings like '0001111', '1100', '00011111', etc.",
        alphabet=["0", "1", "_"],
        objective="Accept if the input is of the form 0^n1^n.",
        mode="accept",
        correct_examples=["000111", "", "01", "0011", "00001111", "0000011111"],
        wrong_examples=["0", "1", "10", "11", "0001111", "00111", "001", "1100", "111000", "00011111"]
    ),
    Level(
        name="N repetitions and M repetitions",
        type="Medium",
        description="Accept strings of the form 0^n1^m (n 0s followed by m 1s). where m = 2*n",
        detailedDescription="Turing machine accepts strings that consist of '0's followed by '1's, where the number of '1's is exactly two times the number of '0's. For example, it should accept '000111111', '011', and '', while rejecting strings like '00111', '1100', '00011111', etc.",
        alphabet=["0", "1", "_"],
        objective="Accept if the input is of the form 0^n1^m where m = 2*n.",
        mode="accept",
        correct_examples=["000111111", "", "011", "001111", "000111111", "000011111111", "000001111111111"],
        wrong_examples=["0", "1", "10", "11", "01", "0001111", "00111", "0011", "001", "1100", "111000", "00011111"]
    ),
    Level(
        name="Pairs of 1s",
        type = "Medium",
        description = "Accept binary strings where all 1s appear in pairs.",
        detailedDescription="Turing machine accepts binary strings where every '1' appears in pairs, such as '0011', '00011011', '11', etc., while rejecting strings with unpaired '1's like '1', '101', '111', etc.",
        alphabet=["0", "1", "_"],
        objective="Accept if all '1's appear in pairs.",
        mode="accept",
        correct_examples=["0011","00011011", "11", "1100", "00110011", "000000011"],
        wrong_examples=["1", "101", "111", "10", "01", "0001", "1000", "1110"]
    ),
    Level(
        name="Most Frequent Character",
        type = "Hard",
        description="Given a binary word, output only the most used character, incase of a tie output 0.",
        detailedDescription="Turing machine reads a binary string and outputs the character ('0' or '1') that appears most frequently in the input. Incase of a tie, it should output '0'. For example, it should transform '1100' to '0', '1111000' to '1', and '10100' to '0'.",
        alphabet=["0", "1", "_"],
        objective="Output the most frequent character, or '0' in case of a tie.",
        mode="transform",
        transform_tests= [ {"input": "1100", "output": "0"} , {"input": "11100", "output": "1"}, {"input": "1010101", "output": "1"}, {"input": "1111", "output": "1"}, {"input": "000", "output": "0"}, {"input": "101010", "output": "0"} ]
    ),
    Level(
        name="1s to binary",
        type = "Hard",
        description="Convert a unary number (a series of 1s) to its binary representation.",
        detailedDescription="Turing machine converts a unary number, represented as a series of '1's, into its binary representation. For example, it should transform '111' to '11' (which is 3 in binary), '11111' to '101' (which is 5 in binary), and '1' to '1' (which is 1 in binary).",
        alphabet=["1", "0", "_", "#"],
        objective="Convert unary '1's to their binary representation.",
        mode="transform",
        transform_tests= [ {"input": "111", "output": "11"} , {"input": "11111", "output": "101"}, {"input": "1", "output": "1"}, {"input": "1111111", "output": "111"}, {"input": "11111111", "output": "1000"}, {"input": "", "output": ""} ]
    ),
    Level(
        name="Two Tapes: Longest Run",
        type = "Hard",
        description="Find the longest run of consecutive 1s or 0s in a binary string.",
        detailedDescription="Turing machine finds the longest consecutive sequence (run) of either '0's or '1's in a binary string and outputs that sequence. For example, it should transform '1100011110' to '1111', '0001111000' to '0000', and '101010' to '1'. Incase of a tie pick the 1s for example: '1100' output '11'.",
        alphabet=["0", "1", "_"],
        objective="Output the longest run of consecutive '0's or '1's.",
        mode="transform",
        transform_tests= [ {"input": "1100011110", "output": "1111"} , {"input": "0001111000", "output": "1111"}, {"input": "101010", "output": "1"}, {"input": "111100001111", "output": "1111"}, {"input": "000000111", "output": "000000"} ],
        double_tape=True
    ),
    Level(
        name="Two Tapes: Add binaries",
        type = "Hard",
        description="Add two binary numbers separated by a # symbol.",
        detailedDescription="Turing machine adds two binary numbers, where the two numbers are separated by a '#' symbol. For example, it should transform '1101#101' to '10010' (which is 13 + 5 = 18 in binary), '1000#1' to '1001' (which is 8 + 1 = 9 in binary), and '1010#10' to '1100' (which is 10 + 2 = 12 in binary).",
        alphabet=["0", "1", "_", "#"],
        objective="Add the two binary numbers. The result must be on the bottom tape.",
        mode="transform",
        transform_tests= [ {"input": "1101#101", "output": "10010"} , {"input": "1000#1", "output": "1001"}, {"input": "1010#10", "output": "1100"}, {"input": "1111#111", "output": "11110"}, {"input": "10000#1", "output": "10001"} ],
    ),
    Level(
        name="Two Tapes: Subtract binaries",
        type = "Hard",
        description="Subtract two binary numbers separated by a # symbol.",
        detailedDescription="Turing machine subtracts the second binary number from the first binary number, where the two numbers are separated by a '#' symbol. For example, it should transform '1101#101' to '1000' (which is 13 - 5 = 8 in binary), '1000#1' to '111' (which is 8 - 1 = 7 in binary), and '1010#10' to '1000' (which is 10 - 2 = 8 in binary). Consider only non-negative results.",
        alphabet=["0", "1", "_", "#"],
        objective="Subtract the second binary number from the first. The result must be on the bottom tape.",
        mode="transform",
        transform_tests= [ {"input": "1101#101", "output": "1000"} , {"input": "1000#1", "output": "111"}, {"input": "1010#10", "output": "1000"}, {"input": "1111#111", "output": "1000"}, {"input": "10000#1", "output": "1111"} ],
        double_tape=True
    ),
    Level(
        name="Two Tapes: Sorting",
        type = "Hard",
        description="Sort a word of 1 to 5 from least to greatetest, left to right.",
        detailedDescription="Turing machine sorts a string of digits (from '1' to '5') in ascending order from left to right. For example, it should transform '321' to '123', '54321' to '12345', and '2143' to '1234' Incase of a tie keep both together for example '1122'.",
        alphabet=["1", "2", "3", "4", "5", "_"],
        objective="Sort the input string in ascending order.",
        mode="transform",
        transform_tests= [ {"input": "321", "output": "123"} , {"input": "54321", "output": "12345"}, {"input": "2143", "output": "1234"}, {"input": "5", "output": "5"}, {"input": "111221", "output": "111122"} ],
        double_tape=True
    ),
]