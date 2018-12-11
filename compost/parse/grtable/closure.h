//
// Created by DannyV on 2018-12-1.
//

#ifndef COMPOST_CLOSURE_H
#define COMPOST_CLOSURE_H

#ifdef __cplusplus
extern "C" {
#endif

#include "symbol.h"
#include "grammar.h"
#include "Python.h"

#define NONE_LABEL 100000000

symt_list_t  * first_sets_proc(sym_ent_t *);

typedef sym_ent_t ntfirsts[128];

extern ntfirsts NTFirst[128];

void init_NTFirst(void);
void NTFirst_print(void);

symt_list_t  * first_sets(sym_ent_t *);

typedef struct closure_t closure_t;
typedef struct goto_list_t goto_list_t;

struct closure_t {
    int label;
    int length;
    pitem_t * items;
    goto_list_t *goto_list;
    goto_list_t *goto_tail;
    symt_list_t * accept_symbols;
};

struct goto_list_t {
    sym_ent_t sym_index;                     // goto closure by this sym_index;
    closure_t closure;                  // goto closure;
    goto_list_t *next;                     // the next goto item.
};

void PyMem_Free_goto_list(goto_list_t *lst);
void PyMem_Free_symbol_sets(symt_list_t *sets);

typedef struct pitem_list_t pitem_list_t;

struct pitem_list_t {
    pitem_t item;
    pitem_list_t *next;
};



typedef struct nterm_follow_t {
    sym_ent_t nterm;
    sym_ent_t follow;
} nterm_follow_t;

typedef struct nf_list_t nf_list_t;
struct nf_list_t {
    nterm_follow_t entry;
    nf_list_t *next;
};

closure_t * get_closure(pitem_list_t * clist, int label);
closure_t * goto_closure(closure_t *clos, sym_ent_t sentry);
void print_closure_t(char * message, closure_t * ct);
int eq_closure_t(closure_t *a, closure_t *b);

typedef struct clos_list_t clos_list_t;
struct clos_list_t {
    closure_t c;
    clos_list_t *next;
};

clos_list_t * closure_collection(void);

void print_collection_t(clos_list_t * c);

#define NTACT 0
#define REDUCE 1
#define SHIFT 2
#define ERROR 3
#define ACCEPT 4

typedef char* action_t ;


PyObject * get_states_list(clos_list_t *c, Py_ssize_t length);

#ifdef __cplusplus
}
#endif

#endif //COMPOST_CLOSURE_H
