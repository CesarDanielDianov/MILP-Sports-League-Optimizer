import sys

from pulp import (
    LpInteger,
    LpMinimize,
    LpProblem,
    LpStatusOptimal,
    LpVariable,
    PULP_CBC_CMD,
    lpSum,
    value,
)


def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return

    values = iter(map(int, data))

    try:
        n_teams = next(values)
        n_played = next(values)
    except StopIteration:
        return

    current_points = [0] * n_teams

    # Initially every pair of teams still has two matches to play.
    remaining_games = {
        (i, j): 2
        for i in range(n_teams)
        for j in range(i + 1, n_teams)
    }

    # Process completed matches.
    for _ in range(n_played):
        try:
            team1 = next(values) - 1
            team2 = next(values) - 1
            result = next(values)
        except StopIteration:
            break

        pair = (team1, team2) if team1 < team2 else (team2, team1)

        if pair in remaining_games:
            remaining_games[pair] = max(0, remaining_games[pair] - 1)

        if result == 0:
            current_points[team1] += 1
            current_points[team2] += 1
        elif result == team1 + 1:
            current_points[team1] += 3
        elif result == team2 + 1:
            current_points[team2] += 3

    remaining_matches = [
        (pair, count)
        for pair, count in remaining_games.items()
        if count > 0
    ]

    wins_vars = {}
    draw_vars = {}

    base_constraints = []
    future_points = [[] for _ in range(n_teams)]
    matches_by_team = [[] for _ in range(n_teams)]

    # Create variables describing every remaining matchup.
    for (i, j), count in remaining_matches:

        wins = LpVariable(f"w_{i}_{j}", 0, count, LpInteger)
        draws = LpVariable(f"d_{i}_{j}", 0, count, LpInteger)

        wins_vars[(i, j)] = wins
        draw_vars[(i, j)] = draws

        # wins + draws <= count
        # The remaining matches are victories for team j.
        base_constraints.append(wins + draws <= count)

        future_points[i].append(3 * wins + draws)
        future_points[j].append(3 * (count - wins - draws) + draws)

        matches_by_team[i].append((j, (i, j)))
        matches_by_team[j].append((i, (i, j)))

    solver = PULP_CBC_CMD(msg=0, presolve=True, threads=0)

    total_points = [
        current_points[i] + lpSum(future_points[i])
        for i in range(n_teams)
    ]

    remaining_by_team = [
        sum(remaining_games[pair] for _, pair in matches_by_team[i])
        for i in range(n_teams)
    ]

    for target in range(n_teams):

        problem = LpProblem("Projeto3", LpMinimize)

        for constraint in base_constraints:
            problem += constraint

        target_win_terms = []

        # Force the target team to win whenever possible.
        for _, pair in matches_by_team[target]:

            wins = wins_vars[pair]
            draws = draw_vars[pair]
            count = remaining_games[pair]

            if target == pair[0]:
                problem += wins + draws == count
                target_win_terms.append(wins)
            else:
                problem += wins == 0
                target_win_terms.append(count - wins - draws)

        target_wins = lpSum(target_win_terms)

        # Every remaining match guarantees one point (draw).
        # Each win replaces that draw with three points (+2).
        target_points = (
            current_points[target]
            + remaining_by_team[target]
            + 2 * target_wins
        )

        # No other team may finish above the target.
        for opponent in range(n_teams):
            if opponent != target:
                problem += total_points[opponent] <= target_points

        problem += target_wins

        status = problem.solve(solver)

        if status == LpStatusOptimal:
            print(int(value(target_wins)))
        else:
            print(-1)


if __name__ == "__main__":
    main()
