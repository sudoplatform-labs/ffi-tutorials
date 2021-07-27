# This file was autogenerated by some hot garbage in the `uniffi` crate.
# Trust me, you don't want to mess with it!

# Common helper code.
#
# Ideally this would live in a separate .py file where it can be unittested etc
# in isolation, and perhaps even published as a re-useable package.
#
# However, it's important that the detils of how this helper code works (e.g. the
# way that different builtin types are passed across the FFI) exactly match what's
# expected by the rust code on the other side of the interface. In practice right
# now that means coming from the exact some version of `uniffi` that was used to
# compile the rust component. The easiest way to ensure this is to bundle the Python
# helpers directly inline like we're doing here.

import os
import sys
import ctypes
import enum
import struct
import contextlib
import datetime


class RustBuffer(ctypes.Structure):
    _fields_ = [
        ("capacity", ctypes.c_int32),
        ("len", ctypes.c_int32),
        ("data", ctypes.POINTER(ctypes.c_char)),
        # Ref https://github.com/mozilla/uniffi-rs/issues/334 for this weird "padding" field.
        ("padding", ctypes.c_int64),
    ]

    @staticmethod
    def alloc(size):
        return rust_call_with_error(InternalError, _UniFFILib.ffi_library_8bbb_rustbuffer_alloc, size)

    @staticmethod
    def reserve(rbuf, additional):
        return rust_call_with_error(InternalError, _UniFFILib.ffi_library_8bbb_rustbuffer_reserve, rbuf, additional)

    def free(self):
        return rust_call_with_error(InternalError, _UniFFILib.ffi_library_8bbb_rustbuffer_free, self)

    def __str__(self):
        return "RustBuffer(capacity={}, len={}, data={})".format(
            self.capacity,
            self.len,
            self.data[0:self.len]
        )

    @contextlib.contextmanager
    def allocWithBuilder():
        """Context-manger to allocate a buffer using a RustBufferBuilder.

        The allocated buffer will be automatically freed if an error occurs, ensuring that
        we don't accidentally leak it.
        """
        builder = RustBufferBuilder()
        try:
            yield builder
        except:
            builder.discard()
            raise

    @contextlib.contextmanager
    def consumeWithStream(self):
        """Context-manager to consume a buffer using a RustBufferStream.

        The RustBuffer will be freed once the context-manager exits, ensuring that we don't
        leak it even if an error occurs.
        """
        try:
            s = RustBufferStream(self)
            yield s
            if s.remaining() != 0:
                raise RuntimeError("junk data left in buffer after consuming")
        finally:
            self.free()

    # For every type that lowers into a RustBuffer, we provide helper methods for
    # conveniently doing the lifting and lowering. Putting them on this internal
    # helper object (rather than, say, as methods on the public classes) makes it
    # easier for us to hide these implementation details from consumers, in the face
    # of python's free-for-all type system.

    # The primitive String type.

    @staticmethod
    def allocFromString(value):
        with RustBuffer.allocWithBuilder() as builder:
            builder.write(value.encode("utf-8"))
            return builder.finalize()

    def consumeIntoString(self):
        with self.consumeWithStream() as stream:
            return stream.read(stream.remaining()).decode("utf-8")

    # The Record type Point.

    @staticmethod
    def allocFromRecordPoint(v):
        with RustBuffer.allocWithBuilder() as builder:
            builder.writeRecordPoint(v)
            return builder.finalize()

    def consumeIntoRecordPoint(self):
        with self.consumeWithStream() as stream:
            return stream.readRecordPoint()

    # The Optional<T> type for i32.

    @staticmethod
    def allocFromOptionali32(v):
        with RustBuffer.allocWithBuilder() as builder:
            builder.writeOptionali32(v)
            return builder.finalize()

    def consumeIntoOptionali32(self):
        with self.consumeWithStream() as stream:
            return stream.readOptionali32()

    # The Sequence<T> type for string.

    @staticmethod
    def allocFromSequencestring(v):
        with RustBuffer.allocWithBuilder() as builder:
            builder.writeSequencestring(v)
            return builder.finalize()

    def consumeIntoSequencestring(self):
        with self.consumeWithStream() as stream:
            return stream.readSequencestring()

    # The Map<T> type for i32.

    @staticmethod
    def allocFromMapi32(v):
        with RustBuffer.allocWithBuilder() as builder:
            builder.writeMapi32(v)
            return builder.finalize()

    def consumeIntoMapi32(self):
        with self.consumeWithStream() as stream:
            return stream.readMapi32()


class ForeignBytes(ctypes.Structure):
    _fields_ = [
        ("len", ctypes.c_int32),
        ("data", ctypes.POINTER(ctypes.c_char)),
        # Ref https://github.com/mozilla/uniffi-rs/issues/334 for these weird "padding" fields.
        ("padding", ctypes.c_int64),
        ("padding2", ctypes.c_int32),
    ]

    def __str__(self):
        return "ForeignBytes(len={}, data={})".format(self.len, self.data[0:self.len])

class RustBufferStream(object):
    """Helper for structured reading of values from a RustBuffer."""

    def __init__(self, rbuf):
        self.rbuf = rbuf
        self.offset = 0

    def remaining(self):
        return self.rbuf.len - self.offset

    def _unpack_from(self, size, format):
        if self.offset + size > self.rbuf.len:
            raise InternalError("read past end of rust buffer")
        value = struct.unpack(format, self.rbuf.data[self.offset:self.offset+size])[0]
        self.offset += size
        return value

    def read(self, size):
        if self.offset + size > self.rbuf.len:
            raise InternalError("read past end of rust buffer")
        data = self.rbuf.data[self.offset:self.offset+size]
        self.offset += size
        return data

    # For every type used in the interface, we provide helper methods for conveniently
    # reading that type in a buffer. Putting them on this internal helper object (rather
    # than, say, as methods on the public classes) makes it easier for us to hide these
    # implementation details from consumers, in the face of python's free-for-all type
    # system.

    def readU8(self):
        return self._unpack_from(1, ">B")

    def readI8(self):
        return self._unpack_from(1, ">b")

    def readU16(self):
        return self._unpack_from(1, ">H")

    def readI16(self):
        return self._unpack_from(2, ">h")

    def readU32(self):
        return self._unpack_from(4, ">I")

    def readI32(self):
        return self._unpack_from(4, ">i")

    def readU64(self):
        return self._unpack_from(8, ">Q")

    def readI64(self):
        return self._unpack_from(8, ">q")

    def readF32(self):
        v = self._unpack_from(4, ">f")
        return v

    def readF64(self):
        return self._unpack_from(8, ">d")

    def readBool(self):
        v = self._unpack_from(1, ">b")
        if v == 0:
            return False
        if v == 1:
            return True
        raise InternalError("Unexpected byte for Boolean type")

    def readString(self):
        size = self._unpack_from(4, ">i")
        if size < 0:
            raise InternalError("Unexpected negative string length")
        utf8Bytes = self.read(size)
        return utf8Bytes.decode("utf-8")

    # The Record type Point.

    def readRecordPoint(self):
        return Point(
            self.readF64(),
            self.readF64()
        )# This type cannot currently be serialized, but we can produce a helpful error.
    def readErrorArithmeticError(self):
        raise InternalError("RustBufferStream.read not implemented yet for ErrorArithmeticError")

    # The Optional<T> type for i32.

    def readOptionali32(self):
        flag = self._unpack_from(1, ">b")
        if flag == 0:
            return None
        elif flag == 1:
            return self.readI32()
        else:
            raise InternalError("Unexpected flag byte for Optionali32")

    # The Sequence<T> type for string.

    def readSequencestring(self):
        count = self._unpack_from(4, ">i")
        if count < 0:
            raise InternalError("Unexpected negative sequence length")
        items = []
        while count > 0:
            items.append(self.readString())
            count -= 1
        return items

    # The Map<T> type for i32.

    def readMapi32(self):
        count = self._unpack_from(4, ">i")
        if count < 0:
            raise InternalError("Unexpected negative map size")
        items = {}
        while count > 0:
            key = self.readString()
            items[key] = self.readI32()
            count -= 1
        return items

class RustBufferBuilder(object):
    """Helper for structured writing of values into a RustBuffer."""

    def __init__(self):
        self.rbuf = RustBuffer.alloc(16)
        self.rbuf.len = 0

    def finalize(self):
        rbuf = self.rbuf
        self.rbuf = None
        return rbuf

    def discard(self):
        if self.rbuf is not None:
            rbuf = self.finalize()
            rbuf.free()

    @contextlib.contextmanager
    def _reserve(self, numBytes):
        if self.rbuf.len + numBytes > self.rbuf.capacity:
            self.rbuf = RustBuffer.reserve(self.rbuf, numBytes)
        yield None
        self.rbuf.len += numBytes

    def _pack_into(self, size, format, value):
        with self._reserve(size):
            # XXX TODO: I feel like I should be able to use `struct.pack_into` here but can't figure it out.
            for i, byte in enumerate(struct.pack(format, value)):
                self.rbuf.data[self.rbuf.len + i] = byte

    def write(self, value):
        with self._reserve(len(value)):
            for i, byte in enumerate(value):
                self.rbuf.data[self.rbuf.len + i] = byte

    # For every type used in the interface, we provide helper methods for conveniently
    # writing values of that type in a buffer. Putting them on this internal helper object
    # (rather than, say, as methods on the public classes) makes it easier for us to hide
    # these implementation details from consumers, in the face of python's free-for-all
    # type system.

    def writeU8(self, v):
        self._pack_into(1, ">B", v)

    def writeI8(self, v):
        self._pack_into(1, ">b", v)

    def writeU16(self, v):
        self._pack_into(1, ">H", v)

    def writeI16(self, v):
        self._pack_into(2, ">h", v)

    def writeU32(self, v):
        self._pack_into(4, ">I", v)

    def writeI32(self, v):
        self._pack_into(4, ">i", v)

    def writeU64(self, v):
        self._pack_into(8, ">Q", v)

    def writeI64(self, v):
        self._pack_into(8, ">q", v)

    def writeF32(self, v):
        self._pack_into(4, ">f", v)

    def writeF64(self, v):
        self._pack_into(8, ">d", v)

    def writeBool(self, v):
        self._pack_into(1, ">b", 1 if v else 0)

    def writeString(self, v):
        utf8Bytes = v.encode("utf-8")
        self._pack_into(4, ">i", len(utf8Bytes))
        self.write(utf8Bytes)

    # The Record type Point.

    def writeRecordPoint(self, v):
        self.writeF64(v.x)
        self.writeF64(v.y)# This type cannot currently be serialized, but we can produce a helpful error.

    def writeErrorArithmeticError(self, value):
        raise InternalError("RustBufferStream.write() not implemented yet for ErrorArithmeticError")

    # The Optional<T> type for i32.

    def writeOptionali32(self, v):
        if v is None:
            self._pack_into(1, ">b", 0)
        else:
            self._pack_into(1, ">b", 1)
            self.writeI32(v)

    # The Sequence<T> type for string.

    def writeSequencestring(self, items):
        self._pack_into(4, ">i", len(items))
        for item in items:
            self.writeString(item)

    # The Map<T> type for i32.

    def writeMapi32(self, items):
        self._pack_into(4, ">i", len(items))
        for (k, v) in items.items():
            self.writeString(k)
            self.writeI32(v)

# Error definitions
class RustError(ctypes.Structure):
    _fields_ = [
        ("code", ctypes.c_int32),
        ("message", ctypes.c_void_p),
    ]

    def free(self):
        rust_call_with_error(InternalError, _UniFFILib.ffi_library_8bbb_string_free, self.message)

    def __str__(self):
        return "RustError(code={}, message={})".format(
            self.code,
            str(ctypes.cast(self.message, ctypes.c_char_p).value, "utf-8"),
        )

class InternalError(Exception):
    @staticmethod
    def raise_err(code, message):
        raise InternalError(message)


class ArithmeticError:
    class IntegerOverflow(Exception):
        pass

    @staticmethod
    def raise_err(code, message):
        if code == 1:
            raise ArithmeticError.IntegerOverflow(message)
        
        raise Exception("Unknown error code")


def rust_call_with_error(error_class, fn, *args):
    error = RustError()
    error.code = 0

    args_with_error = args + (ctypes.byref(error),)
    result = fn(*args_with_error)
    if error.code != 0:
        message = str(error)
        error.free()

        error_class.raise_err(error.code, message)
    
    return result

# This is how we find and load the dynamic library provided by the component.
# For now we just look it up by name.
#
# XXX TODO: This will probably grow some magic for resolving megazording in future.
# E.g. we might start by looking for the named component in `libuniffi.so` and if
# that fails, fall back to loading it separately from `lib${componentName}.so`.

def loadIndirect():
    if sys.platform == "linux":
        libname = "lib{}.so"
    elif sys.platform == "darwin":
        libname = "lib{}.dylib"
    elif sys.platform.startswith("win"):
        # As of python3.8, ctypes does not seem to search $PATH when loading DLLs.
        # We could use `os.add_dll_directory` to configure the search path, but
        # it doesn't feel right to mess with application-wide settings. Let's
        # assume that the `.dll` is next to the `.py` file and load by full path.
        libname = os.path.join(
            os.path.dirname(__file__),
            "{}.dll",
        )
    return getattr(ctypes.cdll, libname.format("uniffi_library"))

# A ctypes library to expose the extern-C FFI definitions.
# This is an implementation detail which will be called internally by the public API.

_UniFFILib = loadIndirect()
_UniFFILib.library_8bbb_bool_inc_test.argtypes = (
    ctypes.c_int8,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_bool_inc_test.restype = ctypes.c_int8
_UniFFILib.library_8bbb_i8_inc_test.argtypes = (
    ctypes.c_int8,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_i8_inc_test.restype = ctypes.c_int8
_UniFFILib.library_8bbb_i16_inc_test.argtypes = (
    ctypes.c_int16,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_i16_inc_test.restype = ctypes.c_int16
_UniFFILib.library_8bbb_i32_inc_test.argtypes = (
    ctypes.c_int32,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_i32_inc_test.restype = ctypes.c_int32
_UniFFILib.library_8bbb_i64_inc_test.argtypes = (
    ctypes.c_int64,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_i64_inc_test.restype = ctypes.c_int64
_UniFFILib.library_8bbb_u8_inc_test.argtypes = (
    ctypes.c_uint8,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_u8_inc_test.restype = ctypes.c_uint8
_UniFFILib.library_8bbb_u16_inc_test.argtypes = (
    ctypes.c_uint16,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_u16_inc_test.restype = ctypes.c_uint16
_UniFFILib.library_8bbb_u32_inc_test.argtypes = (
    ctypes.c_uint32,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_u32_inc_test.restype = ctypes.c_uint32
_UniFFILib.library_8bbb_u64_inc_test.argtypes = (
    ctypes.c_uint64,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_u64_inc_test.restype = ctypes.c_uint64
_UniFFILib.library_8bbb_float_inc_test.argtypes = (
    ctypes.c_float,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_float_inc_test.restype = ctypes.c_float
_UniFFILib.library_8bbb_double_inc_test.argtypes = (
    ctypes.c_double,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_double_inc_test.restype = ctypes.c_double
_UniFFILib.library_8bbb_string_inc_test.argtypes = (
    RustBuffer,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_string_inc_test.restype = RustBuffer
_UniFFILib.library_8bbb_byref_inc_test.argtypes = (
    RustBuffer,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_byref_inc_test.restype = RustBuffer
_UniFFILib.library_8bbb_optional_type_inc_test.argtypes = (
    RustBuffer,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_optional_type_inc_test.restype = RustBuffer
_UniFFILib.library_8bbb_vector_inc_test.argtypes = (
    RustBuffer,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_vector_inc_test.restype = RustBuffer
_UniFFILib.library_8bbb_hash_map_inc_test.argtypes = (
    RustBuffer,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_hash_map_inc_test.restype = RustBuffer
_UniFFILib.library_8bbb_void_inc_test.argtypes = (
    ctypes.c_int32,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_void_inc_test.restype = None
_UniFFILib.library_8bbb_error_inc_test.argtypes = (
    ctypes.c_uint64,
    ctypes.c_uint64,
    ctypes.POINTER(RustError),
)
_UniFFILib.library_8bbb_error_inc_test.restype = ctypes.c_uint64
_UniFFILib.ffi_library_8bbb_rustbuffer_alloc.argtypes = (
    ctypes.c_int32,
    ctypes.POINTER(RustError),
)
_UniFFILib.ffi_library_8bbb_rustbuffer_alloc.restype = RustBuffer
_UniFFILib.ffi_library_8bbb_rustbuffer_from_bytes.argtypes = (
    ForeignBytes,
    ctypes.POINTER(RustError),
)
_UniFFILib.ffi_library_8bbb_rustbuffer_from_bytes.restype = RustBuffer
_UniFFILib.ffi_library_8bbb_rustbuffer_free.argtypes = (
    RustBuffer,
    ctypes.POINTER(RustError),
)
_UniFFILib.ffi_library_8bbb_rustbuffer_free.restype = None
_UniFFILib.ffi_library_8bbb_rustbuffer_reserve.argtypes = (
    RustBuffer,
    ctypes.c_int32,
    ctypes.POINTER(RustError),
)
_UniFFILib.ffi_library_8bbb_rustbuffer_reserve.restype = RustBuffer
_UniFFILib.ffi_library_8bbb_string_free.argtypes = (
    ctypes.c_void_p,
    ctypes.POINTER(RustError),
)
_UniFFILib.ffi_library_8bbb_string_free.restype = None

# Public interface members begin here.


class Point(object):
    def __init__(self,x, y ):
        self.x = x
        self.y = y

    def __str__(self):
        return "Point(x={}, y={} )".format(self.x, self.y )

    def __eq__(self, other):
        if self.x != other.x:
            return False
        if self.y != other.y:
            return False
        return True





def bool_inc_test(value):
    value = bool(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_bool_inc_test,(1 if value else 0))
    return (True if _retval else False)




def i8_inc_test(value):
    value = int(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_i8_inc_test,value)
    return int(_retval)




def i16_inc_test(value):
    value = int(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_i16_inc_test,value)
    return int(_retval)




def i32_inc_test(value):
    value = int(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_i32_inc_test,value)
    return int(_retval)




def i64_inc_test(value):
    value = int(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_i64_inc_test,value)
    return int(_retval)




def u8_inc_test(value):
    value = int(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_u8_inc_test,value)
    return int(_retval)




def u16_inc_test(value):
    value = int(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_u16_inc_test,value)
    return int(_retval)




def u32_inc_test(value):
    value = int(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_u32_inc_test,value)
    return int(_retval)




def u64_inc_test(value):
    value = int(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_u64_inc_test,value)
    return int(_retval)




def float_inc_test(value):
    value = float(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_float_inc_test,value)
    return float(_retval)




def double_inc_test(value):
    value = float(value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_double_inc_test,value)
    return float(_retval)




def string_inc_test(value):
    value = value
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_string_inc_test,RustBuffer.allocFromString(value))
    return _retval.consumeIntoString()




def byref_inc_test(value):
    value = value
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_byref_inc_test,RustBuffer.allocFromRecordPoint(value))
    return _retval.consumeIntoRecordPoint()




def optional_type_inc_test(value):
    value = (None if value is None else int(value))
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_optional_type_inc_test,RustBuffer.allocFromOptionali32(value))
    return _retval.consumeIntoOptionali32()




def vector_inc_test(value):
    value = list(x for x in value)
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_vector_inc_test,RustBuffer.allocFromSequencestring(value))
    return _retval.consumeIntoSequencestring()




def hash_map_inc_test(value):
    value = dict((k,int(v)) for (k, v) in value.items())
    _retval = rust_call_with_error(InternalError,_UniFFILib.library_8bbb_hash_map_inc_test,RustBuffer.allocFromMapi32(value))
    return _retval.consumeIntoMapi32()




def void_inc_test(value):
    value = int(value)
    rust_call_with_error(InternalError,_UniFFILib.library_8bbb_void_inc_test,value)




def error_inc_test(a,b):
    a = int(a)
    b = int(b)
    _retval = rust_call_with_error(ArithmeticError,_UniFFILib.library_8bbb_error_inc_test,a,b)
    return int(_retval)





__all__ = [
    "InternalError",
    "Point",
    "bool_inc_test",
    "i8_inc_test",
    "i16_inc_test",
    "i32_inc_test",
    "i64_inc_test",
    "u8_inc_test",
    "u16_inc_test",
    "u32_inc_test",
    "u64_inc_test",
    "float_inc_test",
    "double_inc_test",
    "string_inc_test",
    "byref_inc_test",
    "optional_type_inc_test",
    "vector_inc_test",
    "hash_map_inc_test",
    "void_inc_test",
    "error_inc_test",
    "ArithmeticError",
]

