import pickle
import json
import glob
from rookie.classes import N_Grammer

TO_PROCESS = glob.glob('/Volumes/USB 1/lens_processed/*')

if __name__ == "__main__":
    for process_file in TO_PROCESS:
        try:
            with open(process_file, 'r') as processed:
                data = json.load(processed)
                s = data['lines']['sentences']
            ng = N_Grammer(data)
#        except ValueError:
#            pass
        except KeyError:
            pass
# with open("data/windows.p", "r") as picklefile:
#     windows = pickle.load(picklefile)
