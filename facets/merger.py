'''
Merge NPs
'''

THRESHOLD = .7

DEBUG = True

def debug_print(*args):
    if DEBUG:
        print "\t".join(args)


def find_canonical(a, b, counter):
    '''for now just take the longer one'''
    out = a if len(a.split()) > len(b.split()) else b
    return out


def language_p(a, b, counter):
    '''
    p(shorter) / p(longer)
    '''
    assert len(a.split()) + 1 == len(b.split())
    numerator = [o[1] for o in counter if o[0] == a].pop()
    denominator = [o[1] for o in counter if o[0] == b].pop()
    return numerator/denominator


def is_split_facet(a, b):
    # Mayor Mitch, Mitch Landrieu
    if a.split()[len(a.split()) - 1] == a.split()[0]:
        return True
    # Mitch Landrieu, Landrieu Administration
    elif b.split()[len(b.split()) - 1] == a.split()[0]:
        return True
    return False


def join_split_facet(a, b):
    '''ex input: Mayor Mitch, Mitch Landrieu'''
    if a.split()[len(a.split()) - 1] == b.split()[0]:
        return a + " " + " ".join(b.split()[1:])
    # Mitch Landrieu, Landrieu Administration
    elif b.split()[len(b.split()) - 1] == a.split()[0]:
        return b + " " + " ".join(a.split()[1:])
    else:
        assert "this should" == "not fire"


def should_go_in_old(candidate, current_cluster, counter):
    '''old: should candidate go into this cluster? uses probs '''
    for term in current_cluster:
        shorter = min([term, candidate], key=lambda k: len(k.split(" ")))
        longer = [i for i in [term, candidate] if i != shorter].pop()
        if len(shorter.split()) + 1 == len(longer.split()) and shorter in longer:
            similarity = language_p(shorter, longer, counter)
            if similarity > THRESHOLD:
                report = "candidates \t {} \t {} \t {}".format(shorter, longer, similarity)
                debug_print(report)
                return True
                # for overlapping facets
            elif is_split_facet(shorter, longer):
                debug_print("split facet", shorter, longer)
                joined = join_split_facet(shorter, longer)
                joined_c = sum(c[1] for c in counter if c[0] == joined)
                if joined_c > 0:
                    similarity = language_p(longer, joined, counter)
                    if similarity > THRESHOLD:
                        return True
    return False


def should_go_in(candidate, current_cluster):
    '''should candidate go into this cluster?'''
    for term in current_cluster:
        if candidate in term or term in candidate:
            return True
        if candidate == term:
            return True
    return False


def coronate(terms):
    '''go forth and represent yr cluster'''
    return max(terms, key=lambda x:len(x))# TODO


def merge_terms(counter, n):
    '''
    simple merging cluster algorithm

    input = list of terms

    output = list of top N terms, merged

    '''
    cluster_list = [] # a list of clusters
    cluster_list.append([counter[0]])
    tracker = 1
    try:
        while len(cluster_list) < n:
            print counter[tracker]
            new_one = counter[tracker]
            tracker += 1
            accepted = False
            for termno, cluster in enumerate(cluster_list):
                # assume min and max break ties in a reasonable way
                if should_go_in(new_one, cluster):
                    accepted = True
                    debug_print("adding {}".format(new_one), ",".join(cluster))
                    cluster.append(new_one)
                    break
                else:
                    pass
                    # print "rejected", new_one, cluster
            if not accepted:
                #if new_one == "oil science":
                #    import ipdb
                #    ipdb.set_trace()
                debug_print("cant find a cluster for {}. Making a new one".format(new_one))
                cluster_list.append([new_one])
    except IndexError:
        print "Cant get up to N. Ending early"
        return [coronate(cluster) for cluster in cluster_list]

    return [coronate(cluster) for cluster in cluster_list]