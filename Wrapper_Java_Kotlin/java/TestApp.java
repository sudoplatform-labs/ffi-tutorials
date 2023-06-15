//
//  TestApp.java
//  TestApp
//
//  Created by Steven H. McCown on 05/23/23.
//

import java.util.HashMap;
import java.util.Optional;
import java.util.OptionalInt;

import uniffi.library.*;  
import uniffi.library.MyArithmeticException.*;
import uniffi.library.MyArithmeticException.IntegerOverflow.*;


public class TestApp {

    public static void main(String[] args) {  
        System.out.println(" --- Running Tests --- ");

        System.out.println("Running boolean test...");
        boolean valueBool = false;
        boolean resultBool = LibraryKt.boolIncTest(valueBool);
        if (valueBool == resultBool) {
            System.out.println("Bool test failed");
        }


        System.out.println("Running signed int tests...");
        byte valueI8 = 0;
        byte resultI8 = LibraryKt.i8IncTest(valueI8);
        if (resultI8 != (valueI8 + 1)) {
            System.out.println("i8 test failed");
        }

        short valueI16 = 0;
        short resultI16 = LibraryKt.i16IncTest(valueI16);
        if (resultI16 != (valueI16 + 1)) {
            System.out.println("i16 test failed");
        }

        int valueI32 = 0;
        int resultI32 = LibraryKt.i32IncTest(valueI32);
        if (resultI32 != (valueI32 + 1)) {
            System.out.println("i32 test failed");
        }

        long valueI64 = 0;
        long resultI64 = LibraryKt.i64IncTest(valueI64);
        if (resultI64 != (valueI64 + 1)) {
            System.out.println("i64 test failed");
        }


        System.out.println("Running float test...");
        float floatValue = 0;
        float resultFloat = LibraryKt.floatIncTest(floatValue);
        if (resultFloat != (floatValue + 1)) {
            System.out.println("float test failed");
        }

        System.out.println("Running double test...");
        double doubleValue = 0.0;
        double resultDouble = LibraryKt.doubleIncTest(doubleValue);
        if (resultDouble != (doubleValue + 1)) {
            System.out.println("double test failed");
        }


        System.out.println("Running String test...");
        String message = "Hello World!";
        String targetMessage = message + message;
        if ((LibraryKt.stringIncTest(message).compareTo(targetMessage)) != 0) {
            System.out.println("string test failed");
        }


        System.out.println("Running byRef test...");
        double x0 = 0.0;
        double y0 = 0.0;
        Point byrefValue = new Point(x0, y0);
        System.out.println("    initial: ");
        System.out.println("        X:  " + byrefValue.getX());
        System.out.println("        Y:  " + byrefValue.getY());
        LibraryKt.byrefIncTest(byrefValue);
        System.out.println("    result: ");
        System.out.println("        X:  " + byrefValue.getX());
        System.out.println("        Y:  " + byrefValue.getY());
        if ((byrefValue.getX() == (x0 + 1.0)) &&
            (byrefValue.getY() == (y0 + 1.0))) {
            System.out.println("    byRef test passed");
        } else {
            System.out.println("    byRef test failed");
        }


        System.out.println("Running vector test...");
        String[] arrayValue = {"one", "two", "three"};
        String[] arrayTarget = new String[arrayValue.length + arrayValue.length];
        System.arraycopy(arrayValue, 0, arrayTarget, 0, arrayValue.length);
        System.arraycopy(arrayValue, 0, arrayTarget, arrayValue.length, arrayValue.length);
        java.util.List<String> arrayResult = LibraryKt.vectorIncTest(java.util.Arrays.asList(arrayValue));
        if (!arrayResult.equals(java.util.Arrays.asList(arrayTarget))) {
            System.out.println("Vector (array) test failed");
            System.out.println("    arrayValue = " + java.util.Arrays.asList(arrayValue));
            System.out.println("    arrayTarget = " + java.util.Arrays.asList(arrayTarget));
            System.out.println("    arrayResult = " + arrayResult);
        }


        System.out.println("Running HashMap test...");
        java.util.Map<String, Integer> arrayDictionaryValue = new HashMap<String, Integer>();
        arrayDictionaryValue.put("one", 1);
        arrayDictionaryValue.put("two", 2);
        arrayDictionaryValue.put("three", 3);
        java.util.Map<String, Integer> arrayDictionaryResult = LibraryKt.hashMapIncTest(arrayDictionaryValue);
        arrayDictionaryValue.put("zero", 0);
        if (!arrayDictionaryValue.equals(arrayDictionaryResult)) {
            System.out.println("HashMap (Dictionary) test failed");
        }


        System.out.println("Running void return value test...");
        int val = 1;
        LibraryKt.voidIncTest(val);

        System.out.println("Running Error Code Test On Success test...");
        int val1 = 0;
        int val2 = 1;
        try {
            int rValue = LibraryKt.errorIncTest(val1, val2);
            System.out.println("     Success!  Returned value = " + rValue);
        } catch (IntegerOverflow e) {
            System.out.println("     Fail!  Returned value = " + e);
        } catch (MyArithmeticException e) {
            System.out.println("     Fail!  Returned value = " + e);
        }

        System.out.println("Running Error Code Test On Failure test...");
        int val11 = Integer.MAX_VALUE;
        int val22 = 1;
        try {
            int rValue = LibraryKt.errorIncTest(val11, val22);
            System.out.println("     Success!  Returned value = " + rValue);
        } catch (IntegerOverflow e) {
            System.out.println("     Fail!  Returned value = " + e);
        } catch (MyArithmeticException e) {
            System.out.println("     Fail!  Returned value = " + e);
        }


        System.out.println(" --- End of Tests ---\n");
    }
}
