'''
this stuff is to help initialize model with empirical lm
(i.e. based on counts in docs)

I thought this would help algo converge. it does! but the serialization
costs are too high. pickling this is expensive. so is counting. 

Based on messing w/ this all afternoon I sort of suspect its better 
to just let CVBO do the work
'''


def fill_qi_and_count(dd, mm):
    '''init w/ emprical language models from D and G'''
    # if a doc is not responsive to a query, there are only 2 options for the token: D or G
    # if it is responsive to query, there are 3 options  
    print "[*] Filling Q_i and counting ntok={}".format(Ntok)
    print "\t - Filling Q_ik"
    ks = np.zeros(K)
    nsk = np.zeros((S, K))
    nwk = np.zeros((V, K))
    for i_ in range(Ntok):
        w = dd.i_w[i_]
        mm.Q_ik[i_][GLM_K] = mm.emprical_N_wk[GLM_K][w]
        if dd.hits[i_] == 1:
            mm.Q_ik[i_][QLM_K] = mm.emprical_N_wk[GLM_K][w] * 2 # init query lm to global X 2 ? 
        dk = dd.i_dk[i_] # i's document lm
        mm.Q_ik[i_][dk] = mm.emprical_N_wk[dk][w]
        mm.Q_ik[i_] = mm.Q_ik[i_]/np.sum(mm.Q_ik[i_]) # normalize
        np.add(ks, mm.Q_ik[i_], out=ks)
        #if i_ == 880:
        #    import ipdb
        #    ipdb.set_trace()
        np.add(nsk[dd.i_s[i_]], mm.Q_ik[i_], out=nsk[dd.i_s[i_]])
        np.add(nwk[dd.i_w[i_]], mm.Q_ik[i_], out=nwk[dd.i_w[i_]])
        assert round(np.sum(mm.Q_ik[i_]), 5) == 1.
        assert np.where(mm.Q_ik[i_] != 0)[0].shape[0] <= 3 # no more than 3 ks turned on per row

    mm.N_k = ks
    mm.N_sk = nsk
    mm.N_wk = nwk


try:
    # annoying that all this stuff is serialized individually.
    # but pickle was freezing on Q_ik: https://github.com/numpy/numpy/issues/2396
    mm.emprical_N_wk = np.load(ARGS.corpus + ".emprical_N_wk.dat")
    print "[*] Found & loaded cached empirical lms"
except IOError:
    print "[*] Could not find cached empirical lm. Building one"
    fill_emprical_language_models(dd, mm)
    print "\t - Dumping model"
    mm.emprical_N_wk.dump(ARGS.corpus + ".emprical_N_wk.dat")
    # This is just too big to pickle. Serialization takes too long
    # https://github.com/numpy/numpy/issues/2396
    # using np.savetxt for big matrixes b/c 
    # apparently pickle does not work for that until python 3.3
    # np.savetxt(ARGS.corpus + ".Q_ik.gz", mm.Q_ik)



def fill_emprical_language_models(dd, mm):
    '''find p(W|K) for each doc, G and Q lm'''
    smoothing = 1
    mm.emprical_N_wk = np.zeros((K,V), dtype=np.float32)
    print "\t - Adding up the empirical language model\n"
    for k in range(K):
        if k % 100 == 0:
            sys.stderr.write("{} of {}\t".format(k, K))
        tot_words = sum(dd.doc_counts[k]) + (smoothing * V)
        for v in range(V):
            try:
                tot_word = tot_word = dd.doc_counts[k][v] + smoothing
            except KeyError:  # i.e. word does not appear
                tot_word = smoothing
            mm.emprical_N_wk[k][v] = tot_word/tot_words
    print "\t Done"
