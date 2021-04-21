//
//  main.swift
//  test_app
//
//  Created by Steven H. McCown on 2/9/21.
//

import Foundation

print(" --- Running Tests --- ")

print("Running boolean test...")
let valueBool: Bool = false
var resultBool: Bool = boolIncTest(value: valueBool)
assert(!valueBool == resultBool, "Bool test failed")


print("Running signed int tests...");
let valueI8: Int8 = 0;
var resultI8: Int8 = i8IncTest(value: valueI8);
assert(resultI8 == (valueI8 + 1), "i8 test failed");

let valueI16: Int16 = 0;
var resultI16: Int16 = i16IncTest(value: valueI16);
assert(resultI16 == (valueI16 + 1), "i16 test failed");

let valueI32: Int32 = 0;
var resultI32: Int32 = i32IncTest(value: valueI32);
assert(resultI32 == (valueI32 + 1), "i32 test failed");

let valueI64: Int64 = 0;
var resultI64: Int64 = i64IncTest(value: valueI64);
assert(resultI64 == (valueI64 + 1), "i64 test failed");


print("Running unsigned int tests...");
let valueU8: UInt8 = 0;
var resultU8: UInt8 = u8IncTest(value: valueU8);
assert(resultI8 == (valueI8 + 1), "u8 test failed");

let valueU16: UInt16 = 0;
var resultU16: UInt16 = u16IncTest(value: valueU16);
assert(resultI16 == (valueI16 + 1), "u16 test failed");

let valueU32: UInt32 = 0;
var resultU32: UInt32 = u32IncTest(value: valueU32);
assert(resultI32 == (valueI32 + 1), "u32 test failed");

let valueU64: UInt64 = 0;
var resultU64: UInt64 = u64IncTest(value: valueU64);
assert(resultI64 == (valueI64 + 1), "u64 test failed");


print("Running float test...");
let floatValue: Float32 = 0.0;
assert(floatIncTest(value: floatValue) == (floatValue + 1.0), "float test failed");


print("Running double test...");
let doubleValue: Double = 0.0;
assert(doubleIncTest(value: doubleValue) == (doubleValue + 1.0), "double test failed");


print("Running String test...");
let message: String = "Hello World!";
let targetMessage: String = "\(message)\(message)";
assert(stringIncTest(value: message) == targetMessage, "string test failed");


print("Running byRef test...");
let byrefValue: Point = Point(x: 1.0, y: 2.0);
let byrefResult: Point = byrefIncTest(value: byrefValue);
assert(byrefResult.x == (byrefValue.x + 1.0), "byRef test failed");
assert(byrefResult.y == (byrefValue.y + 1.0), "byRef test failed");


print("Running option type test...");
let optionalValue : Int32 = 0;
var optionalResult : Int32 = optionalTypeIncTest(value: optionalValue) ?? -1;
assert(optionalResult == (optionalValue + 1), "optional (Int32) test failed");


print("Running vector test...");
let arrayValue: [String] = ["one", "two", "three"]
var arrayResult: [String] = []
arrayResult = vectorIncTest(value: arrayValue)
assert(arrayResult == (arrayValue + arrayValue), "Vector (array) test failed")


print("Running HashMap test...");
var arrayDictionaryValue = [String : Int32] ()
arrayDictionaryValue["one"] = 1
arrayDictionaryValue["two"] = 2
arrayDictionaryValue["three"] = 3
var arrayDictionaryResult = [String : Int32] ()
arrayDictionaryResult = hashMapIncTest(value: arrayDictionaryValue)
arrayDictionaryValue["zero"] = 0;
assert(arrayDictionaryValue == arrayDictionaryResult, "HashMap (Dictionary) test failed")


print("Running void test...")
let voidValue : Int32 = 0
var voidResult : () = voidIncTest(value: voidValue)
assert(voidResult == (), "Void test failed")
        

print("Running Error Code Test On Success test...");
let value1: UInt64 = 0;
let value2: UInt64 = 1;
do {
    let rValue = try errorIncTest(a: value1, b: value2);
    print("     Returned value = \(rValue)");
} catch (let exception) {
    print("     Returned value = \(exception)");
}


print("Running Error Code Test On Failure test...");
let val1: UInt64 = UInt64.max;
let val2: UInt64 = 1;
do {
    let rValue = try errorIncTest(a: val1, b: val2);
    print("     Returned value = \(rValue)");
} catch (let exception) {
    print("     Returned value = \(exception)");
}


print(" --- End of Tests ---\n");
