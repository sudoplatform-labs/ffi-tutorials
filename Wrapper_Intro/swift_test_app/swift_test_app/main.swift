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

print(" --- All Tests Succeded! --- ")
