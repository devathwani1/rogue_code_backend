"""
45 LeetCode-style problems with schemas matching evaluator TypeSchema (python_runner).
Indices 0–29: prior curriculum; 30–44: arrays, two pointers, greedy, intervals, heap.
Daily plan layouts pick subsets from this list.
"""

INT = {"kind": "primitive", "name": "int"}
BOOL = {"kind": "primitive", "name": "bool"}
STRING = {"kind": "primitive", "name": "string"}

INT_ARRAY = {"kind": "array", "of": INT}
STRING_ARRAY = {"kind": "array", "of": STRING}
INT_MATRIX = {"kind": "array", "of": INT_ARRAY}
STRING_ARRAY_ARRAY = {"kind": "array", "of": STRING_ARRAY}
INT_ARRAY_ARRAY = {"kind": "array", "of": INT_ARRAY}


def _q(
    title: str,
    description: str,
    constraints: str,
    function_name: str,
    return_type: dict,
    difficulty: str,
    parameters: list[dict],
    test_cases: list[dict],
) -> dict:
    return {
        "title": title,
        "description": description,
        "constraints": constraints,
        "function_name": function_name,
        "return_type": return_type,
        "difficulty": difficulty,
        "parameters": parameters,
        "test_cases": test_cases,
    }


# --- Questions in fixed order (index = 0 .. 44) ---

CHALLENGE_QUESTIONS: list[dict] = [
    _q(
        title="Two Sum (No Hash Map)",
        description=(
            "Given an integer array nums and an integer target, return indices i and j "
            "(i < j) such that nums[i] + nums[j] == target. "
            "You must solve it without using a hash map or hash set (no dict/set for lookups). "
            "Exactly one valid pair exists."
        ),
        constraints=(
            "2 <= nums.length <= 10^4\n"
            "-10^9 <= nums[i], target <= 10^9\n"
            "Exactly one solution exists."
        ),
        function_name="twoSum",
        return_type=INT_ARRAY,
        difficulty="easy",
        parameters=[
            {"name": "nums", "order": 1, "type_schema": INT_ARRAY},
            {"name": "target", "order": 2, "type_schema": {"kind": "primitive", "name": "int"}},
        ],
        test_cases=[
            {"input_data": [[2, 7, 11, 15], 9], "expected_output": [0, 1]},
            {"input_data": [[3, 2, 4], 6], "expected_output": [1, 2]},
            {"input_data": [[3, 3], 6], "expected_output": [0, 1]},
        ],
    ),
    _q(
        title="Valid Palindrome (Ignore Non-Alphanumeric)",
        description=(
            "Given a string s, return true if it is a palindrome after removing all "
            "non-alphanumeric characters and ignoring case. Only consider letters and digits."
        ),
        constraints="0 <= s.length <= 2 * 10^5\ns is printable ASCII.",
        function_name="isPalindrome",
        return_type=BOOL,
        difficulty="easy",
        parameters=[
            {"name": "s", "order": 1, "type_schema": STRING},
        ],
        test_cases=[
            {"input_data": ["A man, a plan, a canal: Panama"], "expected_output": True},
            {"input_data": ["race a car"], "expected_output": False},
            {"input_data": [""], "expected_output": True},
        ],
    ),
    _q(
        title="First Unique Character in a String",
        description=(
            "Given a string s, return the index of the first non-repeating character. "
            "If none exists, return -1."
        ),
        constraints="1 <= s.length <= 10^5\ns contains only lowercase English letters.",
        function_name="firstUniqChar",
        return_type=INT,
        difficulty="easy",
        parameters=[{"name": "s", "order": 1, "type_schema": STRING}],
        test_cases=[
            {"input_data": ["leetcode"], "expected_output": 0},
            {"input_data": ["loveleetcode"], "expected_output": 2},
            {"input_data": ["aabb"], "expected_output": -1},
        ],
    ),
    _q(
        title="Product of Array Except Self",
        description=(
            "Given an integer array nums, return an array answer where answer[i] equals "
            "the product of all elements except nums[i]. "
            "Solve in O(n) without using division."
        ),
        constraints=(
            "2 <= nums.length <= 10^5\n"
            "-30 <= nums[i] <= 30\n"
            "Prefix/suffix products fit in 32-bit signed integers."
        ),
        function_name="productExceptSelf",
        return_type=INT_ARRAY,
        difficulty="medium",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[1, 2, 3, 4]], "expected_output": [24, 12, 8, 6]},
            {"input_data": [[0, 0]], "expected_output": [0, 0]},
            {"input_data": [[-1, 1, 0, -3, 3]], "expected_output": [0, 0, 9, 0, 0]},
        ],
    ),
    _q(
        title="Move Zeroes (In-Place)",
        description=(
            "Given an integer array nums, move all 0s to the end while preserving the "
            "relative order of non-zero elements. Mutate nums in place and return the same list "
            "(so the judge can verify the result)."
        ),
        constraints="1 <= nums.length <= 10^4\n-2^31 <= nums[i] <= 2^31 - 1",
        function_name="moveZeroes",
        return_type=INT_ARRAY,
        difficulty="easy",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[0, 1, 0, 3, 12]], "expected_output": [1, 3, 12, 0, 0]},
            {"input_data": [[0]], "expected_output": [0]},
            {"input_data": [[1, 2, 3]], "expected_output": [1, 2, 3]},
        ],
    ),
    _q(
        title="Valid Anagram",
        description=(
            "Given two strings s and t, return true if t is an anagram of s, else false. "
            "An anagram uses all original letters exactly once."
        ),
        constraints="0 <= s.length, t.length <= 5 * 10^4\ns and t are lowercase English letters.",
        function_name="isAnagram",
        return_type=BOOL,
        difficulty="easy",
        parameters=[
            {"name": "s", "order": 1, "type_schema": STRING},
            {"name": "t", "order": 2, "type_schema": STRING},
        ],
        test_cases=[
            {"input_data": ["anagram", "nagaram"], "expected_output": True},
            {"input_data": ["rat", "car"], "expected_output": False},
            {"input_data": ["", ""], "expected_output": True},
        ],
    ),
    _q(
        title="Longest Common Prefix",
        description=(
            "Given an array of strings strs, return the longest common prefix among them. "
            "If there is none, return an empty string."
        ),
        constraints="1 <= strs.length <= 200\n0 <= strs[i].length <= 200",
        function_name="longestCommonPrefix",
        return_type=STRING,
        difficulty="easy",
        parameters=[{"name": "strs", "order": 1, "type_schema": STRING_ARRAY}],
        test_cases=[
            {"input_data": [["flower", "flow", "flight"]], "expected_output": "fl"},
            {"input_data": [["dog", "racecar", "car"]], "expected_output": ""},
            {"input_data": [[""]], "expected_output": ""},
        ],
    ),
    _q(
        title="Reverse Words in a String",
        description=(
            "Given a string s, reverse the order of words. Words are separated by spaces. "
            "Trim leading/trailing spaces and collapse internal spacing to single spaces in the output."
        ),
        constraints="1 <= s.length <= 10^4\ns contains printable characters.",
        function_name="reverseWords",
        return_type=STRING,
        difficulty="medium",
        parameters=[{"name": "s", "order": 1, "type_schema": STRING}],
        test_cases=[
            {"input_data": ["the sky is blue"], "expected_output": "blue is sky the"},
            {"input_data": ["  hello world  "], "expected_output": "world hello"},
            {"input_data": ["a"], "expected_output": "a"},
        ],
    ),
    _q(
        title="Majority Element",
        description=(
            "Given an array nums of length n, return the element that appears strictly more "
            "than floor(n / 2) times. Such an element always exists."
        ),
        constraints="1 <= nums.length <= 5 * 10^4\n-10^9 <= nums[i] <= 10^9",
        function_name="majorityElement",
        return_type=INT,
        difficulty="easy",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[3, 2, 3]], "expected_output": 3},
            {"input_data": [[2, 2, 1, 1, 1, 2, 2]], "expected_output": 2},
            {"input_data": [[1]], "expected_output": 1},
        ],
    ),
    _q(
        title="Missing Number",
        description=(
            "Given an array nums containing n distinct numbers from 0 to n, "
            "return the only number in that range missing from the array."
        ),
        constraints="1 <= nums.length <= 10^4\n0 <= nums[i] <= n\nAll values are unique.",
        function_name="missingNumber",
        return_type=INT,
        difficulty="easy",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[3, 0, 1]], "expected_output": 2},
            {"input_data": [[0, 1]], "expected_output": 2},
            {"input_data": [[9, 6, 4, 2, 3, 5, 7, 0, 1]], "expected_output": 8},
        ],
    ),
    _q(
        title="Intersection of Two Arrays",
        description=(
            "Given two integer arrays nums1 and nums2, return a sorted array of distinct integers "
            "that appear in both arrays."
        ),
        constraints="1 <= nums1.length, nums2.length <= 1000\n0 <= nums[i] <= 1000",
        function_name="intersection",
        return_type=INT_ARRAY,
        difficulty="easy",
        parameters=[
            {"name": "nums1", "order": 1, "type_schema": INT_ARRAY},
            {"name": "nums2", "order": 2, "type_schema": INT_ARRAY},
        ],
        test_cases=[
            {"input_data": [[1, 2, 2, 1], [2, 2]], "expected_output": [2]},
            {"input_data": [[4, 9, 5], [9, 4, 9, 8, 4]], "expected_output": [4, 9]},
            {"input_data": [[1, 2, 3], [4, 5, 6]], "expected_output": []},
        ],
    ),
    _q(
        title="Contains Duplicate II (At Most k Apart)",
        description=(
            "Given an integer array nums and an integer k, return true if there exist "
            "distinct indices i and j such that nums[i] == nums[j] and abs(i - j) <= k."
        ),
        constraints="1 <= nums.length <= 10^5\n-10^9 <= nums[i] <= 10^9\n0 <= k <= 10^5",
        function_name="containsNearbyDuplicate",
        return_type=BOOL,
        difficulty="medium",
        parameters=[
            {"name": "nums", "order": 1, "type_schema": INT_ARRAY},
            {"name": "k", "order": 2, "type_schema": INT},
        ],
        test_cases=[
            {"input_data": [[1, 2, 3, 1], 3], "expected_output": True},
            {"input_data": [[1, 0, 1, 1], 1], "expected_output": True},
            {"input_data": [[1, 2, 3, 4, 5], 2], "expected_output": False},
        ],
    ),
    _q(
        title="Rotate Array (In-Place)",
        description=(
            "Given an integer array nums and non-negative k, rotate nums to the right by k steps. "
            "Mutate nums in place and return the same list for verification."
        ),
        constraints="1 <= nums.length <= 10^5\n-2^31 <= nums[i] <= 2^31 - 1\n0 <= k <= 10^5",
        function_name="rotate",
        return_type=INT_ARRAY,
        difficulty="medium",
        parameters=[
            {"name": "nums", "order": 1, "type_schema": INT_ARRAY},
            {"name": "k", "order": 2, "type_schema": INT},
        ],
        test_cases=[
            {"input_data": [[1, 2, 3, 4, 5, 6, 7], 3], "expected_output": [5, 6, 7, 1, 2, 3, 4]},
            {"input_data": [[-1], 2], "expected_output": [-1]},
            {"input_data": [[1, 2], 1], "expected_output": [2, 1]},
        ],
    ),
    _q(
        title="Merge Sorted Array (In-Place)",
        description=(
            "You are given two integer arrays nums1 and nums2 and integers m and n. "
            "nums1 has length m + n, with the last n slots as zeros. Merge nums2 into nums1 "
            "as one sorted array in non-decreasing order, in place. Return nums1."
        ),
        constraints=(
            "nums1.length == m + n\n"
            "nums2.length == n\n"
            "0 <= m, n <= 200\n"
            "1 <= m + n <= 200\n"
            "-10^9 <= nums1[i], nums2[j] <= 10^9"
        ),
        function_name="merge",
        return_type=INT_ARRAY,
        difficulty="hard",
        parameters=[
            {"name": "nums1", "order": 1, "type_schema": INT_ARRAY},
            {"name": "m", "order": 2, "type_schema": INT},
            {"name": "nums2", "order": 3, "type_schema": INT_ARRAY},
            {"name": "n", "order": 4, "type_schema": INT},
        ],
        test_cases=[
            {
                "input_data": [[1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3],
                "expected_output": [1, 2, 2, 3, 5, 6],
            },
            {"input_data": [[1], 1, [], 0], "expected_output": [1]},
            {"input_data": [[0], 0, [1], 1], "expected_output": [1]},
        ],
    ),
    _q(
        title="Best Time to Buy and Sell Stock",
        description=(
            "Given an array prices where prices[i] is the price on day i, choose one day to buy "
            "and a later day to sell to maximize profit. Return that maximum profit; "
            "if no profit is possible, return 0."
        ),
        constraints="1 <= prices.length <= 10^5\n0 <= prices[i] <= 10^4",
        function_name="maxProfit",
        return_type=INT,
        difficulty="easy",
        parameters=[{"name": "prices", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[7, 1, 5, 3, 6, 4]], "expected_output": 5},
            {"input_data": [[7, 6, 4, 3, 1]], "expected_output": 0},
            {"input_data": [[1, 2]], "expected_output": 1},
        ],
    ),
    # --- Batch 2 (indices 15–29) ---
    _q(
        title="Longest Substring Without Repeating Characters",
        description=(
            "Given a string s, return the length of the longest substring without repeating characters."
        ),
        constraints="0 <= s.length <= 5 * 10^4\ns consists of English letters, digits, symbols and spaces.",
        function_name="lengthOfLongestSubstring",
        return_type=INT,
        difficulty="medium",
        parameters=[{"name": "s", "order": 1, "type_schema": STRING}],
        test_cases=[
            {"input_data": ["abcabcbb"], "expected_output": 3},
            {"input_data": ["bbbbb"], "expected_output": 1},
            {"input_data": [""], "expected_output": 0},
        ],
    ),
    _q(
        title="Minimum Size Subarray Sum",
        description=(
            "Given an array of positive integers nums and a positive integer target, return the "
            "minimal length of a contiguous subarray with sum >= target. If none exists, return 0."
        ),
        constraints="1 <= nums.length <= 10^5\n1 <= nums[i] <= 10^4\n1 <= target <= 10^9",
        function_name="minSubArrayLen",
        return_type=INT,
        difficulty="medium",
        parameters=[
            {"name": "target", "order": 1, "type_schema": INT},
            {"name": "nums", "order": 2, "type_schema": INT_ARRAY},
        ],
        test_cases=[
            {"input_data": [7, [2, 3, 1, 2, 4, 3]], "expected_output": 2},
            {"input_data": [4, [1, 4, 4]], "expected_output": 1},
            {"input_data": [11, [1, 1, 1, 1, 1, 1, 1, 1]], "expected_output": 0},
        ],
    ),
    _q(
        title="Subarray Sum Equals K",
        description=(
            "Given an integer array nums and an integer k, return the total number of contiguous "
            "subarrays whose sum equals k."
        ),
        constraints="1 <= nums.length <= 2 * 10^4\n-1000 <= nums[i] <= 1000\n-10^7 <= k <= 10^7",
        function_name="subarraySum",
        return_type=INT,
        difficulty="medium",
        parameters=[
            {"name": "nums", "order": 1, "type_schema": INT_ARRAY},
            {"name": "k", "order": 2, "type_schema": INT},
        ],
        test_cases=[
            {"input_data": [[1, 1, 1], 2], "expected_output": 2},
            {"input_data": [[1, 2, 3], 3], "expected_output": 2},
            {"input_data": [[1, -1, 0], 0], "expected_output": 3},
        ],
    ),
    _q(
        title="Find All Anagrams in a String",
        description=(
            "Given strings s and p, return the starting indices of all anagrams of p in s, "
            "in ascending order."
        ),
        constraints="1 <= s.length, p.length <= 3 * 10^4\ns and p contain only lowercase English letters.",
        function_name="findAnagrams",
        return_type=INT_ARRAY,
        difficulty="medium",
        parameters=[
            {"name": "s", "order": 1, "type_schema": STRING},
            {"name": "p", "order": 2, "type_schema": STRING},
        ],
        test_cases=[
            {"input_data": ["cbaebabacd", "abc"], "expected_output": [0, 6]},
            {"input_data": ["abab", "ab"], "expected_output": [0, 1, 2]},
            {"input_data": ["aaaaaa", "aa"], "expected_output": [0, 1, 2, 3, 4]},
        ],
    ),
    _q(
        title="Longest Repeating Character Replacement",
        description=(
            "Given a string s and an integer k, you may replace at most k characters so that all "
            "letters in the substring are identical. Return the length of the longest such substring."
        ),
        constraints="1 <= s.length <= 10^5\ns contains only uppercase English letters.\n0 <= k <= s.length",
        function_name="characterReplacement",
        return_type=INT,
        difficulty="medium",
        parameters=[
            {"name": "s", "order": 1, "type_schema": STRING},
            {"name": "k", "order": 2, "type_schema": INT},
        ],
        test_cases=[
            {"input_data": ["AABABBA", 2], "expected_output": 4},
            {"input_data": ["ABAB", 2], "expected_output": 4},
            {"input_data": ["AAAA", 2], "expected_output": 4},
        ],
    ),
    _q(
        title="Group Anagrams",
        description=(
            "Given an array of strings strs, group the anagrams together. "
            "Each inner list must be sorted lexicographically; the list of groups must be sorted "
            "lexicographically by the first string in each group."
        ),
        constraints="1 <= strs.length <= 10^4\n0 <= strs[i].length <= 100",
        function_name="groupAnagrams",
        return_type=STRING_ARRAY_ARRAY,
        difficulty="medium",
        parameters=[{"name": "strs", "order": 1, "type_schema": STRING_ARRAY}],
        test_cases=[
            {
                "input_data": [["eat", "tea", "tan", "ate", "nat", "bat"]],
                "expected_output": [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]],
            },
            {"input_data": [["a"]], "expected_output": [["a"]]},
            {"input_data": [[""]], "expected_output": [[""]]},
        ],
    ),
    _q(
        title="Top K Frequent Elements",
        description=(
            "Given an integer array nums and an integer k, return the k most frequent elements. "
            "Return them sorted in ascending order so the judge can compare outputs deterministically."
        ),
        constraints="1 <= nums.length <= 10^5\nk is in range [1, number of unique elements in nums]",
        function_name="topKFrequent",
        return_type=INT_ARRAY,
        difficulty="medium",
        parameters=[
            {"name": "nums", "order": 1, "type_schema": INT_ARRAY},
            {"name": "k", "order": 2, "type_schema": INT},
        ],
        test_cases=[
            {"input_data": [[1, 1, 1, 2, 2, 3], 2], "expected_output": [1, 2]},
            {"input_data": [[1], 1], "expected_output": [1]},
            {"input_data": [[7, 7], 1], "expected_output": [7]},
        ],
    ),
    _q(
        title="Encode and Decode Strings",
        description=(
            "Implement encode(strs) that serializes a list of strings to a single string using a "
            "length-prefixed format: for each string, write len + '#' + string (length is decimal). "
            "The judge only tests encode output against the expected encoded string."
        ),
        constraints="1 <= strs.length <= 200\n0 <= strs[i].length <= 200",
        function_name="encode",
        return_type=STRING,
        difficulty="medium",
        parameters=[{"name": "strs", "order": 1, "type_schema": STRING_ARRAY}],
        test_cases=[
            {"input_data": [["hello", "world"]], "expected_output": "5#hello5#world"},
            {"input_data": [[""]], "expected_output": "0#"},
            {"input_data": [["a", "bc"]], "expected_output": "1#a2#bc"},
        ],
    ),
    _q(
        title="Valid Sudoku",
        description=(
            "Given a 9 x 9 Sudoku board represented as nine strings of length nine, "
            "each character is a digit '1'-'9' or '.'. Return true if the board could be valid "
            "(no duplicate non-empty digits in any row, column, or 3x3 box)."
        ),
        constraints="board.length == 9\nEach board[i] has length 9",
        function_name="isValidSudoku",
        return_type=BOOL,
        difficulty="medium",
        parameters=[{"name": "board", "order": 1, "type_schema": STRING_ARRAY}],
        test_cases=[
            {
                "input_data": [
                    [
                        "53..7....",
                        "6..195....",
                        ".98....6.",
                        "8...6...3",
                        "4..8.3..1",
                        "7...2...6",
                        ".6....28.",
                        "...419..5",
                        "....8..79",
                    ]
                ],
                "expected_output": True,
            },
            {
                "input_data": [
                    [
                        "88..7....",
                        "6..195....",
                        ".98....6.",
                        "8...6...3",
                        "4..8.3..1",
                        "7...2...6",
                        ".6....28.",
                        "...419..5",
                        "....8..79",
                    ]
                ],
                "expected_output": False,
            },
            {
                "input_data": [["........."] * 9],
                "expected_output": True,
            },
        ],
    ),
    _q(
        title="Spiral Matrix",
        description=(
            "Given an m x n matrix of integers, return all elements of the matrix in spiral order, "
            "starting from the top-left, moving right, then down, left, up, and repeating."
        ),
        constraints="1 <= matrix.length, matrix[i].length <= 10",
        function_name="spiralOrder",
        return_type=INT_ARRAY,
        difficulty="medium",
        parameters=[{"name": "matrix", "order": 1, "type_schema": INT_MATRIX}],
        test_cases=[
            {"input_data": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "expected_output": [1, 2, 3, 6, 9, 8, 7, 4, 5]},
            {"input_data": [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]], "expected_output": [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]},
            {"input_data": [[[42]]], "expected_output": [42]},
        ],
    ),
    _q(
        title="Set Matrix Zeroes",
        description=(
            "Given an m x n integer matrix, if an element is 0, set its entire row and column to 0. "
            "Do it in place and return the modified matrix."
        ),
        constraints="1 <= matrix.length, matrix[i].length <= 200\n-2^31 <= matrix[i][j] <= 2^31 - 1",
        function_name="setZeroes",
        return_type=INT_MATRIX,
        difficulty="medium",
        parameters=[{"name": "matrix", "order": 1, "type_schema": INT_MATRIX}],
        test_cases=[
            {"input_data": [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], "expected_output": [[1, 0, 1], [0, 0, 0], [1, 0, 1]]},
            {"input_data": [[[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]], "expected_output": [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]},
            {"input_data": [[[1, 2], [3, 4]]], "expected_output": [[1, 2], [3, 4]]},
        ],
    ),
    _q(
        title="Rotate Image (Matrix)",
        description=(
            "Given an n x n 2D matrix representing an image, rotate the image 90 degrees clockwise "
            "in place. Return the rotated matrix."
        ),
        constraints="1 <= matrix.length == matrix[i].length <= 20\n-1000 <= matrix[i][j] <= 1000",
        function_name="rotateImage",
        return_type=INT_MATRIX,
        difficulty="medium",
        parameters=[{"name": "matrix", "order": 1, "type_schema": INT_MATRIX}],
        test_cases=[
            {"input_data": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "expected_output": [[7, 4, 1], [8, 5, 2], [9, 6, 3]]},
            {"input_data": [[[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]], "expected_output": [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]},
            {"input_data": [[[1, 2], [3, 4]]], "expected_output": [[3, 1], [4, 2]]},
        ],
    ),
    _q(
        title="Word Pattern",
        description=(
            "Given a pattern of letters and a string s of words separated by single spaces, "
            "return true if there is a bijection between pattern letters and words."
        ),
        constraints="1 <= pattern.length <= 300\n1 <= s.length <= 3000",
        function_name="wordPattern",
        return_type=BOOL,
        difficulty="easy",
        parameters=[
            {"name": "pattern", "order": 1, "type_schema": STRING},
            {"name": "s", "order": 2, "type_schema": STRING},
        ],
        test_cases=[
            {"input_data": ["abba", "dog cat cat dog"], "expected_output": True},
            {"input_data": ["abba", "dog dog dog dog"], "expected_output": False},
            {"input_data": ["aaaa", "dog cat cat dog"], "expected_output": False},
        ],
    ),
    _q(
        title="Isomorphic Strings",
        description=(
            "Given two strings s and t, return true if characters in s can be replaced to get t "
            "(one-to-one mapping between characters)."
        ),
        constraints="1 <= s.length <= 5 * 10^4\ns.length == t.length",
        function_name="isIsomorphic",
        return_type=BOOL,
        difficulty="easy",
        parameters=[
            {"name": "s", "order": 1, "type_schema": STRING},
            {"name": "t", "order": 2, "type_schema": STRING},
        ],
        test_cases=[
            {"input_data": ["egg", "add"], "expected_output": True},
            {"input_data": ["foo", "bar"], "expected_output": False},
            {"input_data": ["paper", "title"], "expected_output": True},
        ],
    ),
    _q(
        title="Partition Labels",
        description=(
            "Given a string s of lowercase letters, partition s into as many parts as possible so "
            "that each letter appears in at most one part. Return the length of each part in order."
        ),
        constraints="1 <= s.length <= 500\ns has only lowercase English letters.",
        function_name="partitionLabels",
        return_type=INT_ARRAY,
        difficulty="medium",
        parameters=[{"name": "s", "order": 1, "type_schema": STRING}],
        test_cases=[
            {"input_data": ["ababcbacadefegdehijhklij"], "expected_output": [9, 7, 8]},
            {"input_data": ["eccbbbbdec"], "expected_output": [10]},
            {"input_data": ["abc"], "expected_output": [1, 1, 1]},
        ],
    ),
    # --- Batch 3 (indices 30–44): classic interview II ---
    _q(
        title="3Sum",
        description=(
            "Given an integer array nums, return all unique triplets [nums[i], nums[j], nums[k]] "
            "such that i, j, k are distinct and nums[i] + nums[j] + nums[k] == 0. "
            "Return triplets sorted: each triplet in non-decreasing order, and the list of triplets "
            "sorted lexicographically."
        ),
        constraints="3 <= nums.length <= 3000\n-10^5 <= nums[i] <= 10^5",
        function_name="threeSum",
        return_type=INT_ARRAY_ARRAY,
        difficulty="medium",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[-1, 0, 1, 2, -1, -4]], "expected_output": [[-1, -1, 2], [-1, 0, 1]]},
            {"input_data": [[0, 1, 1]], "expected_output": []},
            {"input_data": [[0, 0, 0]], "expected_output": [[0, 0, 0]]},
        ],
    ),
    _q(
        title="3Sum Closest",
        description=(
            "Given an integer array nums and an integer target, return the sum of three distinct "
            "elements in nums that is closest to target."
        ),
        constraints="3 <= nums.length <= 1000\n-1000 <= nums[i] <= 1000\n-10^4 <= target <= 10^4",
        function_name="threeSumClosest",
        return_type=INT,
        difficulty="medium",
        parameters=[
            {"name": "nums", "order": 1, "type_schema": INT_ARRAY},
            {"name": "target", "order": 2, "type_schema": INT},
        ],
        test_cases=[
            {"input_data": [[-1, 2, 1, -4], 1], "expected_output": 2},
            {"input_data": [[0, 0, 0], 1], "expected_output": 0},
            {"input_data": [[1, 1, 1, 0], 100], "expected_output": 3},
        ],
    ),
    _q(
        title="Container With Most Water",
        description=(
            "Given an integer array height of length n, choose two lines such that together with "
            "the x-axis they form a container. Return the maximum amount of water the container can store."
        ),
        constraints="2 <= height.length <= 10^5\n0 <= height[i] <= 10^4",
        function_name="maxArea",
        return_type=INT,
        difficulty="medium",
        parameters=[{"name": "height", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[1, 8, 6, 2, 5, 4, 8, 3, 7]], "expected_output": 49},
            {"input_data": [[1, 1]], "expected_output": 1},
            {"input_data": [[4, 3, 2, 1, 4]], "expected_output": 16},
        ],
    ),
    _q(
        title="Trapping Rain Water",
        description=(
            "Given n non-negative integers representing an elevation map where the width of each bar is 1, "
            "compute how much water can be trapped after raining."
        ),
        constraints="1 <= height.length <= 2 * 10^4\n0 <= height[i] <= 10^5",
        function_name="trap",
        return_type=INT,
        difficulty="hard",
        parameters=[{"name": "height", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], "expected_output": 6},
            {"input_data": [[4, 2, 0, 3, 2, 5]], "expected_output": 9},
            {"input_data": [[3, 0, 2, 0, 4]], "expected_output": 7},
        ],
    ),
    _q(
        title="Next Permutation",
        description=(
            "Given an array nums, rearrange it into the lexicographically next greater permutation. "
            "If none exists, rearrange to the lowest possible order (sorted ascending). "
            "Mutate nums in place and return it."
        ),
        constraints="1 <= nums.length <= 100\n0 <= nums[i] <= 100",
        function_name="nextPermutation",
        return_type=INT_ARRAY,
        difficulty="medium",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[1, 2, 3]], "expected_output": [1, 3, 2]},
            {"input_data": [[3, 2, 1]], "expected_output": [1, 2, 3]},
            {"input_data": [[1, 1, 5]], "expected_output": [1, 5, 1]},
        ],
    ),
    _q(
        title="Longest Consecutive Sequence",
        description=(
            "Given an unsorted array of integers nums, return the length of the longest consecutive "
            "elements sequence. O(n) time expected."
        ),
        constraints="0 <= nums.length <= 10^5\n-10^9 <= nums[i] <= 10^9",
        function_name="longestConsecutive",
        return_type=INT,
        difficulty="medium",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[100, 4, 200, 1, 3, 2]], "expected_output": 4},
            {"input_data": [[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], "expected_output": 9},
            {"input_data": [[]], "expected_output": 0},
        ],
    ),
    _q(
        title="Find the Duplicate Number (Cycle Detection)",
        description=(
            "Given an array nums of n + 1 integers where each integer is in [1, n] inclusive, "
            "exactly one integer appears twice. Return that duplicate number. "
            "Use O(1) extra space (treat as linked list / cycle) — no extra array/hash proportional to n."
        ),
        constraints="2 <= nums.length <= 10^5\n1 <= nums[i] <= n where n = len(nums) - 1",
        function_name="findDuplicate",
        return_type=INT,
        difficulty="hard",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[1, 3, 4, 2, 2]], "expected_output": 2},
            {"input_data": [[3, 1, 3, 4, 2]], "expected_output": 3},
            {"input_data": [[1, 1, 2]], "expected_output": 1},
        ],
    ),
    _q(
        title="Gas Station",
        description=(
            "There are n gas stations in a circle; gas[i] is fuel gained and cost[i] is cost to reach next. "
            "Return the starting index if you can complete the circuit once, or -1 if impossible."
        ),
        constraints="1 <= gas.length == cost.length <= 10^5\n0 <= gas[i], cost[i] <= 10^4",
        function_name="canCompleteCircuit",
        return_type=INT,
        difficulty="medium",
        parameters=[
            {"name": "gas", "order": 1, "type_schema": INT_ARRAY},
            {"name": "cost", "order": 2, "type_schema": INT_ARRAY},
        ],
        test_cases=[
            {"input_data": [[1, 2, 3, 4, 5], [3, 4, 5, 1, 2]], "expected_output": 3},
            {"input_data": [[2, 3, 4], [3, 4, 3]], "expected_output": -1},
            {"input_data": [[5], [4]], "expected_output": 0},
        ],
    ),
    _q(
        title="Jump Game",
        description=(
            "Given an array nums where nums[i] is your max jump length from index i, "
            "return true if you can reach the last index starting from index 0."
        ),
        constraints="1 <= nums.length <= 10^4\n0 <= nums[i] <= 10^5",
        function_name="canJump",
        return_type=BOOL,
        difficulty="medium",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[2, 3, 1, 1, 4]], "expected_output": True},
            {"input_data": [[3, 2, 1, 0, 4]], "expected_output": False},
            {"input_data": [[0]], "expected_output": True},
        ],
    ),
    _q(
        title="Jump Game II",
        description=(
            "Given an array nums of non-negative integers, you are initially at the first index. "
            "Each element nums[i] represents your maximum jump length at that position. "
            "Return the minimum number of jumps to reach the last index. Assume you can always reach the end."
        ),
        constraints="1 <= nums.length <= 10^4\n0 <= nums[i] <= 1000",
        function_name="jump",
        return_type=INT,
        difficulty="medium",
        parameters=[{"name": "nums", "order": 1, "type_schema": INT_ARRAY}],
        test_cases=[
            {"input_data": [[2, 3, 1, 1, 4]], "expected_output": 2},
            {"input_data": [[2, 3, 0, 1, 4]], "expected_output": 2},
            {"input_data": [[1]], "expected_output": 0},
        ],
    ),
    _q(
        title="Merge Intervals",
        description=(
            "Given an array of intervals where intervals[i] = [start_i, end_i], merge all overlapping "
            "intervals and return non-overlapping intervals sorted by start."
        ),
        constraints="1 <= intervals.length <= 10^4\nintervals[i].length == 2",
        function_name="mergeIntervals",
        return_type=INT_ARRAY_ARRAY,
        difficulty="medium",
        parameters=[{"name": "intervals", "order": 1, "type_schema": INT_ARRAY_ARRAY}],
        test_cases=[
            {
                "input_data": [[[1, 3], [2, 6], [8, 10], [15, 18]]],
                "expected_output": [[1, 6], [8, 10], [15, 18]],
            },
            {"input_data": [[[1, 4], [4, 5]]], "expected_output": [[1, 5]]},
            {"input_data": [[[1, 4], [0, 4]]], "expected_output": [[0, 4]]},
        ],
    ),
    _q(
        title="Insert Interval",
        description=(
            "Given non-overlapping sorted intervals and a new interval, insert newInterval, merging if needed. "
            "Return merged non-overlapping intervals sorted by start."
        ),
        constraints="0 <= intervals.length <= 10^4\nintervals is sorted by start; newInterval.length == 2",
        function_name="insertInterval",
        return_type=INT_ARRAY_ARRAY,
        difficulty="medium",
        parameters=[
            {"name": "intervals", "order": 1, "type_schema": INT_ARRAY_ARRAY},
            {"name": "newInterval", "order": 2, "type_schema": INT_ARRAY},
        ],
        test_cases=[
            {
                "input_data": [[[1, 3], [6, 9]], [2, 5]],
                "expected_output": [[1, 5], [6, 9]],
            },
            {"input_data": [[], [5, 7]], "expected_output": [[5, 7]]},
            {"input_data": [[[1, 5]], [2, 3]], "expected_output": [[1, 5]]},
        ],
    ),
    _q(
        title="Non-overlapping Intervals",
        description=(
            "Given an array of intervals, return the minimum number of intervals you must remove "
            "so that the rest are non-overlapping (touching endpoints is allowed)."
        ),
        constraints="1 <= intervals.length <= 10^5\nintervals[i].length == 2",
        function_name="eraseOverlapIntervals",
        return_type=INT,
        difficulty="medium",
        parameters=[{"name": "intervals", "order": 1, "type_schema": INT_ARRAY_ARRAY}],
        test_cases=[
            {"input_data": [[[1, 2], [2, 3], [3, 4], [1, 3]]], "expected_output": 1},
            {"input_data": [[[1, 2], [1, 2], [1, 2]]], "expected_output": 2},
            {"input_data": [[[1, 2], [2, 3]]], "expected_output": 0},
        ],
    ),
    _q(
        title="Task Scheduler",
        description=(
            "Given a string tasks where each character is a task type, and a non-negative integer n "
            "meaning the same task must be separated by at least n idle slots, return the minimum "
            "number of time units to finish all tasks (each task one unit; idle counts as a unit)."
        ),
        constraints="1 <= tasks.length <= 10^4\n0 <= n <= 100",
        function_name="leastInterval",
        return_type=INT,
        difficulty="medium",
        parameters=[
            {"name": "tasks", "order": 1, "type_schema": STRING},
            {"name": "n", "order": 2, "type_schema": INT},
        ],
        test_cases=[
            {"input_data": ["AAABBB", 2], "expected_output": 8},
            {"input_data": ["A", 2], "expected_output": 1},
            {"input_data": ["AAAAA", 0], "expected_output": 5},
        ],
    ),
    _q(
        title="Kth Largest Element in an Array",
        description=(
            "Given an integer array nums and an integer k, return the kth largest element in the array. "
            "1 <= k <= len(nums) (1-indexed from largest)."
        ),
        constraints="1 <= k <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
        function_name="findKthLargest",
        return_type=INT,
        difficulty="medium",
        parameters=[
            {"name": "nums", "order": 1, "type_schema": INT_ARRAY},
            {"name": "k", "order": 2, "type_schema": INT},
        ],
        test_cases=[
            {"input_data": [[3, 2, 1, 5, 6, 4], 2], "expected_output": 5},
            {"input_data": [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], "expected_output": 4},
            {"input_data": [[1], 1], "expected_output": 1},
        ],
    ),
]


# Daily layouts: list of (day_number, list of question indices into CHALLENGE_QUESTIONS)

# Easy (Low): 1 per day — first 5 problems (indices 0–4), batch-1 warm-up set
EASY_PLAN_DAYS: list[tuple[int, list[int]]] = [
    (i + 1, [i]) for i in range(30)
]


# Medium (Standard): 2 per day — next 10 problems (indices 5–14), rest of batch 1
MEDIUM_PLAN_DAYS: list[tuple[int, list[int]]] = [
(1, [0,1]),
(2, [2,3]),
(3, [4,5]),
(4, [6,7]),
(5, [8,9]),
(6, [10,11]),
(7, [12,13]),
(8, [14,15]),
(9, [16,17]),
(10, [18,19]),
(11, [20,21]),
(12, [22,23]),
(13, [24,25]),
(14, [26,27]),
(15, [28,29]),
(16, [30,31]),
(17, [32,33]),
(18, [34,35]),
(19, [36,37]),
(20, [38,39]),
(21, [40,41]),
(22, [42,43]),
(23, [44,0]),
(24, [1,2]),
(25, [3,4]),
(26, [5,6]),
(27, [7,8]),
(28, [9,10]),
(29, [11,12]),
(30, [13,14])
]


# Hard (Crushing): 3 questions × 15 days = all 45 problems (full curriculum on this track)
HARD_PLAN_DAYS: list[tuple[int, list[int]]] = [
(1, [0,1,2]),
(2, [3,4,5]),
(3, [6,7,8]),
(4, [9,10,11]),
(5, [12,13,14]),
(6, [15,16,17]),
(7, [18,19,20]),
(8, [21,22,23]),
(9, [24,25,26]),
(10, [27,28,29]),
(11, [30,31,32]),
(12, [33,34,35]),
(13, [36,37,38]),
(14, [39,40,41]),
(15, [42,43,44]),
(16, [0,1,2]),
(17, [3,4,5]),
(18, [6,7,8]),
(19, [9,10,11]),
(20, [12,13,14]),
(21, [15,16,17]),
(22, [18,19,20]),
(23, [21,22,23]),
(24, [24,25,26]),
(25, [27,28,29]),
(26, [30,31,32]),
(27, [33,34,35]),
(28, [36,37,38]),
(29, [39,40,41]),
(30, [42,43,44])
]


# common.Difficulty row updates: days and total question count for UI (ceil division = q/day)
DIFFICULTY_DB_FIELDS = {
    "Low": {"days": 30, "number_of_questions": 30},
    "Standard": {"days": 30, "number_of_questions": 60},
    "Crushing": {"days": 30, "number_of_questions": 90},
}
