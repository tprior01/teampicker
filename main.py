import gspread
from numpy import array
from random import choice

gc = gspread.service_account()
sh = gc.open("team_picker")


def pick_teams():
    """Picks the fairest two teams possible and writes them to the sheet"""
    try:
        # this length determines how many weeks of football have already been played
        l = len(sh.get_worksheet(0).get('C26:Z26')[0])

        # creates a dictionary of every player and their latest score
        scores = {players[0]: players[-1] for players in sh.get_worksheet(1).get(f"A2:Z100")}

        # creates a list of all previous team combinations
        prev_teams = array(sh.get_worksheet(0).get(f"C14:{letter(l, 2)}25"))
        prev_teams = [set(prev_teams[0+j:6+j, i]) for j in range(0, 7, 6) for i in range(len(prev_teams[0]))]

        # creates the pool of players and another list of their respective scores
        pool = [player[-1] for player in sh.get_worksheet(0).get(f"{letter(l, 3)}2:{chr(ord('@')+(l + 3))}13")]
        pool_scores = [float(scores[player[-1]]) for player in sh.get_worksheet(0).get('C2:Z13')]

        # the number of players must be a multiple of 2
        n = len(pool)
        if n % 2 != 0:
            return

        # a list of every unique binary number with n bits and n/2 0's an 1's
        options = [f"{i:b}" for i in range(max_bits(n - 1), 2 ** n) if f"{i:b}".count("1") == n / 2]

        # the abs difference between the combined score of team1 and team2, using this to parse the options
        scores = [round(abs(sum([pool_scores[i] for i in range(n) if bit[i] == "1"]) -
                            sum([pool_scores[i] for i in range(n) if bit[i] == "0"])), 1) for bit in options]
        parsed = [options[i] for i in range(len(options)) if scores[i] == min(scores)]

        # the amount of times two players on the same team have played together before, using this to parse the options
        counts = [round(count_combos(team, 0, pool, prev_teams) +
                        count_combos(team, 1, pool, prev_teams), 1) for team in parsed]
        parsed = [parsed[i] for i in range(len(counts)) if counts[i] == min(counts)]

        # writes a random choice of teams to the sheet
        teams = choice(parsed)
        team1 = [[pool[i]] for i, bit in enumerate(teams) if bit == "0"]
        team2 = [[pool[i]] for i, bit in enumerate(teams) if bit == "1"]
        output = team1 + [[""]] * int((12 % n) / 2) + team2 + [[""]] * int((12 % n) / 2) if n != 12 else team1 + team2
        sh.get_worksheet(0).update(f"{letter(l, 3)}14:{letter(l, 3)}25", output if n != 12 else team1 + team2)
    except Exception as e:
        print(e)




def letter(l, n):
    """Returns the capital of the lth + nth letter in the alphabet"""
    return chr(ord('@')+(l + n))


def max_bits(b):
    """Returns the largest decimal number for a given bit length"""
    return (1 << b) - 1


def count_combos(teams, bit, pool, prev_teams):
    """Returns the amount of times two players on the same team have played together before, with more recent matches
    weighted higher (prev_teams must be ordered with less recent teams first)"""
    count = 0
    for i, bit_i in enumerate(teams):
        for j, bit_j in enumerate(teams):
            if i == j:
                continue
            else:
                if bit_i == str(bit) and bit_j == str(bit):
                    for k, team in enumerate(prev_teams):
                        if pool[i] in team and pool[j] in team:
                            count += 1 + k / 10
    return count


def main():
    pick_teams()


if __name__ == '__main__':
    main()