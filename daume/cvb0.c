#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// index for a matrix represented row-major.
// does NOT need to know total number of rows.

// double: 32bit
// double: 64bit.  note this is the most common default

#include <pthread.h>
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

#define MAX(a, b) ((a>b) ? (a) : (b))

int ind2(int numcols, int row, int col) {
    return numcols*row + col;
}

struct ARGS;
struct ARGS_array;
const int MAX = 10000;

// parameterization for 1 thread. 
// if no threading, just past this to sweep
typedef struct ARGS{
    int nthreads;    // 
    int starttok;    // run on positions [starttok;endtok)
    int endtok;
    uint32_t *tokens;   // wordid per token position; length Ntok
    uint32_t *docids;   // docid per token position; length Ntok
    uint32_t *qfix;   // boolean: fix this position?
    int K;  // num topics
    int V;  // vocab size (num wordtypes) .. oh not necessary?
    double *A_dk;      // doc pseudocounts
    double *E_wk;      // lexical pseudocounts
    double *E_k;       // precomputed sum(E_wk[:;k]) for each k
    double *Q_ik;      // token-level Q fields size (Ntok x K)
    double *N_wk;   // matrix size (V x K)
    double *N_k;    // vector length K
    double *N_dk;    // matrix size (D x K)
    uint32_t *I_dk;
} ARGS;

// an array of parameterizations, one for each thread
typedef struct ARGS_array{
    short nthread;    // number of structs. each thread gets 1 struct
    ARGS* all_args[MAX]; 
} ARGS_array;

void update(
        int direction,
        int K,
        int i,
        int d,
        int w,
        double *Q_ik,   // token-level Q fields
        double *N_wk,   // matrix size (V x K)
        double *N_k,
        double *N_dk,
        uint32_t *I_dk
        ) {

    int valid_ks[3] = {0, 1, I_dk[i]};
    for (int k_ix=0; k_ix<3; k_ix++) {
        int k = valid_ks[k_ix];
        double qdelta = direction * Q_ik[ind2(K,i,k)];
        N_k[k]            += qdelta;
        N_wk[ind2(K,w,k)] += qdelta;
        N_dk[ind2(K,d,k)] += qdelta;
    }
}



void sweep(
        ARGS *args
        )
{
    double probs[args->K];  // careful: uninitialized memory to start

    
    for (int i=args->starttok; i<args->endtok; i++) {
        //if (qfix[i]) {
        //    continue;
        //}
        //printf("%d tokno \n", i);
        //printf("%d tokens \n", args->tokens[i]);
        //printf("%d idk \n", args->I_dk[i]);
        uint32_t w = args->tokens[i];
        uint32_t d = args->docids[i];
        // decrement

        //pthread_mutex_lock (&mutex);  // this whole update is part of one transaction w/ mutex
        update(-1, args->K,i,d,w, args->Q_ik, args->N_wk, args->N_k, args->N_dk, args->I_dk);

        // P(z=k | w) \propto
        //                   n[w,k] + eta[w,k]
        // (a[d,k]+n[d,k]) * -----------------
        //                   n[k]   + eta[k]
        
        double probsum = 0;
        int valid_ks[3] = {0, 1, args->I_dk[i]};
        for (int k_ix=0; k_ix<3; k_ix++) {
            int k = valid_ks[k_ix];
            double DD = args->A_dk[ind2(args->K, d,k)] + args->N_dk[ind2(args->K, d,k)];
            double AA = args->E_wk[ind2(args->K, w,k)] + args->N_wk[ind2(args->K, w,k)];
            double BB = args->E_k[k] + args->N_k[k];
            double pp = DD * AA / BB;
            pp = MAX(1e-100, pp);
            // if (pp <= 0) { 
            //     printf("BAD %d\n", w);
            // } 
            probs[k] = pp;
            probsum += pp;
            // printf("%g %g\n", pp, probsum); 
        }
        // could get another speed gain by folding this into increment step?
        for (int k_ix=0; k_ix<3; k_ix++) {
            int k = valid_ks[k_ix];
            // printf("k=%d Q=%g\n", k, probs[k]/probsum); 
            // Q_ik[ind2(K, i,k)] = MAX(1e-100, probs[k] / probsum); 
            args->Q_ik[ind2(args->K, i,k)] = probs[k] / probsum;
        }
        // increment
        update(+1, args->K,i,d,w, args->Q_ik, args->N_wk, args->N_k, args->N_dk, args->I_dk);
        //pthread_mutex_unlock (&mutex); // release the lock
    }
}

/*
void threaded_sweep(ARGS* args)
{
    pthread_t thr[args->nthreads];
    int o;
    int per_thread = args->endtok/args->nthreads;
    for(int n = 0; n < args->nthreads; n++){
        struct ARGS a;
        a.starttok = per_thread * n;
        a.endtok = MAX(per_thread * n, args->endtok);
        a.tokens = args->tokens;
        a.docids = args->docids;
        a.qfix = NULL;
        a.K = args->K;
        a.V = args->V;
        a.A_dk = args->A_dk;
        a.E_wk = args->E_wk;
        a.E_k = args->E_k;
        a.Q_ik = args->Q_ik;
        a.N_wk = args->N_wk;
        a.N_k = args->N_k;
        a.N_dk = args->N_dk;

        o = pthread_create(&thr[n], NULL, sweep, &a);

    }
    for(int n = 0; n < args->nthreads; n++){
        o = pthread_join(thr[n], NULL);
    }
}
*/
