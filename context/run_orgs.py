import pdb
import collections
from rookie.utils import get_pickled

windows = get_pickled("pickled/org_windows.p")

for key in windows.keys():
    itemz = collections.Counter(windows[key]).items()
    print key, itemz
