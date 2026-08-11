"""StableMarriages"""
#
# StableMarriages.py
#
# @author Alexandros Lattas
#
# created with Spyder
#

#Imports

import sys
import json

#Input
#Arguments:
# 1. python3 stable_marriage.py -m <input_filename>
# 2. python3 stable_marriage.py -m <input_filename> -o <output_filename>
# 3. python3 stable_marriage.py -w <input_filename>
# 4. python3 stable_marriage.py -w <input_filename> -o <output_filename>

def get_husband(woman, couples):
    """Finds the Husband of an engaged woman"""
    for man in couples:
        if couples[man] == woman:
            return man

#json output name
if len(sys.argv) == 3:
    OUTPUTFILENAME = 'stable_marriage_results.json'
elif len(sys.argv) == 5:
    if not sys.argv[4].endswith('.json'):
        print('Wrong output filename:')
        print('Should be a .json file.')
        sys.exit(0)
    OUTPUTFILENAME = sys.argv[4]
else:
    print('Wrong Arguments.')
    print('Available Argumnets:')
    print('1. python3 stable_marriage.py -m <input_filename>')
    print('2. python3 stable_marriage.py -m <input_filename> -o <output_filename>')
    print('3. python3 stable_marriage.py -w <input_filename>')
    print('4. python3 stable_marriage.py -w <input_filename> -o <output_filename>')
    sys.exit(0)

#json file import

with open(sys.argv[2]) as json_file:
    JSON_DATA = json.loads(json_file.read())

json_file.close()
#initializations

if sys.argv[1] == '-m':
    FIRST_TO_CHOOSE = 'men_rankings'
    SECOND_TO_CHOOSE = 'women_rankings'
elif sys.argv[1] == '-w':
    FIRST_TO_CHOOSE = 'women_rankings'
    SECOND_TO_CHOOSE = 'men_rankings'
else:
    print('Wrong Arguments:')
    print('Second Argument should be either -m or -w')
    sys.exit(0)


def GS(DATA, FIRST, SEC):
    """Finds a stable marriage with Gale-Shapley Algorithm"""
    COUPLESNO = len(DATA[FIRST])
    couples = {}
    engagedF = {}
    engagedS = {}
    for name in DATA[FIRST]:
        engagedF[name] = 0
    for name in DATA[SEC]:
        engagedS[name] = 0


    stable = 1
    while len(couples) < COUPLESNO or not stable:
        stable = 1
        for name in DATA[FIRST]:
            if not engagedF[name]:
                w = DATA[FIRST][name][0]
                DATA[FIRST][name].pop(0)
                if not engagedS[w]:
                    couples[name] = w
                    engagedS[w] = 1
                    engagedF[name] = 1
                else:
                    mm = get_husband(w, couples)
                    if DATA[SEC][w].index(name) < DATA[SEC][w].index(mm):
                        stable = 0
                        couples[name] = w
                        del couples[mm]
                        engagedF[name] = 1
                        engagedF[mm] = 0

    return couples

#output
with open(OUTPUTFILENAME, 'w') as outfile:
    json.dump(GS(JSON_DATA, FIRST_TO_CHOOSE, SECOND_TO_CHOOSE), outfile, sort_keys=True)

print('done')

    