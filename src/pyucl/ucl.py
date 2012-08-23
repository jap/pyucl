from collections import defaultdict

from cffi import FFI

ffi = FFI()
ffi.cdef("""
int ucl_init();
int ucl_version(void);
const char* ucl_version_string(void);
const char* ucl_version_date(void);

struct ucl_compress_config_t
{
   ...;
};

typedef struct
{
    void(*callback)(unsigned int,
                    unsigned int,
                    int, void*);
   ...;
} ucl_progress_callback_t;

int ucl_nrv2b_99_compress(const unsigned char* src, unsigned int src_len,
                          unsigned char* dst, unsigned int* dst_len,
                          ucl_progress_callback_t *cb,
                          int level,
                          struct ucl_compress_config_t* conf,
                          unsigned int *result);

int ucl_nrv2d_99_compress(const unsigned char* src, unsigned int src_len,
                          unsigned char* dst, unsigned int* dst_len,
                          ucl_progress_callback_t *cb,
                          int level,
                          struct ucl_compress_config_t* conf,
                          unsigned int *result);

int ucl_nrv2e_99_compress(const unsigned char* src, unsigned int src_len,
                          unsigned char* dst, unsigned int* dst_len,
                          ucl_progress_callback_t *cb,
                          int level,
                          struct ucl_compress_config_t* conf,
                          unsigned int *result);

int ucl_nrv2b_decompress_safe_8(const unsigned char* src, unsigned int src_len,
                           unsigned char* dst, unsigned int* dst_len,
                           void* wrkmem);

int ucl_nrv2d_decompress_safe_8(const unsigned char* src, unsigned int src_len,
                           unsigned char* dst, unsigned int* dst_len,
                           void* wrkmem);

int ucl_nrv2e_decompress_safe_8(const unsigned char* src, unsigned int src_len,
                           unsigned char* dst, unsigned int* dst_len,
                           void* wrkmem);
""")

C = ffi.verify("#include <ucl/ucl.h>",
                libraries=['ucl'])

_callback_type =  "void(*)(unsigned int, unsigned int, int, void*)"
def callback(fun):
    """Decorator which turns a function into a ucl callback."""
    return ffi.callback(_callback_type, fun)

_ucl_errors = {
0: "UCL_E_OK",
-1: "UCL_E_ERROR",
-2: "UCL_E_INVALID_ARGUMENT",
-3: "UCL_E_OUT_OF_MEMORY",
# compression errors
-101: "UCL_E_NOT_COMPRESSIBLE",
# decompression errors
-201: "UCL_E_INPUT_OVERRUN",
-202: "UCL_E_OUTPUT_OVERRUN",
-203: "UCL_E_LOOKBEHIND_OVERRUN",
-204: "UCL_E_EOF_NOT_FOUND",
-205: "UCL_E_INPUT_NOT_CONSUMED",
-206: "UCL_E_OVERLAP_OVERRUN",
}

ucl_errors = defaultdict(lambda: "Unknown error")
ucl_errors.update(_ucl_errors)

def ucl_init():
    rv = C.ucl_init()
    if rv:
        raise RuntimeError("ucl_init() returned an error: %d (%s)" % (rv,
                           ucl_errors[rv]))
ucl_init()

ucl_version = C.ucl_version
ucl_version_string = C.ucl_version_string
ucl_version_date = C.ucl_version_date

def _ucl_compress(algo, data, level=1, callback=None):
    max_outbuflen = 256 + int(len(data)*1.25)
    outbuf = ffi.new("unsigned char[]", max_outbuflen)
    outbuflen = ffi.new("unsigned int *")
    outbuflen[0] = max_outbuflen

    if callback:
        assert ffi.typeof(callback) == ffi.typeof(_callback_type)
        str_callback = ffi.new("ucl_progress_callback_t*")
        str_callback[0].callback = callback
    else:
        str_callback = ffi.NULL

    retval = algo(ffi.new('char[]', data),
                  len(data),
                  outbuf, outbuflen,
                  str_callback, level,
                  ffi.NULL, ffi.NULL)
    if retval:
        raise RuntimeError("Compression failed: %d (%s)" % (retval,
                           ucl_errors[retval]))
    return ffi.buffer(outbuf, outbuflen[0])[:]

def nrv2b_99_compress(data, level=1, callback=None):
    return _ucl_compress(C.ucl_nrv2b_99_compress, data, level, callback)
def nrv2d_99_compress(data, level=1, callback=None):
    return _ucl_compress(C.ucl_nrv2d_99_compress, data, level, callback)
def nrv2e_99_compress(data, level=1, callback=None):
    return _ucl_compress(C.ucl_nrv2e_99_compress, data, level, callback)

def _ucl_decompress(algo, data, outsize):
    outbuf = ffi.new("unsigned char[]", outsize)
    outbuflen = ffi.new("unsigned int *")
    outbuflen[0] = outsize

    retval = algo(ffi.new('char[]', data),
                  len(data),
                  outbuf, outbuflen,
                  ffi.NULL)
    if retval:
        raise RuntimeError("Decompression failed: %d (%s)" % (retval,
                           ucl_errors[retval]))
    return ffi.buffer(outbuf, outbuflen[0])[:]

def nrv2b_decompress(data, outsize):
    return _ucl_decompress(C.ucl_nrv2b_decompress_safe_8, data, outsize)
def nrv2d_decompress(data, outsize):
    return _ucl_decompress(C.ucl_nrv2d_decompress_safe_8, data, outsize)
def nrv2e_decompress(data, outsize):
    return _ucl_decompress(C.ucl_nrv2e_decompress_safe_8, data, outsize)
