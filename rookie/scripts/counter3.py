#  pull in the keys
#  see which ones are candidates for merge via jacaard
#  then check the pmis of the jacaard candidates. maybe even a second jacard score for the bag o words on the PMIS terms. if overlap, they're in business.
#  once you have determined that two tokens are aliases, then create a master aliases dictionary. the dict could be aliases[word]=canonical #maybe not filter yet.
#  so like alias['Mitch Landrieus'] = 'Mitch Landrieu'
#  then rerun the counter.py, converting each word to its alias. and converying each word in the window to the alias.
#  This is wasteful interms of system time, but there is too much to keep track of w/ the multiple passes