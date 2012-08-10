pyucl
=====

This is a very simple python wrapper for ucl
(http://www.oberhumer.com/opensource/ucl/) using cffi.  Note that it
has been written for cffi 0.2.1, and doesn't really work hard to be
efficient.

Use it as follows::

  >>> from pyucl import ucl

  >>> @ucl.callback
  ... def a_callback(n0, n1, n, v):
  ...     print "CALLBACK GOT CALLED: %r %r %r" % (n0, n1, n)

  >>> string_in = "henkitsminehenkhenkhenkitsmine"
  >>> string_out = ucl.nrv2d_99_compress(string_in,
  ...                                level=10, callback=a_callback)
  CALLBACK GOT CALLED: 0L 0L -1
  CALLBACK GOT CALLED: 1L 0L 3
  CALLBACK GOT CALLED: 30L 24L 4

  >>> print len(string_in), len(string_out)
  30 24

  >>> string_dec = ucl.nrv2d_decompress(string_out, len(string_in))

  >>> print string_dec == string_in
  True

  >>> string_dec = ucl.nrv2d_decompress(string_out, len(string_in) - 10)
  Traceback (most recent call last):
  ...
  RuntimeError: Decompression failed: -202 (UCL_E_OUTPUT_OVERRUN)

  >>> ucl.nrv2b_decompress(string_out, 2*len(string_in))
  Traceback (most recent call last):
  ...
  RuntimeError: Decompression failed: -203 (UCL_E_LOOKBEHIND_OVERRUN)

Before running, make sure to have ucl installed on your system.

