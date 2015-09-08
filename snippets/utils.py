import random

def flip(*regions):
    '''
    Each region is a float representing
    some part of an overall probability space
    '''
    running_total = 0.
    sum_regions = sum(regions)
    region_boundries = []
    for region in regions:
    	assert type(region) is float
        old_total = running_total
        new_total = running_total + region
        region_boundries.append((old_total, new_total))
        running_total = new_total

    flip = random.uniform(0, sum_regions)
    for i in range(0, len(region_boundries)):
        win_zone = region_boundries[i]
        if flip >= win_zone[0] and flip <= win_zone[1]:
            return i
