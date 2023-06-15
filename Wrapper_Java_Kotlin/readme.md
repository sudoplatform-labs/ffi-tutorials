# Creating Language Wrappers For Rust Libraries - Part 3
# How to:  call Rust libraries from Java (via Kotlin)


## Background
The previous tutorial ([Creating Language Wrappers for Rust Libraries - Part 2](https://github.com/sudoplatform-labs/ffi-tutorials/tree/main/Wrapper_Data_Types)), showed how to use many different Rust data types and to share them between underlying Rust libraries and native apps that included them ... *using uniffi*.  This tutorial also demonstrated how to build and use the [Mozilla uniffi](https://github.com/mozilla/uniffi-rs) tool to *automatically* generate language wrappers for Swift and Python. Finally, the tutorial built Swift and Python test applications to demonstrate how to import the Rust library using the generated language wrappers.  (Note:  some of the example material was adapted from various uniffi examples.)


## Tutorial:  but what about Java?

The [Java](https://www.java.com/en/) programming language has many innovative features that make it ideal for a variety of applications.  In building one such application, I wanted to include a Rust library and access it using uniffi.  One problem ... uniffi doesn't create Java wrappers.  However, *they* say that Java can include libraries built with Kotlin, because [they use the same bytecode](https://kotlinlang.org/docs/faq.html).  Since uniffi does create Kotlin wrappers, importing them into a Java app sounded like an easy way to go.
 
For this tutorial, I will use the same library and test app format that I used in Part 2, so all of that should be familiar.  I will also discuss the differences or nuances that I discovered along the way.  As a quick summary, this tutorial describes how to:

1. **Rust:** Design and build a Rust library
2. **uniffi:** Create a UDL file describing the Rust library's accessible elements
3. **Kotlin:** Build a Kotlin wrapper / library
4. **Java** Create a Java test app that includes the Kotlin library 


## Mozilla's uniffi Tool Automates FFI Processes

As a review from Parts 1 & 2, building a Rust library and language wrappers using the uniffi tools is done as follows:

1. Create a custom Rust library
	1. Expose the desired API for the library.  The API will consist of all top-level functions and structures
	2. Setup a Cargo.toml file that specifies that the crate will be built as a dylib
	3. Build and test the library

2. Create a [*UDL*](https://mozilla.github.io/uniffi-rs/udl_file_spec.html) representation of each of the API functions
	1. UDL is a uniffi-specific design language that is a variation of Web Interface Definition Language (Web IDL)
	2. The UDL file will describe each of the top-level functions in the library

3. Use the uniffi tool to create a [*scaffolding layer*](https://mozilla.github.io/uniffi-rs/tutorial/Rust_scaffolding.html) for the library
	1. The scaffolding layer is a set of helper code that is used to make the top-level functions available to the foreign-language bindings

4. Create language-specific [bindings](https://mozilla.github.io/uniffi-rs/tutorial/foreign_language_bindings.html)
	1. This makes FFI calls look & feel like native code (e.g., Kotlin FFI feels like native Kotlin)

5. Import the scaffolding code, the language-specific code, and the generated library into a native application


## Creating the Rust Library
To get started, open a terminal window and create a project directory that will contain each of the library and applications for this tutorial.  In the terminal, navigate to the *Wrapper_Java_Kotlin* project directory and create a new rust library called *library*, as follows:

`cargo new --lib library` 

### Edit the Cargo.toml file
Next, navigate into the new *library* sub-directory just created, open Cargo.toml, and add the following (substituting your own values as desired), so that it looks like this:

```
[package]
name = "library"
version = "0.1.0"
authors = ["Steve McCown <smccown@anonyome.com>"]
license = "Apache version 2.0"
edition = "2018"
build = "build.rs"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
uniffi = { version = "0.23.0" }
uniffi_bindgen = "0.23.0"
# includes the 'thiserror' crate.
thiserror = "1.0"

[build-dependencies]
uniffi = { version = "0.23.0", features = [ "build", "cli"] }

[[bin]]
name = "uniffi-bindgen"
path = "uniffi-bindgen.rs"

[lib]
crate-type = ["cdylib"]
name = "library"
```

The ```[dependencies]``` section instructs cargo to load and use uniffi version 0.23.0.  (uniffi-bindgen is now built while building the app and is described below.). ```[build-dependencies]``` section instructs cargo to use uniffi version 0.23.0 and references the *build* and *cli* features.  *cli* is specified to allow building the uniffi-bindgen tool.  The ```[bin]``` section shows that a binary target called *uniffi-bindgen* will be created from a file called uniffi-bindgen.rs (located next to the Cargo.toml file).  The ```[lib]``` section allows developers to specify that the target is a cdylib and *name* is user defined.  For this tutorial, I have named it *library*, so it's clear what is being created. 

## Create The uniffi-bindgen ExecutableA previously described, the Cargo.toml file contains a reference to the uniffi-bindgen binary, which looks like this:

```
[[bin]]
name = "uniffi-bindgen"
path = "uniffi-bindgen.rs"
```

To generate the binary, create a new file called *uniffi-bindgen.rs* next to Cargo.toml and add:

```
fn main() {

    uniffi::uniffi_bindgen_main()
}
```

This instructs Cargo to launch the newly built uniffi-bindgen and tell it to call the uniffi-bindgen code contained within the uniffi crate.  The purpose of these steps is to give Cargo something to build / call that is wholly dependent on the specific versions contained within the particular uniffi crate.  This makes things simpler when new versions are installed, as well as, simplifying the build process.


To build the uniffi-bindgen binary, please execute the following:

```
cargo run
```

Once the build process completes, it should display something like this:

```
Finished dev [unoptimized + debuginfo] target(s) in 1m 01s
     Running `target/debug/uniffi-bindgen`
uniffi-bindgen 0.23.0
Scaffolding and bindings generator for Rust

USAGE:
    uniffi-bindgen <SUBCOMMAND>

OPTIONS:
    -h, --help       Print help information
    -V, --version    Print version information

SUBCOMMANDS:
    generate       Generate foreign language bindings
    help           Print this message or the help of the given subcommand(s)
    print-json     Print the JSON representation of the interface from a dynamic library
    scaffolding    Generate Rust scaffolding code
```


## Include the uniffi Rust Binding Code
Now, go into the src subdirectory, edit lib.rs, and add the following line near the top of the file (i.e., after the *use* statements):

```
uniffi::include_scaffolding!("library");
```

The uniffi include macro instructs the Rust compiler to load the scaffolding code, which will be generated during the build process.  The Rust functions being exported are listed below and will comprise the API for this library.    *Please note that this file will not have been created by this point, but it will be once the scaffolding and binding layers are generated (see below).*  

## Build Methods to Test Each Supported Type
Just like in Part 2, several public test functions will be created and added to the lib.rs file.  Each of the following test routines will provide a very simple function that will receive a specific data type as an input parameter and then return a corresponding data type as a result.  While Part 2 created test routines for each of the Rust data types currently supported by uniffi, this tutorial will discuss why some of those may not translate (through Kotlin) up to the Java test app.  In a nutshell, there are some inconsistencies between Java and Kotlin.  *(Please note:  for simplicity, no error checking is performed unless it is a necessary part of the demonstration.)*

### Add A Boolean Test Routine
Now, add the same boolean function that was created in Part 2.  The function receives a boolean value as an input parameter and returns its inverse.

```
pub fn bool_inc_test(value: bool) -> bool {

    return !value
}
```

### Add Some Integer Test Routines
In Rust, signed integers can be defined as 8-bit, 16-bit, 32-bit, or 64-bit values.  To demonstrate a simple test, each of the functions below will receive an integer value, increment it by 1, and return the result.  

```
pub fn i8_inc_test(value: i8) -> i8 {

    return value + 1
}

pub fn i16_inc_test(value: i16) -> i16 {

    return value + 1
}

pub fn i32_inc_test(value: i32) -> i32 {

    return value + 1
}

pub fn i64_inc_test(value: i64) -> i64 {

    return value + 1
}
```

### How About The Unsigned Integer Test Routines?
In Rust, unsigned values can be also defined as 8-bit, 16-bit, 32-bit, or 64-bit numerical values.  Since Kotlin also supports unsigned values, I have added them to the Rust library and the UDL file.  However, since Java does not natively support unsigned values, trying to call test routines using unsigned parameters will give a type error during the Java build process.  For that reason (and to stay with standard Java), I have omitted them from the Java test app and won't discuss them here.  However, it is worth noting that third party add-on packages do enable Java code to process unsigned values.  Experimenting with using some of those external packages to exchange unsigned values between Java and Kotlin would be a fun exercise for the reader.  


### Add A Float Test Routine
To test floating point values, create a test routine that accepts a float value, increments it by 1, and then returns the result.

```
pub fn float_inc_test(value: f32) -> f32 {

    return value + 1.0
}
```

### Add A Double Test Routine
To test double values, create a test routine that accepts a double value, increments it by 1, and then returns the result.

```
pub fn double_inc_test(value: f64) -> f64 {

    return value + 1.0
}
```

### Add A String Test Routine
For testing string values, create a test routine that accepts a string input value and then returns a concatenation of the input string with itself.


```
pub fn string_inc_test(value: String) -> String {

    return format!("{}{}", value, value);
}
```

### Add A Pass By Reference Test Routine
*Pass by reference* parameters pass allow programmers to pass references to values (rather than the values themselves) into a function without actually copying the referenced data.  Since Rust implements strict ownership rules, multiple functions (e.g., caller and called) cannot write to the same data element, simultaneously.  While this test function shows how *pass by reference* parameters are input and used, Rust's ownership rules constrain multiple write accesses.  For a more detailed view of the ownership rules, please see the [Rust Manual](https://doc.rust-lang.org/rust.html).  

As part of demonstrating *pass by reference* parameters, this test creates and uses a new data type structure.  The following *Point* structure defines a point value with an x-coordinate and a y-coordinate, which are each defined as 64-bit floating point values.  Add the following structure definition near the top of the lib.rs file:

```
#[derive(Debug)] 
pub struct Point {
    pub x: RwLock<f64>,
    pub y: RwLock<f64>,
}
```

The *RwLock* struct is used to enable Rust to control access to each member variable.  In this case, RwLock was chosen to allow many readers, but only one writer.  To use these values with RwLocks, it is necessary to provide access functions and not try to access them directly.  To do, this an *impl* body for the Point struct is required.  To accomplish this, please add the following immediately after the declaration of *struct Point*:

```
impl Point {

    fn new(x: f64, y: f64) -> Self {
        Point {
            x: RwLock::new(x),
            y: RwLock::new(y)
        }
    }

    fn set_x(self: Arc<Self>, x: f64) {
        *self.x.write().unwrap() = x;
    }

    fn get_x(&self) -> f64 {
        self.x.read().unwrap().clone()
    }

    fn set_y(self: Arc<Self>, y: f64) {
        *self.y.write().unwrap() = y;
    }

    fn get_y(&self) -> f64 {
        self.y.read().unwrap().clone()
    }
}
```

Next, create a test function that receives a Point input value by reference, modifies the member values (i.e., increments by 1), and returns.  After the function returns, the calling application will have the modified values within the data it previously allocated.  Please add the following code to test using parameters by reference" 

```
pub fn byref_inc_test(value: &Arc<Point>) -> () { 

    (Arc::clone(&value)).set_x(value.get_x() + 1.0);
    (Arc::clone(&value)).set_y(value.get_y() + 1.0);
}
```


### Add An Optional Test Routine
In Rust, optional values can represent either a valid value (of the specified type) or have the value of *None* (which shows that no type value is present).  Since Kotlin supports optional values, the corresponding code from Part 2 has been left in the Rust library and UDL file.  However, Java does not support optional values, so attempting to use them results in a build error.  For that reason, they have been omitted from TestApp.java.


### Add A Vector Test Routine
In Rust, a vector is analogous to a re-sizable array.  In this test example, create a function that receives a mutable vector of Strings (i.e., Vec<String>).  Inside the function, create a local variable *new_value* and initialize it with the value parameter.  Next, append another copy of the value parameter to *new_value*.  More simply stated, this function is returning a concatenation of two copies of the input value, as follows:

```
pub fn vector_inc_test(mut value: Vec<String>) -> Vec<String> {

    let mut new_value: Vec<String> = value.to_vec();
    new_value.append(&mut value);

    return new_value;
}
```

### Add A HashMap Test Routine
HashMaps, in Rust, are dictionaries of *key : value* pairs.  For this test, add a function that receives a HashMap with key : value pairs defined as HashMap<String, i32>.  In this function, clone the input value, add a new key : value pair (i.e., *"zero" : 0*), and then return the result as follows:

```
pub fn hash_map_inc_test(value: HashMap<String, i32>) -> HashMap<String, i32> {     // Only string keys are supported.

    let mut result = value.clone();
    result.insert(String::from("zero"), 0);

    return result;
}
```

### Add A Void Test Routine
When a Rust function returns a 'void' value (designated as '*( )*'), it is stating that no value of any type is returned.  Since this function doesn't returning anything, there's nothing to print in the test, so this is just showing how it's done.  Create a test routine that returns a void, as follows:

```
pub fn void_inc_test(_value: i32) -> () {

    return ();
}
```

### Add An Error Code Test Routine
Throwing and catching exceptions (errors) is common practice in modern programming languages.  In Rust, it is also possible to create custom exception types.  These exceptions can be *thrown* in an underlying library, pass through the uniffi scaffolding and language wrapper layers, and then be handled in an exception handler provided by the higher-level application.  

For example, ArithmeticError is a custom Rust error enum (borrowed from one of the uniffi examples) that can be thrown when the sum of two values overflows the range of 32-bit unsigned integers.  However, while the name *ArithmeticError* is available for programmers in Rust and Kotlin, it is a reserved word in Java and causes a build error when Java programmers attempt to use it.  For this reason, I have modified it slightly as *MyArithmeticError*.  With this change, please put the following error definition near the top of the lib.rs file:

```
#[derive(Debug, thiserror::Error)]
pub enum MyArithmeticError {
    #[error("Integer overflow on an operation with {a} and {b}")]
    IntegerOverflow { a: i32, b: i32 },
}
```

Once the MyArithmeticError enum (and IntegerOverflow member) has been defined, it can be used within lib.rs, as well as, in applications that import the Rust library.  In the following example, two 32-bit integers are added together and if the result overflows the 32-bit unsigned int range of values, then the ArithmeticError will be generated.

```
pub fn error_inc_test(a: i32, b: i32) -> Result<i32, MyArithmeticError> {

    let a1: i32 = a;
    a1.checked_add(b).ok_or(MyArithmeticError::IntegerOverflow { a, b })
}
```

## Create the UDL File
Just like in Part 1 and Part 2, once the Rust library is created and its API defined, it's time to create the UDL file.  The UDL file is also created in the library/src directory.  This file will define each the public functions, type structures, and custom errors created above.  The reason for creating a custom UDL representation of these items is that it makes it easier for uniffi to generate the scaffolding and language wrapper layers.  A byproduct of this process is that it also helps the programmer(s) to see each of the library's public members.

To create the UDL, start by creating a file called *library.udl* in the Rust library's *src* directory.  The uniffi naming convention is such that the name *'library'* is the same name chosen as the name of the project's library and '.udl' denotes that it is a uniffi UDL file.  In UDL, all of the API functions must be specified in the UDL file under the *namespace* block while the types and error definitions are declared outside of the namespace block. UDL reads like a pseudocode representation of the public interface.  The types used in this file adhere to the [UDL specification](https://mozilla.github.io/uniffi-rs/udl_file_spec.html).  UDL can be used to specify many other types, enumerations, structs, dictionaries, interfaces, objects, and errors, however, those are not covered in this tutorial. Please add the following lines to the new UDL file:

```
[Error]
enum MyArithmeticError {
    "IntegerOverflow",
};

interface Point {
    constructor(f64 x, f64 y);
    f64 get_x();

    [Self=ByArc]
    void set_x(f64 x);

    f64 get_y();
    
    [Self=ByArc]
    void set_y(f64 y);
};

namespace library {

    boolean bool_inc_test(boolean value);

    i8 i8_inc_test(i8 value);
    i16 i16_inc_test(i16 value);
    i32 i32_inc_test(i32 value);
    i64 i64_inc_test(i64 value);

    u8 u8_inc_test(u8 value);
    u16 u16_inc_test(u16 value);
    u32 u32_inc_test(u32 value);
    u64 u64_inc_test(u64 value);

    f32 float_inc_test(f32 value);

    f64 double_inc_test(f64 value);

    string string_inc_test(string value);

    void byref_inc_test([ByRef] Point value);

    i32? optional_type_inc_test(i32? value);

    sequence<string> vector_inc_test(sequence<string> value);

    record<DOMString, i32> hash_map_inc_test(record<DOMString, i32> value);

    void void_inc_test(i32 value);

    [Throws=MyArithmeticError]
    i32 error_inc_test(i32 a, i32 b);
};
```

In UDL, all of the API functions must be specified in the UDL file under the *namespace* block.  The UDL reads like a type of pseudocode that easily describes the function definition.  The types used in this file adhere to the [UDL specification](https://mozilla.github.io/uniffi-rs/udl_file_spec.html).  Outside of the namespace block, but in the same file, are the error type and interface (Object) definitions.


## Generate The Scaffolding Layer

The *scaffolding layer* is set of code that exposes the library's API and serializes the specified data types as an enhanced FFI layer.  In previous uniffi versions, the scaffolding layer used to be generated from the command terminal.  Starting in version 0.23.0, this is accomplished in the *build.rs* file, which cargo uses to perform build steps.  To do this, create build.rs next to Cargo.toml and add the following:

```
fn main() {

	uniffi::generate_scaffolding("./src/library.udl").unwrap();
}
```

This call will generate the scaffolding layer code from the library.udl file (created above) and will make it available for import into lib.rs. 


## Build the Rust Library

Go to the library sub-directory and type:

`cargo build`

This will build the Rust library according to the settings in Cargo.toml.  If everything is successful, the output should be similar to:

```
% cargo build
   Compiling library v0.1.0 (./ffi-tutorials/Wrapper_Data_Types/library)
    Finished dev [unoptimized + debuginfo] target(s) in 21.47s
```

Since we added a custom build.rs file (see above), building the Rust library will also create the uniffi-bindgen executable.


## Generating the Kotlin Language Wrapper

With the newly created *uniffi-bindgen*, we can create the Kotlin wrapper via the command line by entering:

 ```cargo run --bin uniffi-bindgen generate src/library.udl --language kotlin```

Executing this command will create *./src/uniffi/library/library.kt*, which contains the Kotlin wrapper code. 


## Generate a JAR File From the Kotlin Code

At this point, the Kotlin wrapper has been created from the Rust library.  In order to use the wrapper from within a Java app, it is necessary to build it into a JAR file.  For this step, please install the [Kotlin compiler](https://kotlinlang.org/docs/command-line.html).  Once installed, please go to the *./library* folder and invoke the Kotlin compiler to create a JAR file as follows (from the command line):

```kotlinc src/uniffi/library/library.kt -classpath ./jna-5.13.0.jar -d target/debug/library.jar```

Notice the inclusion of the Java Native Access (JNA) library.  When building from the command line, it is necessary to specify the JNA library in the classpath.  To get the JNA library, please download it from the [repository](https://mvnrepository.com/artifact/net.java.dev.jna/jna/5.13.0) and copy *jna-5.13.0.jar* into the local directory.  This copy step is only done for brevity and readability in this tutorial.  In practice, you will have installed the JNA library to a more standard location and will specify the actual path in your build tool.  For convenience, I have instructed kotlinc to output the resulting JAR file into the *./target/debug* folder.


## Java Application: Calling the Rust Library

With the Rust library, scaffolding layer, and Kotlin wrapper, we are ready to test importing them into a Java application.  To do this, make a directory called *java* next to the *library* directory.  Inside of the java directory, please create a file called *TestApp.java*.  To test each of the functions provided by the Rust library and supported by Java, please add the following to TestApp.java:

```
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
```

In these tests, initial values are created and passed into various library functions that do some simple calculations and then return the calculated value. For numeric values, the library functions increment the input value and return the calculated result.  For string functions, the library functions return a concatenation of the input string with itself.  For Vector and HashMap tests, the library functions return the input value with a new member added.  Finally, the exception handling test calls the errorIncTest( ) twice.  The first time errorIncTest( ) is called, it is called with valid input values in order to generate a successful result.  The second time errorInctest( ) is called, it is intentionally called with one value containing the maximum value of an Integer type, so that when added to the second input value, it will overflow the Integer range and generate an IntegerOverflow exception.


## Building the Java Test App
For standard build processing, a tool such as [Gradle](https://gradle.org) or [Maven](https://maven.apache.org/index.html) will be used to build the Java sources and bundle the requisite libraries.  However, for the purposes of this tutorial, I wanted to demonstrate each step, so I will perform the build functions manually via the command line.  To begin, please go into the *java* directory where the TestApp.java file is located.

To build and run the Java test app, the following dependencies must added to the bundle.  Please copy the following to *./java*:

1. **Java Native Access (JNA):** JNA provides some native code that enable Java apps to run more effectively on a specific platforms.  To do this, please copy *jna-5.13.0.jar* (previously downloaded) into *./java*.
2. **Kotlin Standard Library** The Kotlin Standard Library contains the basic code necessary to run Kotlin bytecode and to do so in a Java environment.  To do this, please [download](https://mvnrepository.com/artifact/org.jetbrains.kotlin/kotlin-stdlib-jdk8/1.8.21) and copy *kotlin-stdlib-1.8.21.jar* into *./java*.
3. **Library for uniffi** the dynamically-linked library for uniffi support has been built and is located in *./library/target/debug*.  Please copy *liblibrary.dylib* to *./java* and rename it to *libuniffi_library.dylib*.  (NOTE:  The renaming step is due to a naming issue with the uniffi build process and will be corrected in an upcoming version of uniffi.)
4. **Kotlin JAR File For The Rust Library** the Kotline JAR file created from the Rust library and Kotlin wrapper has been built and is located in *./library/target/debug*.  Please copy *library.lib* to *./java*.

To build the Java test app, please execute the following (via the command line) from within *./java*:

```javac -cp library.jar TestApp.java```

This will create the TestApp.class file, which represents the bytecode for the TestApp.java file.  Please note that it does not include the dependent library code.


## Running The Java Test Application 

At this point, everything has been built and all of the necessary resources have been copied into the *./java* folder.  To run the *TestApp*, please go to the *./java* folder and enter:

```java -cp ./library.jar:./jna-5.13.0.jar:./kotlin-stdlib-1.8.21.jar:./libuniffi_library.dylib:. TestApp```

If the library is successfully linked and the public functions correctly called, the following messages should be displayed:

```
 --- Running Tests --- 
Running boolean test...
Running signed int tests...
Running float test...
Running double test...
Running String test...
Running byRef test...
    initial: 
        X:  0.0
        Y:  0.0
    result: 
        X:  1.0
        Y:  1.0
byRef test passed
Running vector test...
Running HashMap test...
Running void return value test...
Running Error Code Test On Success test...
     Success!  Returned value = 1
Running Error Code Test On Failure test...
     Fail!  Returned value = uniffi.library.MyArithmeticException$IntegerOverflow: Integer overflow on an operation with 2147483647 and 1
 --- End of Tests ---
```


## Conclusion

Developing reusable libraries in Rust is an excellent way to build the business logic once and then reuse it natively across several languages and platforms.  While FFI makes it possible to call Rust libraries from a variety of different programming languages, it requires application developers to make C-language calls into linked libraries.  Since many developers are unfamiliar with C and its unique requirements (especially with memory management), it can be confusing and burdensome.  

The uniffi tool from Mozilla dramatically simplifies the software development process by automatically generating the scaffolding layer and building language-specific bindings, which simplify the integration effort for application developers.  Having completed this tutorial, you should now be ready to import Rust libraries generated with uniffi into other language environments, as well.  This presents many reusability benefits with the only requirement that implementers be aware of integration requirements between the languages used (e.g., Java and Kotlin).  
