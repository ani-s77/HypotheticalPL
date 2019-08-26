import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
desired_width = 320
pd.set_option('display.width', desired_width)

# use creds to create a client to interact with the Google Drive API
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/Anirudh/PycharmProjects/soccer/client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Hypothetical PL 2").sheet1
s2 = client.open("Hypothetical PL 2").worksheet("Fixtures")


# Reads player names, FIFA ratings, set piece takers, and tactics from a file
def read_players(file_path):
    teams_map = {"mci": 0, "liv": 1, "che": 2, "tot": 3, "ars": 4, "mun": 5, "wol": 6, "eve": 7, "lei": 8, "whu": 9,
                 "wat": 10, "cry": 11, "new": 12, "bou": 13, "bur": 14, "sou": 15, "shu": 16, "bha": 17, "lee": 18,
                 "for": 19, "c": 20, "1": 21, "2": 22, "n": 23, "t": 24, "g": 25, "cl": 26, "el": 27, "bar": 28,
                 "rma": 29, "juv": 30, "atm": 31, "fcb": 32, "bvb": 33, "int": 34, "psg": 35, "ol": 36}
    col = (teams_map[file_path] + 1) * 2
    count = 0
    team_name = "Team"
    num_defs = 4
    pk_taker = 10
    fk_taker = 7
    tactics = 1
    ratings = []
    player_names = []
    v1 = sheet.col_values(col)
    v2 = sheet.col_values(col + 1)
    while count < 19:
        if count == 0:
            team_name = v1[1]
        elif count < 15:
            player_names.append(v1[1 + count])
            ratings.append(int(v2[1 + count]))
        elif count == 15:
            num_defs = int(v1[16])
        elif count == 16:
            pk_taker = int(v1[17]) - 3
        elif count == 17:
            fk_taker = int(v1[18]) - 3
        else:
            tactics = int(v1[19])
        count += 1
    if tactics == 0:
        tactics = 1
    return team_name, num_defs, pk_taker, fk_taker, tactics, ratings, player_names


# Gets the scoreline when given the FIFA ratings and tactics
def get_scoreline(home_fifa_ratings, away_fifa_ratings, home_tactics, away_tactics):

    home_total_fifa_rating = int(0)
    away_total_fifa_rating = int(0)

    # Finds the total team rating as the sum of all starter ratings + half the sum of all sub ratings
    for i in range(0, 11):
        home_total_fifa_rating += int(home_fifa_ratings[i])
        away_total_fifa_rating += int(away_fifa_ratings[i])
    for i in range(11, 14):
        home_total_fifa_rating += (int(home_fifa_ratings[i]) // 2)
        away_total_fifa_rating += (int(away_fifa_ratings[i]) // 2)

    # Sets the home advantage
    #home_total_fifa_rating += 33

    # Sets tactical advantages
    if home_tactics < 7 and away_tactics < 7:
        home_tactics %= 3
        away_tactics %= 3
        if (home_tactics - away_tactics) % 3 == 1:
            home_total_fifa_rating += 33
        if (home_tactics - away_tactics) % 3 == 2:
            away_total_fifa_rating += 33

    # Finds the scoreline using the team ratings and probability of each scoreline
    goal_probs = []
    fifa_rating_difference = abs(home_total_fifa_rating - away_total_fifa_rating)
    if fifa_rating_difference < 20:
        goal_probs.append([50, 150, 215, 220, 222, 223])
        goal_probs.append([323, 483, 583, 603, 608, 609])
        goal_probs.append([674, 774, 879, 904, 909, 911])
        goal_probs.append([916, 936, 961, 967, 971, 973])
        goal_probs.append([975, 980, 985, 989, 991, 992])
        goal_probs.append([993, 994, 996, 998, 999, 1000])
    elif fifa_rating_difference < 50:
        goal_probs.append([20, 130, 230, 275, 278, 280])
        goal_probs.append([355, 505, 655, 705, 708, 710])
        goal_probs.append([715, 800, 880, 900, 905, 908])
        goal_probs.append([913, 933, 943, 991, 995, 997])
        goal_probs.append([997, 997, 997, 997, 999, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])
    elif fifa_rating_difference < 80:
        goal_probs.append([73, 193, 313, 413, 423, 428])
        goal_probs.append([476, 574, 674, 814, 822, 826])
        goal_probs.append([831, 871, 919, 944, 954, 956])
        goal_probs.append([958, 963, 988, 994, 998, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])
    else:
        goal_probs.append([50, 170, 320, 395, 445, 455])
        goal_probs.append([480, 563, 663, 813, 888, 898])
        goal_probs.append([900, 920, 934, 959, 978, 988])
        goal_probs.append([988, 989, 991, 994, 998, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])

    higher_rated_team_goals = 0
    lower_rated_team_goals = 0
    rnd = random.randint(0, 1000)
    i = 0
    while i < 6:
        j = 0
        while j < 6:
            if rnd < goal_probs[i][j]:
                higher_rated_team_goals = j
                lower_rated_team_goals = i
                i = 6
                j = 6
            j += 1
        i += 1
    if home_total_fifa_rating >= away_total_fifa_rating:
        home_goals = higher_rated_team_goals
        away_goals = lower_rated_team_goals
    else:
        home_goals = lower_rated_team_goals
        away_goals = higher_rated_team_goals

    if home_total_fifa_rating / 12 < 70.0:
        rdm = random.randint(0, 10)
        if rdm < 5:
            away_goals += 3
    if away_total_fifa_rating / 12 < 70.0:
        rdm = random.randint(0, 10)
        if rdm < 5:
            home_goals += 3

    # Changes number of goals for bus parking and all out attack
    random_limit = home_total_fifa_rating + away_total_fifa_rating - 33
    if home_tactics == 7 or away_tactics == 7:
        rdm = random.randint(0, random_limit)
        if rdm < home_total_fifa_rating:
            home_goals -= 2
            if home_goals < 0:
                home_goals = 0
        rdm = random.randint(0, random_limit)
        if rdm < away_total_fifa_rating:
            away_goals -= 2
            if away_goals < 0:
                away_goals = 0

    if home_tactics == 8 or away_tactics == 8:
        rdm = random.randint(0, random_limit)
        if rdm < home_total_fifa_rating:
            home_goals += 2
        rdm = random.randint(0, random_limit)
        if rdm < away_total_fifa_rating:
            away_goals += 2

    return home_goals, away_goals


def get_ratings(goal_data, num_conceded, num_defs):

    ratings = []
    fpl_points = []
    num_scored = len(goal_data[0])
    max_mid = 7 + (num_defs % 2)

    for i in range(0, 14):
        fpl_points.append(0)

    for i in range(0, 14):
        if i < max_mid:
            fpl_points[i] -= int(num_conceded // 2)
        elif i < 11:
            fpl_points[i] += int(num_scored // 2)

    for i in goal_data[0]:
        if i < max_mid:
            fpl_points[i] += 6
        elif i == 10:
            fpl_points[i] += 4
        elif i < 14:
            fpl_points[i] += 5

    for i in goal_data[1]:
        fpl_points[i] += 3

    if num_conceded == 0:
        for i in range(0, max_mid):
            fpl_points[i] += 4

    if num_scored == 0:
        for i in range(max_mid, 11):
            fpl_points[i] -= 3

    rnd = random.randint(0, 11)
    fpl_points[0] += (rnd - 5)

    for i in range(1, 14):
        rnd = random.randint(0, 7)
        if fpl_points[i] < 8:
            fpl_points[i] += (rnd - 3)
        else:
            fpl_points[i] += (rnd // 2)

    for i in range(0, 14):

        if fpl_points[i] >= 0:
            fpl_points[i] = int(10 + (2.0 * fpl_points[i] / 3.0))
        else:
            fpl_points[i] = int(10 + (4.0 * fpl_points[i] / 3.0))

        player_rating = fpl_points[i] / 2.0

        if num_scored != num_conceded:
            player_rating += (num_scored - num_conceded) / abs(num_scored - num_conceded)

        if player_rating < 0:
            player_rating = 0.0
        if player_rating > 10:
            player_rating = 10.0

        ratings.append(player_rating)

    return ratings


# Determines scorers, assisters, and minutes
def determine_goal_data(fifa_ratings, num_defs, num_scored):

    max_def = num_defs + 1
    max_mid = 7 + (num_defs % 2)

    adj_ratings = [0]
    for i in fifa_ratings[1:max_def]:
        adj_ratings.append(2 * int(i))
    for i in fifa_ratings[max_def:max_mid]:
        adj_ratings.append(int(i))
    for i in fifa_ratings[max_mid:10]:
        adj_ratings.append(8 * int(i))
    adj_ratings.append(10 * int(fifa_ratings[10]))
    for i in fifa_ratings[11:14]:
        adj_ratings.append(int(i))

    prob_bins = [0]
    for i in adj_ratings[1:]:
        prob_bins.append(int(prob_bins[-1]) + int(i))

    goal_data = []
    scorers = []

    for i in range(0, num_scored):
        rnd = random.randint(0, prob_bins[13])
        j = 0
        while j < 14:
            if rnd < prob_bins[j]:
                rnd_diff = random.randint(0, 20)
                if rnd_diff < 2:
                    scorers.append(14)
                elif rnd_diff == 2:
                    rnd_og = random.randint(0, 7)
                    scorers.append(16 + int(rnd_og))
                elif rnd_diff == 3:
                    scorers.append(15)
                else:
                    scorers.append(int(j))
                j = 14
            j += 1

    goal_data.append(scorers)

    adj_ratings = [50]
    if num_defs == 3:
        for i in fifa_ratings[1:4]:
            adj_ratings.append(int(i))
        for i in fifa_ratings[4:6]:
            adj_ratings.append(8 * int(i))
        for i in fifa_ratings[6:8]:
            adj_ratings.append(int(i))
    else:
        for i in fifa_ratings[1:3]:
            adj_ratings.append(5 * int(i))
        for i in fifa_ratings[3:max_def]:
            adj_ratings.append(int(i))
        for i in fifa_ratings[max_def:max_mid]:
            adj_ratings.append(3 * int(i))
    for i in fifa_ratings[max_mid:10]:
        adj_ratings.append(10 * int(i))
    adj_ratings.append(7 * int(fifa_ratings[10]))
    for i in fifa_ratings[11:14]:
        adj_ratings.append(int(i))

    prob_bins = [50]
    for i in adj_ratings[1:]:
        prob_bins.append(int(prob_bins[-1]) + int(i))

    assisters = []
    for i in range(0, num_scored):
        rnd = random.randint(0, prob_bins[13])
        j = 0
        while j < 14:
            if rnd < prob_bins[j]:
                assisters.append(int(j))
                j = 14
            j += 1

    goal_data.append(assisters)

    minutes = []
    for i in range(0, len(goal_data[0])):
        rnd = random.randint(0, 94) + 1
        if 10 < goal_data[0][i] < 14 or goal_data[1][i] > 10:
            rnd = random.randint(0, 30) + 64
        minutes.append(rnd)

    goal_data.append(minutes)

    if num_scored > 1:
        for i in range(0, len(goal_data[0]) - 1):
            for j in range(0, len(goal_data[0]) - i - 1):
                if goal_data[2][j] > goal_data[2][j + 1]:
                    for k in range(0, 3):
                        goal_data[k][j], goal_data[k][j + 1] = goal_data[k][j + 1], goal_data[k][j]

    return goal_data


def get_motm_and_dotm(names_1, names_2, ratings_1, ratings_2):

    ratings_data = []
    for i in range(0, 14):
        ratings_data.append((ratings_1[i], names_1[i]))
        ratings_data.append((ratings_2[i], names_2[i]))
    random.shuffle(ratings_data)

    motm = max(ratings_data)
    dotm = min(ratings_data)
    if motm == dotm:
        dotm = min(ratings_data[:-1])

    return motm[1], dotm[1]


def show_result(goal_data, player_names, opp_player_names, pk_taker, fk_taker):
    goal_string = ""
    for i in range(0, len(goal_data[0])):
        goal_type = ""
        if goal_data[0][i] == 14:
            goal_data[0][i] = pk_taker
            goal_string += (player_names[pk_taker] + " (p, ")
            if random.randint(0, 2) == 1:
                goal_type = " [VAR]"
        elif goal_data[0][i] == 15:
            goal_data[0][i] = fk_taker
            goal_string += (player_names[fk_taker] + " (fk, ")
        elif goal_data[0][i] > 15:
            goal_string += opp_player_names[goal_data[0][i] - 16]
            goal_string += (" (og), off " + player_names[goal_data[1][i]] + " (")
        else:
            goal_string += player_names[goal_data[0][i]]
            if goal_data[0][i] == goal_data[1][i]:
                goal_string += " ("
            else:
                goal_string += (", a " + player_names[goal_data[1][i]] + " (")
            if random.randint(0, 20) == 2:
                goal_type = " [BANGER]"
        minute = goal_data[2][i]
        if minute <= 45:
            goal_string += (str(minute) + "')" + goal_type + "\n")
        elif minute <= 48:
            goal_string += ("45+" + str(minute - 45) + "')" + goal_type + "\n")
        elif minute <= 93:
            goal_string += (str(minute - 3) + "')" + goal_type + "\n")
        else:
            goal_string += ("90+" + str(minute - 93) + "')" + goal_type + "\n")
    return goal_string


def penalties():
    home_score = 0
    away_score = 0
    home_left = 5
    away_left = 5
    while away_left > 0:
        rnd = random.randint(0, 5)
        if rnd != 4:
            home_score += 1
        home_left -= 1
        if home_score > away_score + away_left:
            return home_score, away_score
        if away_score > home_score + home_left:
            return home_score, away_score
        rnd = random.randint(0, 5)
        if rnd != 4:
            away_score += 1
        away_left -= 1
        if home_score > away_score + away_left:
            return home_score, away_score
        if away_score > home_score + home_left:
            return home_score, away_score
    while 0 == 0:
        rnd_1 = random.randint(0, 3)
        rnd_2 = random.randint(0, 3)
        if rnd_1 != 2:
            home_score += 1
        if rnd_2 != 2:
            away_score += 1
        if home_score != away_score:
            return home_score, away_score


def play(team_1, team_2, cup):

    home_short_name = team_1
    away_short_name = team_2
    home_file_path = home_short_name
    away_file_path = away_short_name
    home_name, home_defs, home_pk_taker, home_fk_taker, home_tactics, home_fifa_ratings, home_player_names = \
        read_players(home_file_path)
    away_name, away_defs, away_pk_taker, away_fk_taker, away_tactics, away_fifa_ratings, away_player_names = \
        read_players(away_file_path)

    home_goals, away_goals = get_scoreline(home_fifa_ratings, away_fifa_ratings, home_tactics, away_tactics)

    home_goal_data = determine_goal_data(home_fifa_ratings, home_defs, home_goals)
    away_goal_data = determine_goal_data(away_fifa_ratings, away_defs, away_goals)

    pen_score = ""
    if cup == 1 and home_goals == away_goals:
        home_pens, away_pens = penalties()
        pen_score = "(" + str(home_pens) + "-" + str(away_pens) + " p) "

    result = home_name + " " + str(home_goals) + "-" + str(away_goals) + " " + pen_score + away_name + "\n" + "\n"
    result += (show_result(home_goal_data, home_player_names, away_player_names, home_pk_taker, home_fk_taker))
    if home_goals != 0:
        result += "\n"
    result += (show_result(away_goal_data, away_player_names, home_player_names, away_pk_taker, away_fk_taker))
    if away_goals != 0:
        result += "\n"

    home_player_ratings = get_ratings(home_goal_data, away_goals, home_defs)
    away_player_ratings = get_ratings(away_goal_data, home_goals, away_defs)
    # Prints player ratings
    for i in range(0, 14):
        result += (str.ljust(home_player_names[i] + ": " + str(round(home_player_ratings[i], 1)), 25) +
                   str.ljust(away_player_names[i] + ": " + str(round(away_player_ratings[i], 1)), 25) + "\n")
    motm, dotm = get_motm_and_dotm(home_player_names, away_player_names, home_player_ratings, away_player_ratings)
    result += ("Man of the match: " + motm + "\nDonkey of the match: " + dotm + "\n\n")

    return result, home_goal_data, away_goal_data, home_player_names, away_player_names, home_player_ratings, \
        away_player_ratings, motm, dotm


def fixtures(teams):
    n = len(teams)
    matches = []
    all_fixtures = []
    return_matches = []
    for fixture in range(1, n):
        for i in range(n // 2):
            matches.append((teams[i], teams[n - 1 - i]))
            return_matches.append((teams[n - 1 - i], teams[i]))
        teams.insert(1, teams.pop())
        all_fixtures.insert(len(all_fixtures) // 2, matches)
        all_fixtures.append(return_matches)
        matches = []
        return_matches = []
    return all_fixtures


def play_league(team_list):

    if len(team_list) % 2 != 0:
        exit(2)

    matches = fixtures(team_list)
    table = {}
    team_data = {}

    for team in team_list:
        team_name, _, _, _, _, _, player_names = read_players(team)
        table[team] = [team_name, 0, 0, 0, 0, 0, 0, 0, 0]
        player_data = []
        for name in player_names:
            player_data.append([name, 0, 0, 0.0])
        team_data[team] = player_data

    count = 1
    for gameweek in matches:
        print("Gameweek " + str(int(count)))
        count += 1
        for game in gameweek:
            print(game[0] + " vs " + game[1])
            result, hgd, agd, _, _, hpr, apr, _, _ = play(game[0], game[1], 0)
            print(result)
            hg = len(hgd[0])
            ag = len(agd[0])
            if hg > ag:
                table[game[0]][2] += 1
                table[game[1]][4] += 1
            elif ag > hg:
                table[game[1]][2] += 1
                table[game[0]][4] += 1
            else:
                table[game[0]][3] += 1
                table[game[1]][3] += 1
            table[game[0]][6] += hg
            table[game[1]][7] += hg
            table[game[0]][7] += ag
            table[game[1]][6] += ag
            for team in game:
                table[team][1] += 1
                table[team][5] = (3 * table[team][2]) + table[team][3]
                table[team][8] = table[team][6] - table[team][7]

            for i in range(0, len(hgd[0])):
                if hgd[0][i] < 14:
                    scorer = hgd[0][i]
                    team_data[game[0]][scorer][1] += 1
            for i in range(0, len(agd[0])):
                if agd[0][i] < 14:
                    scorer = agd[0][i]
                    team_data[game[1]][scorer][1] += 1
            for i in range(0, len(hgd[0])):
                assister = hgd[1][i]
                team_data[game[0]][assister][2] += 1
            for i in range(0, len(agd[0])):
                if agd[0][i] < 14:
                    assister = agd[1][i]
                    team_data[game[1]][assister][2] += 1
            for i in range(0, 14):
                team_data[game[0]][i][3] += hpr[i]
                team_data[game[1]][i][3] += apr[i]

    final_table = []
    for key in table:
        final_table.append(table[key])

    for i in range(0, len(final_table) - 1):
        for j in range(0, len(final_table) - i - 1):
            if final_table[j][5] < final_table[j + 1][5]:
                final_table[j], final_table[j + 1] = final_table[j + 1], final_table[j]

    print("{:<25}".format("TEAM") + "{:>4}".format("P") + "{:>4}".format("W") + "{:>4}".format("D") +
          "{:>4}".format("L") + "{:>4}".format("Pts") + "{:>4}".format("GF") + "{:>4}".format("GA") +
          "{:>4}".format("GD"))
    for i in final_table:
        print("{:<25}".format(i[0]) + "{:>4}".format(i[1]) + "{:>4}".format(i[2]) + "{:>4}".format(i[3]) +
              "{:>4}".format(i[4]) + "{:>4}".format(i[5]) + "{:>4}".format(i[6]) + "{:>4}".format(i[7]) +
              "{:>4}".format(i[8]))

    high_scores = []
    high_assists = []
    ratings = []
    for key in team_data:
        for player in team_data[key]:
            if player[1] > 0:
                high_scores.append((player[1], player[0]))
            if player[2] > 0:
                high_assists.append((player[2], player[0]))
            ratings.append((round(player[3] / (2 * (len(team_list) - 1)), 1), player[0]))

    high_scores.sort(reverse=True)
    high_assists.sort(reverse=True)
    ratings.sort(reverse=True)

    print("\nHIGH SCORERS")
    for score in high_scores[:5]:
        print(str(score[1]) + ": " + str(score[0]))
    print("\nHIGH ASSISTS")
    for assist in high_assists[:5]:
        print(str(assist[1]) + ": " + str(assist[0]))
    print("\nHIGHEST RATED PLAYERS")
    for rating in ratings[:15]:
        print(str(rating[1]) + ": " + str(rating[0]))


def play_games(teams, cup):
    if len(teams) % 2 != 0:
        exit(2)
    for i in range(0, len(teams) // 2):
        print(play(teams[2 * i], teams[2 * i + 1], cup)[0])


def play_week(teams):
    play_games(teams, 0)


def play_cup_round(teams):
    play_games(teams, 1)


string = "eve rma eve rma eve rma eve rma new eve new eve new eve whu tot"
playing_teams = string.split()
#random.shuffle(playing_teams)
play_cup_round(playing_teams)
