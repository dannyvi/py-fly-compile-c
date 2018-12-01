//
// Created by DannyV on 2018-11-28.
//

#include <Python.h>
#include <stdio.h>


#include "symbol.h"
#include "grammar.h"
#include "closure.h"
#include "tests.h"

PyObject *classNT, *classT, *classV;

static PyObject* grtable_init_class(PyObject* self, PyObject* args){
    PyObject *NT, *T, *V;
    if (! PyArg_ParseTuple( args, "OOO", &NT, &T, &V )) {
        return NULL;
    }
    classNT = NT;
    classT = T;
    classV = V;
    Py_INCREF(Py_None);
    return Py_None;
}

static symbol pyobj_build_symbol(PyObject *instance) {
    PyObject *attr;
    Py_ssize_t  size;
    sym_type type=NTerm;
    const char * pr=" ";
    symbol sym;

    if ( PyObject_IsInstance(instance, classNT)){
       type = NTerm;
    } else if ( PyObject_IsInstance(instance, classT)){
        type = Term;
    } else if ( PyObject_IsInstance(instance, classV)){
        type = Value;
    }
    if (PyObject_HasAttrString(instance, "symbol")){
        attr = PyObject_GetAttrString(instance, "symbol");
        pr = PyUnicode_AsUTF8AndSize(attr, &size);
        //printf( "%d: %s\n", type, pr);
    }
    sym = symbol_create(type, (char *)pr);
    return sym;
}

static PyObject* grtable_init_symbols(PyObject* self, PyObject* args)
{
    PyObject *listObj;

     if (! PyArg_ParseTuple( args, "O", &listObj ))
        {return NULL;}

    long length = PyList_Size(listObj);
    symbol syms[length];

    int i =0;
    for (i = 0; i < length; i++) {
        PyObject* temp = PyList_GetItem(listObj, i);
        syms[i] = pyobj_build_symbol(temp);
    }

    build_symbol_table(syms, length);

    SymbolTable_print();

    Py_INCREF(Py_None);
    return Py_None;

}

static PyObject*  grtable_init_grammar(PyObject* self, PyObject* size){
    int m;
    if (!PyArg_ParseTuple(size, "i", &m)) {
        return NULL;
    }

    printf("Init Grammar: %d\n", m);
    Grammar_init((size_t) m);
    printf("Count: %d\n", GrammarCount);
    Py_INCREF(Py_None);
    return Py_None;
}

static production* pyobj_build_production(PyObject *prod ){
    production *product = calloc(1, sizeof(production));
    long length = PyList_Size(prod);
    for (int i = 0; i < length; i++) {
        PyObject* temp = PyList_GetItem(prod, i);
        symbol s = pyobj_build_symbol(temp);
        symbol_entry e = sentry_find(s);
        product->body[i] = e;
    }
    return product;
}

static PyObject*  grtable_build_grammar(PyObject* self, PyObject* PyProd){
    PyObject *prod;
    if (!PyArg_ParseTuple(PyProd, "O", &prod)) {
        return NULL;
    }
    long length = PyList_Size(prod);
    for (int i=0; i<length;i++){
        PyObject* p = PyList_GetItem(prod, i);
        production *product = pyobj_build_production(p);
        Grammar_add(*product);
    }

    Grammar_print();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*  grtable_tests(PyObject* self, PyObject* obj){
    tests() ;
    Py_INCREF(Py_None);
    return Py_None;
}

static char grtable_init_class_docs[] =
        "init the Nterm, Term, Value class reference.\n";

static char grtable_init_symbols_docs[] =
        "add(  ): add all elements of the list\n";

static char grtable_init_gr_docs[] =
        "neccesarily init grammar before add productions.\n";

static char grtable_test_docs[] =
        "tests.\n";

static char grtable_build_gr_docs[] =
        "building_grammar.\n";

static PyMethodDef module_methods[] = {
        {"init_class", (PyCFunction)grtable_init_class, METH_VARARGS, grtable_init_class_docs},
        {"init_symbols", (PyCFunction)grtable_init_symbols, METH_VARARGS, grtable_init_symbols_docs},
        {"init_grammar", (PyCFunction)grtable_init_grammar, METH_VARARGS, grtable_init_gr_docs},
        {"build_grammar", (PyCFunction)grtable_build_grammar, METH_VARARGS, grtable_build_gr_docs},
        {"_tests", (PyCFunction)grtable_tests, METH_VARARGS, grtable_test_docs},
        {NULL, NULL, 0, NULL}
};


static struct PyModuleDef grtable = {
                PyModuleDef_HEAD_INIT,
                "grtable", /* name of module */
                "usage: grtable.init_symbols(type,type,type,symbols)\n", /* module documentation, may be NULL */
                -1,   /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
                module_methods
};

PyMODINIT_FUNC PyInit_grtable(void)
{
    return PyModule_Create(&grtable);
}
