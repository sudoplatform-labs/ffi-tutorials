import numpy

import library

print("\n --- Running Tests --- \n")

print("Running boolean test...", end="  ")
valueBool = False
resultBool = library.bool_inc_test(valueBool)
assert ((not valueBool) == resultBool), "Bool test failed"
print("Passed")

print("Running signed int tests...", end="  ")
valueI8: numpy.int8 = 0
resultI8: numpy.int8 = library.i8_inc_test(valueI8)
assert (resultI8 == (valueI8 + 1)), "i8 test failed"

valueI16: numpy.int16 = 0
resultI16: numpy.int16 = library.i16_inc_test(valueI16)
assert (resultI16 == (valueI16 + 1)), "i16 test failed"

valueI32: numpy.int32 = 0
resultI32: numpy.int32 = library.i32_inc_test(valueI32)
assert (resultI32 == (valueI32 + 1)), "i32 test failed"

valueI64: numpy.int64 = 0
resultI64: numpy.int64 = library.i64_inc_test(valueI64)
assert (resultI64 == (valueI64 + 1)), "i64 test failed"
print("Passed")


print("Running unsigned int tests...", end="  ")
valueU8: numpy.uint8 = 0
resultU8: numpy.uint8 = library.u8_inc_test(valueU8)
assert (resultU8 == (valueU8 + 1)), "u8 test failed"

valueU16: numpy.uint16 = 0
resultU16: numpy.uint16 = library.u16_inc_test(valueU16)
assert (resultU16 == (valueU16 + 1)), "u16 test failed"

valueU32: numpy.uint32 = 0
resultU32: numpy.uint32 = library.u32_inc_test(valueU32)
assert (resultU32 == (valueU32 + 1)), "u32 test failed"

valueU64: numpy.uint64 = 0
resultU64: numpy.uint64 = library.u64_inc_test(valueU64)
assert (resultU64 == (valueU64 + 1)), "u64 test failed"
print("Passed")


print("Running float test...", end="  ")
floatValue: numpy.float32 = 0.0
assert (library.float_inc_test(floatValue) == (floatValue + 1.0)), "float test failed"
print("Passed")


print("Running double test...", end="  ")
doubleValue: numpy.double = 0.0
assert (library.double_inc_test(doubleValue) == (doubleValue + 1.0)), "double test failed"
print("Passed")


print("Running String test...", end="  ")
message = "Hello World!"
targetMessage = message + message
assert (library.string_inc_test(message) == targetMessage), "string test failed"
print("Passed")


print("Running byRef test...", end="\t")
byrefValue: library.Point = library.Point(1.0, 2.0)
byrefResult: library.Point = library.byref_inc_test(byrefValue)
assert (byrefResult.x == (byrefValue.x + 1.0)), "byRef test failed"
assert (byrefResult.y == (byrefValue.y + 1.0)), "byRef test failed"
print("Passed")


print("Running option type test (test for int32)...", end="  ")
optionalValue : numpy.int32 = 0
optionalResult : numpy.int32 = library.optional_type_inc_test(optionalValue)
if optionalResult != None:
    assert(optionalResult == (optionalValue + 1)), "optional type test returned None"
    print("Passed")
    print("\tReturned value = " + str(optionalResult))
else:
    print("Failed")
    print("\tReturned value = None when an int32 was expected")


print("Running option type test (test for None)...", end="  ")
optionalValue : numpy.int32 = None
optionalResult : numpy.int32 = library.optional_type_inc_test(optionalValue)
if optionalResult != None:
    print("Failed")
    print("\tReturned value = " + str(optionalResult) + " when None was expected")
else:
    print("Passed")
    print("\tReturned value = None")


print("Running vector test...", end="  ");
arrayValue = ["one", "two", "three"]
arrayResult = library.vector_inc_test(arrayValue)
assert(arrayResult == (arrayValue + arrayValue)), "Vector (array) test failed"
print("Passed")
print ("\tarrayResult = ", end=" ")
print (' '.join(arrayResult))


print("Running HashMap test...", end="  ");
arrayDictionaryValue = {
    "one" : 1,
    "two" : 2,
    "three" : 3 }
arrayDictionaryResult = library.hash_map_inc_test(arrayDictionaryValue)
arrayDictionaryValue["zero"] = 0
assert(arrayDictionaryValue == arrayDictionaryResult), "HashMap (Dictionary) test failed"
print("Passed")

print("Running void test...", end="  ")
voidValue : numpy.int32 = 0
voidResult = library.void_inc_test(voidValue)
assert (voidResult == None), "Void test failed"
print("Passed")


print("Running Error Code Test On Success test...", end="  ")
value1: numpy.uint64 = 0
value2: numpy.uint64 = 1
try:
    rValue = library.error_inc_test(value1, value2)
    print("Passed")
    print("\tReturned value = " + str(rValue))
except ArithmeticError.IntegerOverflow:
    print("Failed")
    print("\tReturned value = " + str(exception))


print("Running Error Code Test On Failure test...", end="  ")
value1: numpy.uint64 = numpy.iinfo(numpy.uint64).max
value2: numpy.uint64 = 1
try:
    rValue = library.error_inc_test(value1, value2)
    print("Failed")
    print("\tReturned value = " + str(rValue))
except library.ArithmeticError.IntegerOverflow as ex:
    print("Passed")
    print("\tReturned value = error" + ex.args[0])


print("\n --- End of Tests ---\n")