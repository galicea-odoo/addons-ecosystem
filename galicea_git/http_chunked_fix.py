# -*- coding: utf-8 -*-

import io

# Werkzeug version bundled into odoo doesn't handle this kind of Transfer-Encoding
# correctly. We copy the fix from https://github.com/pallets/werkzeug/pull/1198/files
class DechunkedInput(io.RawIOBase):
    """An input stream that handles Transfer-Encoding 'chunked'"""

    def __init__(self, rfile):
        self._rfile = rfile
        self._done = False
        self._len = 0

    def readable(self):
        return True

    def read_chunk_len(self):
        try:
            line = self._rfile.readline().decode('latin1')
            _len = int(line.strip(), 16)
        except ValueError:
            raise IOError('Invalid chunk header')
        if _len < 0:
            raise IOError('Negative chunk length not allowed')
        return _len

    def readinto(self, buf):
        read = 0
        while not self._done and read < len(buf):
            if self._len == 0:
                # This is the first chunk or we fully consumed the previous
                # one. Read the next length of the next chunk
                self._len = self.read_chunk_len()

            if self._len == 0:
                # Found the final chunk of size 0. The stream is now exhausted,
                # but there is still a final newline that should be consumed
                self._done = True

            if self._len > 0:
                # There is data (left) in this chunk, so append it to the
                # buffer. If this operation fully consumes the chunk, this will
                # reset self._len to 0.
                n = min(len(buf), self._len)
                buf[read:read + n] = self._rfile.read(n)
                self._len -= n
                read += n

            if self._len == 0:
                # Skip the terminating newline of a chunk that has been fully
                # consumed. This also applies to the 0-sized final chunk
                terminator = self._rfile.readline()
                if terminator not in (b'\n', b'\r\n', b'\r'):
                    raise IOError('Missing chunk terminating newline')

        return read

def http_input_stream(request):
    if request.httprequest.headers.get('Transfer-Encoding') == 'chunked' \
            and not request.httprequest.environ.get('wsgi.input_terminated'):
        return DechunkedInput(request.httprequest.environ['wsgi.input'])
    return request.httprequest.stream
