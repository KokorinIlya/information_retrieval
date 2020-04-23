from spellcheck.editorial_actions import Match, Replacement, Removal, Insertion


def calc_distance(from_string, to_string):
    n = len(from_string)
    m = len(to_string)

    dp = [
        [
            j if i == 0 else i if j == 0 else 0
            for j in range(m + 1)
        ]
        for i in range(n + 1)
    ]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if from_string[i - 1] == to_string[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + 1)

    result = dp[n][m]
    i, j = n, m
    editorial_actions = []
    while i > 0 and j > 0:
        from_char = from_string[i - 1]
        to_char = to_string[j - 1]
        if from_char == to_char:
            editorial_actions.append(Match(from_char))
            i -= 1
            j -= 1
        else:
            min_cost = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + 1)
            if dp[i - 1][j] + 1 == min_cost:
                editorial_actions.append(Removal(from_char))
                i -= 1
            elif dp[i][j - 1] + 1 == min_cost:
                editorial_actions.append(Insertion(to_char))
                j -= 1
            else:
                editorial_actions.append(Replacement(from_char, to_char))
                i -= 1
                j -= 1
    return result, list(reversed(editorial_actions))
