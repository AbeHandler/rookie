#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// index for a matrix represented row-major.
// does NOT need to know total number of rows.

// float: 32bit
// double: 64bit.  note this is the most common default

#define MAX(a, b) ((a>b) ? (a) : (b))

int ind2(int numcols, int row, int col) {
    return numcols*row + col;
}

void check_nwk(double pp, int k, int i){
    if (pp < 0) { 
        printf("BAD. nwk %f %d %d\n", pp, k, i); 
    }
}

void update(
        int direction,
        int K,
        int i,
        int d,
        int w,
        float *Q_ik,   // token-level Q fields
        float *N_wk,   // matrix size (V x K)
        float *N_k,
        float *N_dk,
        uint32_t *i_dk
        ) {

    for (int k=0; k<K; k++) {
        float qdelta = direction * Q_ik[ind2(K,i,k)];
        N_k[k]            += qdelta;
        N_wk[ind2(K,w,k)] += qdelta;
        N_dk[ind2(K,d,k)] += qdelta;
        check_nwk(N_wk[ind2(K,w,k)], k, i);
    }
}



void checkPP(double pp, uint32_t w){
    if (pp <= 0.0) { 
        printf("BAD. under %d\n", w); 
    }
}

void checkQQ(double pp, double probs, double probsum){
    if (pp < 0.0) { 
        printf("BAD QQ. under %f %f\n", probs, probsum); 
    }
    if (pp > 1.0) { 
        printf("BAD QQ. over %f %f\n", probs, probsum); 
    }
}

// many args! maybe should use struct

void sweep(
        int starttok,    // run on positions [starttok,endtok)
        int endtok,
        uint32_t *tokens,   // wordid per token position, length Ntok
        uint32_t *docids,   // docid per token position, length Ntok
        uint32_t *i_dk,     // map: token position -> dk (document lm), length Ntok
        // uint8_t *qfix,   // boolean: fix this position?
        int K,  // num topics
        int V,  // vocab size (num wordtypes) .. oh not necessary?
        float *A_dk,      // doc pseudocounts
        float *E_wk,      // lexical pseudocounts
        float *E_k,       // precomputed sum(E_wk[:,k]) for each k
        float *Q_ik,      // token-level Q fields size (Ntok x K)
        float *N_wk,   // matrix size (V x K)
        float *N_k,    // vector length K
        float *N_dk    // matrix size (D x K)
        //float *qfix    // ignore this token? a binary vector of length Ntok
        )
{
    // temp space
    double probs[K];  // careful: uninitialized memory to start

    for (int i=starttok; i<endtok; i++) {
        //if (qfix[i]) {
        //    continue;
        //}

        uint32_t w = tokens[i];
        uint32_t d = docids[i];
        /* printf("TOK %u %d %d\n", i, w,d); */

        // decrement
        update(-1, K,i,d,w, Q_ik, N_wk, N_k, N_dk, i_dk);

        // P(z=k | w) \propto
        //                   n[w,k] + eta[w,k]
        // (a[d,k]+n[d,k]) * -----------------
        //                   n[k]   + eta[k]
        double probsum = 0.0;
        for (int k=0; k<K; k++) {
            double DD = A_dk[ind2(K, d,k)] + N_dk[ind2(K, d,k)];
            double AA = E_wk[ind2(K, w,k)] + N_wk[ind2(K, w,k)];
            double BB = E_k[k] + N_k[k];
            double pp = (DD * AA) / BB;
            
            /* printf("%g %g\n", pp, probsum); */
            if (k < 2 || k == i_dk[i]){ //In Daume model, only 3 Ks are valid.
                pp = MAX(1e-100, pp); //general lm and query lm
                checkPP(pp, w);
                probs[k] = pp;
                probsum += pp;
            } else {
                probs[k] = 0.0;
            }
        }
        

        for (int k=0; k<K; k++) {
            Q_ik[ind2(K, i,k)] = probs[k] / probsum;
            if (k < 2 || k == i_dk[i]){
                checkQQ(Q_ik[ind2(K, i,k)], probs[k], probsum);
            }
        }

        // increment
        update(+1, K,i,d,w, Q_ik, N_wk, N_k, N_dk, i_dk);

    }
}

