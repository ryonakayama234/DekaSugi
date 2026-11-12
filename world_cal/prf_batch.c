/* Optional batch evaluator of the unchanged WORLD-CAL-v1 HMAC domain.
 * No RNG, no seed creation, no retained key or mutable global state.
 * The caller supplies encode_parts(..., stage); append the exact integer
 * marker, uint64 length=8 and big-endian uint64 index for each draw.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <openssl/hmac.h>
#include <math.h>
#include <stdint.h>

static PyObject *uniforms(PyObject *self, PyObject *args) {
    const char *key, *prefix;
    Py_ssize_t keylen, plen, count;
    int raw=0;
    unsigned long long start;
    if (!PyArg_ParseTuple(args, "y#y#Kn|p", &key, &keylen, &prefix, &plen,
                          &start, &count, &raw)) return NULL;
    if (keylen != 32 || count < 0 || (count &&
        (uint64_t)start > UINT64_MAX - (uint64_t)(count - 1))) {
        PyErr_SetString(PyExc_ValueError, "invalid PRF batch bounds");
        return NULL;
    }
    HMAC_CTX *base = HMAC_CTX_new(), *ctx = HMAC_CTX_new();
    PyObject *result = NULL;
    if (!base || !ctx || !HMAC_Init_ex(base,key,32,EVP_sha256(),NULL) ||
        !HMAC_Update(base,(const unsigned char *)prefix,(size_t)plen)) goto error;
    if (raw && count > PY_SSIZE_T_MAX/32) {
        PyErr_SetString(PyExc_OverflowError,"digest batch too large"); goto error;
    }
    result = raw ? PyBytes_FromStringAndSize(NULL,count*32) : PyList_New(count);
    if (!result) goto error;
    for (Py_ssize_t k = 0; k < count; ++k) {
        unsigned char tail[17] = {'I',0,0,0,0,0,0,0,8};
        uint64_t ix = (uint64_t)start + (uint64_t)k;
        for (int b=0;b<8;++b) tail[16-b]=(unsigned char)(ix >> (8*b));
        unsigned char digest[EVP_MAX_MD_SIZE];
        unsigned int len;
        if (!HMAC_CTX_copy(ctx,base) || !HMAC_Update(ctx,tail,sizeof tail) ||
            !HMAC_Final(ctx,digest,&len) || len!=32) goto error;
        if (raw) {
            memcpy(PyBytes_AS_STRING(result)+32*k,digest,32);
            continue;
        }
        uint64_t x=0;
        for (int b=0;b<7;++b) x=(x<<8)|digest[b];
        x >>= 3;
        double u=((double)x+0.5)/9007199254740992.0;
        if (u>=1.0) u=nextafter(1.0,0.0);
        if (!(isfinite(u) && u>0.0 && u<1.0)) goto error;
        PyObject *value=PyFloat_FromDouble(u);
        if (!value) goto error;
        PyList_SET_ITEM(result,k,value);
    }
    HMAC_CTX_free(ctx); HMAC_CTX_free(base);
    return result;
error:
    HMAC_CTX_free(ctx); HMAC_CTX_free(base);
    Py_XDECREF(result);
    if (!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError,"PRF batch failed");
    return NULL;
}
/* Final weighted parent sums only. Group formation and resampling stay Python.
 * Sequential binary64 additions may differ from Python 3.12 compensated sum;
 * the audit compares all 999x9 entries within the registered tolerance.
 */
static PyObject *weighted_sums(PyObject *self, PyObject *args) {
    PyObject *counts,*groups;
    if (!PyArg_ParseTuple(args,"OO",&counts,&groups)) return NULL;
    if (!PyList_Check(counts) || !PyList_Check(groups)) goto invalid;
    Py_ssize_t k=PyList_Size(groups),m=PyList_Size(counts);
    for (Py_ssize_t c=0;c<k;++c) {
        PyObject *g=PyList_GetItem(groups,c);
        if (!PyList_Check(g) || PyList_Size(g)!=9) goto invalid;
        for (int j=0;j<9;++j) if (!PyFloat_Check(PyList_GetItem(g,j))) goto invalid;
    }
    for (Py_ssize_t r=0;r<m;++r) {
        PyObject *row=PyList_GetItem(counts,r);
        if (!PyList_Check(row) || PyList_Size(row)!=k) goto invalid;
        for (Py_ssize_t c=0;c<k;++c) if (!PyLong_Check(PyList_GetItem(row,c))) goto invalid;
    }
    PyObject *result=PyList_New(m);
    if (!result) return NULL;
    for (Py_ssize_t r=0;r<m;++r) {
        PyObject *row=PyTuple_New(9);
        if (!row) {Py_DECREF(result); return NULL;}
        for (int j=0;j<9;++j) {
            double sum=0.0;
            for (Py_ssize_t c=0;c<k;++c) {
                double count=PyLong_AsDouble(PyList_GET_ITEM(PyList_GET_ITEM(counts,r),c));
                double value=PyFloat_AS_DOUBLE(PyList_GET_ITEM(PyList_GET_ITEM(groups,c),j));
                sum+=count*value;
            }
            if (PyErr_Occurred() || !isfinite(sum)) {
                Py_DECREF(row); Py_DECREF(result); goto invalid;
            }
            PyObject *value=PyFloat_FromDouble(sum);
            if (!value) {Py_DECREF(row);Py_DECREF(result);return NULL;}
            PyTuple_SET_ITEM(row,j,value);
        }
        PyList_SET_ITEM(result,r,row);
    }
    return result;
invalid:
    if (!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError,"invalid bootstrap arrays");
    return NULL;
}
static PyMethodDef methods[]={{"uniforms",uniforms,METH_VARARGS,"Exact contiguous HMAC uniforms."},{"weighted_sums",weighted_sums,METH_VARARGS,"Sequential parent-weighted bootstrap sums."},{NULL,NULL,0,NULL}};
static struct PyModuleDef module={PyModuleDef_HEAD_INIT,"_prf_batch",NULL,-1,methods};
PyMODINIT_FUNC PyInit__prf_batch(void) {return PyModule_Create(&module);}
