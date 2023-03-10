import gspread
from random import choice
import os

credentials = {
    "type": os.environ["type"],
    "project_id": os.environ["project_id"],
    "private_key_id": os.environ["private_key_id"],
    "private_key": os.environ["private_key"],
    "client_email": os.environ["client_email"],
    "auth_uri": os.environ["auth_uri"],
    "token_uri": os.environ["token_uri"],
    "auth_provider_x509_cert_url": os.environ["auth_provider_x509_cert_url"],
    "client_x509_cert_url": os.environ["client_x509_cert_url"]
}

credentials["private_key"] = credentials["private_key"].replace("\\n", "\n")

gc = gspread.service_account_from_dict(credentials)
sh = gc.open("team_picker")


def pick_teams():
    """Picks the fairest two teams possible and writes them to the sheet"""
    try:
        # this length determines how many weeks of football have already been played
        l = len(sh.sheet1.get('C26:Z26')[0])

        # creates a dictionary of every player and their latest score
        scores = {players[0]: players[-1] for players in sh.get_worksheet(1).get(f"A2:Z100")}

        # creates a list of all previous team combinations
        prev_teams = [{player[0] for player in sh.sheet1.get(f"{cap(i, 2)}{14 + j}:{cap(i, 2)}{19 + j}")
                       if player != []} for i in range(1, l + 1) for j in range(0, 7, 6)]

        # creates the pool of players and another list of their respective scores
        pool = [player[-1] for player in sh.sheet1.get(f"{cap(l, 3)}2:{chr(ord('@') + (l + 3))}13")]
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
        sh.sheet1.update(f"{cap(l, 3)}14:{cap(l, 3)}25", output if n != 12 else team1 + team2)
    except Exception as e:
        print(e)


def cap(l, n):
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