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

struct ARGS;

typedef struct ARGS{
    int starttok;    // run on positions [starttok;endtok)
    int endtok;
    uint32_t *tokens;   // wordid per token position; length Ntok
    uint32_t *docids;   // docid per token position; length Ntok
    uint32_t *qfix;   // boolean: fix this position?
    int K;  // num topics
    int V;  // vocab size (num wordtypes) .. oh not necessary?
    float *A_dk;      // doc pseudocounts
    float *E_wk;      // lexical pseudocounts
    float *E_k;       // precomputed sum(E_wk[:;k]) for each k
    float *Q_ik;      // token-level Q fields size (Ntok x K)
    float *N_wk;   // matrix size (V x K)
    float *N_k;    // vector length K
    float *N_dk;    // matrix size (D x K)
} ARGS;

void update(
        int direction,
        int K,
        int i,
        int d,
        int w,
        float *Q_ik,   // token-level Q fields
        float *N_wk,   // matrix size (V x K)
        float *N_k,
        float *N_dk
        ) {

    for (int k=0; k<K; k++) {
        float qdelta = direction * Q_ik[ind2(K,i,k)];
        N_k[k]            += qdelta;
        N_wk[ind2(K,w,k)] += qdelta;
        N_dk[ind2(K,d,k)] += qdelta;
    }
}

void update_i(
        int starttok,    // run on positions [starttok,endtok)
        int endtok,
        uint32_t *tokens,   // wordid per token position, length Ntok
        uint32_t *docids,   // docid per token position, length Ntok
        uint32_t *qfix,   // boolean: fix this position?
        int K,  // num topics
        int V,  // vocab size (num wordtypes) .. oh not necessary?
        float *A_dk,      // doc pseudocounts
        float *E_wk,      // lexical pseudocounts
        float *E_k,       // precomputed sum(E_wk[:,k]) for each k
        float *Q_ik,      // token-level Q fields size (Ntok x K)
        float *N_wk,   // matrix size (V x K)
        float *N_k,    // vector length K
        float *N_dk    // matrix size (D x K)
        ){

}

// many args! maybe should use struct

void sweep(
        ARGS* args
        )
{
    // temp space
    double probs[args->K];  // careful: uninitialized memory to start

    for (int i=args->starttok; i<args->endtok; i++) {
        //if (qfix[i]) {
        //    continue;
        //}
        uint32_t w = args->tokens[i];
        uint32_t d = args->docids[i];
        /* printf("TOK %u %d %d\n", i, w,d); */
        // decrement
        update(-1, args->K,i,d,w, args->Q_ik, args->N_wk, args->N_k, args->N_dk);

        // P(z=k | w) \propto
        //                   n[w,k] + eta[w,k]
        // (a[d,k]+n[d,k]) * -----------------
        //                   n[k]   + eta[k]
        
        double probsum = 0;
        for (int k=0; k<args->K; k++) {

            double DD = args->A_dk[ind2(args->K, d,k)] + args->N_dk[ind2(args->K, d,k)];
            double AA = args->E_wk[ind2(args->K, w,k)] + args->N_wk[ind2(args->K, w,k)];
            double BB = args->E_k[k] + args->N_k[k];
            double pp = DD * AA / BB;
            pp = MAX(1e-100, pp);
            /* if (pp <= 0) { */
            /*     printf("BAD %d\n", w); */
            /* } */
            probs[k] = pp;
            probsum += pp;
            /* printf("%g %g\n", pp, probsum); */
        }
        // could get another speed gain by folding this into increment step?
        for (int k=0; k<args->K; k++) {
            /* printf("k=%d Q=%g\n", k, probs[k]/probsum); */
            /* Q_ik[ind2(K, i,k)] = MAX(1e-100, probs[k] / probsum); */
            args->Q_ik[ind2(args->K, i,k)] = probs[k] / probsum;
        }
        // increment
        update(+1, args->K,i,d,w, args->Q_ik, args->N_wk, args->N_k, args->N_dk);

    }
}

