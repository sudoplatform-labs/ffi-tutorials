# Creating Language Wrappers For Rust Libraries - Part 2


## Background
In the previous tutorial ([Creating Language Wrappers for Rust Libraries - Part 1](https://github.com/sudoplatform-labs/ffi-tutorials/tree/main/Wrapper_Intro)), methods were presented for creating platform-independent and programming language-independent libraries using the [Rust](https://www.rust-lang.org) programming language.  Part 1 also demonstrated how to install and use the [Mozilla uniffi](https://github.com/mozilla/uniffi-rs) tool to *automatically* generate language wrappers for Swift and Python. Test applications (for Swift and Python) were created and used to demonstrate how to import the Rust library using the generated language wrappers.  (Note:  some of the example material was adapted from various uniffi examples.)


## Tutorial

This tutorial will build upon the library and test applications created in Part 1 in order to demonstrate how each of the supported data type elements can be passed through the language wrappers to the linked Rust and how data types can be returned from the Rust library.  A description of each of the data types and now they correspond to equivalent types in other programming languages will also be discussed.  As in Part 1, the following will be created and discussed:

* Rust library
* UDL file
* Swift test app
* Python test app



## Mozilla's uniffi Tool Automates FFI Processes

As a review from Part 1, building a Rust library and language wrappers using the uniffi tools is done as follows:

1. Create a custom Rust library
	1. Expose the desired API for the library.  The API will consist of all top-level functions
	2. Setup a Cargo.toml file that specifies that the crate will be built as a dylib
	3. Build and test the library

2. Create a [*UDL*](https://mozilla.github.io/uniffi-rs/udl_file_spec.html) representation of each of the API functions
	1. UDL is a uniffi-specific design language that is a variation of Web Interface Definition Language (Web IDL)
	2. The UDL file will describe each of the top-level functions in the library

3. Use the uniffi tool to create a [*scaffolding layer*](https://mozilla.github.io/uniffi-rs/tutorial/Rust_scaffolding.html) for the library
	1. The scaffolding layer is a set of helper code that is used to make the top-level functions available to the foreign-language bindings

4. Create language-specific [bindings](https://mozilla.github.io/uniffi-rs/tutorial/foreign_language_bindings.html)
	1. This makes FFI calls look & feel like native code (e.g., Swift FFI feels like native Swift)

5. Import the scaffolding code, the language-specific code, and the generated library into a native application


## Creating the Rust Library
To get started, open a terminal window and create a project directory that will contain each of the library and applications for this tutorial.  In the terminal, navigate to the project directory and create a new rust library called *library*, as follows:

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

The ```[dependencies]``` section instructs cargo to load and use uniffi version 0.23.0.  (uniffi-bindgen is now built while building the app and is described below.). ```[build-dependencies]``` section instructs cargo to use uniffi version 0.23.0 and references the *build* and *cli* features.  *cli* is specified to allow building the uniffi-bindgen tool.  The ```[bin``` section shows that a binary target called *uniffi-bindgen* will be created from a file called uniffi-bindgen.rs (located next to the Cargo.toml file).  The ```[lib]``` section allows developers to specify that the target is a cdylib and *name* is user defined.  For this tutorial, I have named it *library*, so it's clear what is being created. 

## Create The uniffi-bindgen Executable

A previously described, the Cargo.toml file contains a reference to the uniffi-bindgen binary, which looks like this:

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
cargo run --features=uniffi/cli --bin uniffi-bindgen
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
Now, go into the src sub-directory, edit lib.rs, and add the following line to the **top** of the file:

```
uniffi::include_scaffolding!("library");
```

The uniffi include macro instructs the Rust compiler to load the scaffolding code, which will be generated during the build process.  The Rust functions being exported are listed below and will comprise the API for this library.    *Please note that this file will not have been created by this point, but it will be once the scaffolding and binding layers are generated (see below).*  

## Build Methods to Test Each Supported Type
In order to test the capabilities of the language wrappers, several public test functions will be created and added to the lib.rs file.  Each of the following test routines will provide a very simple function that will receive a specific data type as an input parameter and then return a corresponding data type as a result.  This series of test routines will use each of the Rust data types that is currently supported by uniffi.  *(Please note:  for simplicity, no error checking is performed unless it is a necessary part of the demonstration.)*

### Add A Boolean Test Routine
Now, add the same boolean function that was created in Part 1.  The function receives a boolean value as an input parameter and returns its inverse.

```
fn bool_inc_test(value: bool) -> bool {

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

### Add Some Unsigned Integer Test Routines
In Rust, unsigned integers can be also defined as 8-bit, 16-bit, 32-bit, or 64-bit values.  To demonstrate a simple test, each of the functions below will receive an unsigned int value, increment it by 1, and return the result.  


```
pub fn u8_inc_test(value: u8) -> u8 {

    return value + 1
}

pub fn u16_inc_test(value: u16) -> u16 {

    return value + 1
}

pub fn u32_inc_test(value: u32) -> u32 {

    return value + 1
}

pub fn u64_inc_test(value: u64) -> u64 {

    return value + 1
}
```

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
In Rust, optional values can represent either a valid value (of the specified type) or have the value of *None* (which shows that no type value is present).  Optional values are useful in functions that may return either a valid type value or may have failed to create one.  Please add the following routine, which tests the validity of the input value and increments its value and then returns the result:

```
pub fn optional_type_inc_test(value: Option<i32>) -> Option<i32> {

    let r_value: Option<i32>;

    match value {
        Option::Some(val) => 
            r_value = Some(val + 1),
        Option::None =>
            r_value = None
    };

    return r_value
}  
```

### Add A Vector Test Routine
In Rust, a vector is analagous to a re-sizable array.  In this test example, create a function that receives a mutuable vector that will contain Strings (i.e., Vec<String>), creates a duplicate of the input vector, and appends the input value to the newly created value.  More simply stated, this function is returning the concatenation of a copy of the input value with itself.

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
When a Rust function returns a 'void' value (designated as '*( )*'), it is stating that no value of any type is returned.  Create a test routine that returns a void, as follows:

```
pub fn void_inc_test(_value: i32) -> () {

    return ();
}
```

### Add An Error Code Test Routine
Throwing and catching exceptions (errors) is common practice in modern programming languages.  In Rust, it is also possible to create custom exception types.  These exceptions can be *thrown* in an underlying library, pass through the uniffi scaffolding and language wrapper layers, and then be handled in an exception handler provided by the higher-level application.  

For example, ArithmeticError is a custom Rust error (borrowed from one of the uniffi examples) that can be thrown when the sum of two values overflows the range of 64-bit unsigned integers.  Please put the following error definition near the top of the lib.rs file:

```
#[derive(Debug, thiserror::Error)]
pub enum ArithmeticError {
    #[error("Integer overflow on an operation with {a} and {b}")]
    IntegerOverflow { a: u64, b: u64 },
}
```

Once ArithmeticError has been defined, it can be used within lib.rs, as well as, in applications that import the Rust library.  In the following example, two 64-bit integers are added together and if the result overflows the 64-bit unsigned int range of values, then the ArithmeticError will be generated.

```
pub fn error_inc_test(a: u64, b: u64) -> Result<u64, ArithmeticError> {

    let a1: u64 = a;
    a1.checked_add(b).ok_or(ArithmeticError::IntegerOverflow { a, b })
}
```

## Create the UDL File
Just like in Part 1, once the Rust library is created and its API defined, it's time to create the UDL file.  The UDL file is also created in the library/src directory.  This file will define each the public functions, type structures, and custom errors created above.  The reason for creating a custom UDL representation of these items is that it makes it easier for uniffi to generate the scaffolding and language wrapper layers.  A byproduct of this process is that it also helps the programmer(s) to see each of the library's public members.

To create the UDL, start by creating a file called *library.udl*.  The uniffi naming convention is such that the name *'library'* is the same name chosen as the name of the project's library and '.udl' denotes that it is a uniffi UDL file.  In UDL, all of the API functions must be specified in the UDL file under the *namespace* block while the types and error definitions are declared outside of the namespace block. UDL reads like a pseudocode representation of the public interface.  The types used in this file adhere to the [UDL specification](https://mozilla.github.io/uniffi-rs/udl_file_spec.html).  UDL can be used to specify many other types, enumerations, structs, dictionaries, interfaces, objects, and errors, however, those are not covered in this tutorial. Please add the following lines to the new UDL file:

```
[Error]
enum ArithmeticError {
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

    [Throws=ArithmeticError]
    u64 error_inc_test(u64 a, u64 b);
};
```

In UDL, all of the API functions must be specified in the UDL file under the *namespace* block.  The UDL reads like a type of pseudocode that easily describes the function definition.  The types used in this file adhere to the [UDL specification](https://mozilla.github.io/uniffi-rs/udl_file_spec.html).


## Generate The Scaffolding Layer

The *scaffolding layer* is set of code that exposes the library's API and serializes the specified data types as an enhanced FFI layer.  In previous uniffi versions, the scaffolding layer used to be generated from the command terminal.  Starting in version 0.23.0, this is accomplished in the *build.rs* file, which cargo uses to perform build steps.  To do this, create build.rs next to Cargo.toml and add the following:

```
fn main() {

	uniffi::generate_scaffolding("./src/library.udl").unwrap();
}
```

This call will generate the scaffolding layer code from the library.udl file created above and will make it available for import into lib.rs at build time. 


## Build the Rust Library

Go to the library sub-directory and type:

`cargo build`

This will build the rust library according to the settings in Cargo.toml.  If everything is successful, the output should be similar to:

```
% cargo build
   Compiling library v0.1.0 (./ffi-tutorials/Wrapper_Data_Types/library)
    Finished dev [unoptimized + debuginfo] target(s) in 21.47s
```

## Testing the Rust Library

It's always good practice to test a library before delivering it to other code that links to it.  To test the library just created, please add the following test functions after the last library function:

```
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    pub fn internal() {

        println!("\n\n----- Start of Tests -----");
        print!("Running boolean test...");
        assert_eq!(false, bool_inc_test(true));
        println!("Passed");

        print!("Running signed int tests...");
        assert_eq!(1, i8_inc_test(0));
        assert_eq!(1, i16_inc_test(0));
        assert_eq!(1, i32_inc_test(0));
        assert_eq!(1, i64_inc_test(0));
        println!("Passed");

        print!("Running unsigned int tests...");
        assert_eq!(1, u8_inc_test(0));
        assert_eq!(1, u16_inc_test(0));
        assert_eq!(1, u32_inc_test(0));
        assert_eq!(1u64, u64_inc_test(0));
        println!("Passed");

        print!("Running float test...");
        let float_value: f32 = 0.0;
        assert_eq!(float_value + 1.0, float_inc_test(float_value));
        println!("Passed");

        print!("Running double test...");
        let double_value: f64 = 0.0;
        assert_eq!(double_value + 1.0, double_inc_test(double_value));
        println!("Passed");

        print!("Running String test...");
        let message: String = "Hello World!".to_string();
        let target_message: String = format!("{}{}", message, message);
        assert_eq!(target_message, string_inc_test(message.clone()));
        println!("Passed");

        println!("Running byRef test...");
        let x0: f64 = 1.0;
        let y0: f64 = 2.0;
        let byref_value = Arc::new(Point::new(x0, y0));
        
        println!("    initial: ");
        println!("        X:  {}", byref_value.get_x());
        println!("        Y:  {}", byref_value.get_y());
        byref_inc_test(&byref_value);
        println!("    result: ");
        println!("        X:  {}", byref_value.get_x());
        println!("        Y:  {}", byref_value.get_y());
        if (byref_value.get_x() == (x0 + 1.0)) &&
            (byref_value.get_y() == (y0 + 1.0)) {
            println!("    byRef test Passed");
        } else {
            println!("    byRef test Failed");
        }

        print!("Running vector test...");
        let my_array: Vec<String> = vec!["one".to_string(), "two".to_string(), "three".to_string()];
        let mut target_my_array: Vec<String> = my_array.to_vec();
        target_my_array.append(&mut my_array.clone());
        assert_eq!(target_my_array, vector_inc_test(my_array.clone()));
        println!("Passed");
        
        print!("Running HashMap test...");
        let mut initial_hash_map: HashMap<String, i32> = 
            [("one".to_string(), 1), 
            ("two".to_string(), 2), 
            ("three".to_string(), 3)]
            .iter().cloned().collect();
        let result_hash_map = hash_map_inc_test(initial_hash_map.clone());
        initial_hash_map.insert(String::from("zero"), 0);
        assert_eq!(initial_hash_map, result_hash_map);
        println!("Passed");

        print!("Running void test...");
        assert_eq!((), void_inc_test(0));
        println!("Passed");
        
        // ----- Error Code Test On Success -----
        print!("Running Error Code Test On Success test...");
        let value_1: i32 = 0;
        let value_2: i32 = 5;
        let r_value: Result<i32, MyArithmeticError> = error_inc_test(value_1, value_2);
        if r_value.is_ok() {
            println!("Passed");
            println!("     Returned value = {:?}", r_value.unwrap());
        }
        else {
            println!("Passed");
            println!("     Returned value = {:?}", r_value.unwrap_err());
        }

        // ----- Error Code Test On Failure -----
        print!("Running Error Code Test On Failure test...");
        let value_1: i32 = i32::MAX;
        let value_2: i32 = 1;
        let r_value: Result<i32, MyArithmeticError> = error_inc_test(value_1, value_2);
        if r_value.is_ok() {
            println!("Passed");
            println!("     Returned value = {:?}", r_value.unwrap());
        }
        else {
            println!("Passed");
            println!("     Returned value = {:?}", r_value.unwrap_err());
        }

        println!("----- End of Tests -----\n");
    }
}
```

To test the Rust library by itself, please enter the following on the command line:

```cargo test -- --nocapture```

This command instructs cargo to build the library and execute the test commands.  The ``` -- --nocapture``` portion instructs cargo to display anything printed using the ```println!``` statements in the test code.  If everything builds and runs correctly, you should see output similar to the following:

```
% cargo test -- --nocapture
   Compiling library v0.1.0 (/Users/XXXXXX/ffi-tutorials/Wrapper_Data_Types/library)
    Finished test [unoptimized + debuginfo] target(s) in 1.54s
     Running unittests src/lib.rs (target/debug/deps/library-4824b9037f064677)

running 1 test
test tests::internal ... 

----- Start of Tests -----
Running boolean test...Passed
Running signed int tests...Passed
Running unsigned int tests...Passed
Running float test...Passed
Running double test...Passed
Running String test...Passed
Running byRef test...
    initial: 
        X:  1
        Y:  2
    result: 
        X:  2
        Y:  3
    byRef test Passed
Running vector test...Passed
Running HashMap test...Passed
Running void test...Passed
Running Error Code Test On Success test...Passed
     Returned value = 5
Running Error Code Test On Failure test...Passed
     Returned value = IntegerOverflow { a: 2147483647, b: 1 }
----- End of Tests -----

ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests uniffi-bindgen.rs (target/debug/deps/uniffi_bindgen-950cf3f13364c569)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

% 
```


## Genrating a Swift Language Wrapper

At this point, the newly created *uniffi-bindgen* can be called with:

 ```cargo run --features=uniffi/cli --bin uniffi-bindgen [args]```

where *args* refers to the language wrapper being created.  So, for Swift, the call would look like 

```cargo run --bin uniffi-bindgen generate src/library.udl --language swift```

Executing this command will create *libraryFFI.h*, *libraryFFI.modulemap*, and (for Swift) *library.swift*.  *library.swift* is a file of ~846 lines of code that contains the Swift wrapper code.  As an example, the function ```boolIncTest( )``` will appear as follows:

```
621  public func boolIncTest(value: Bool) -> Bool {
622      return try! FfiConverterBool.lift(
623          try!
624  
625              rustCall {
626                  library_635_bool_inc_test(
627                      FfiConverterBool.lower(value), $0
628                  )
629              }
630      )
631  }
```

This code calls the FFI code (generated by uniffi) that performs the actual functions of calling into the library, sending / retrieving parameters, etc.  For fun, feel free to browse through the rest of the *library.swift* (or other language) file to see the FFI complexity that is saved by uniffi.  While it is definately possible to craft the FFI code by hand, it is a steep climb for application programmers who are not also C-programmers.  For that reason, a language-specific wrapper function definately simplifies calls into the library.

Please note that the Swift function has been formatted in the style of other Swift source code -- even the name has been converted from *snake case* (used in Rust) to *camel case* (used in Swift).  Additionally, this Swift function invokes (on line 626) the function, library\_635\_bool\_inc\_test( ), that was generated during the scaffolding creation step during the build process as described above. 

## Generating a Python Language Wrapper

To generate the Python language wrapper, run 

```cargo run --bin uniffi-bindgen generate src/library.udl --language python```

Executing this command will create *library.py*, which is a file of ~900 lines of code that contains the Python wrapper code.  As an example, the function ```bool_inc_test( )``` will appear as follows:


```
731  def bool_inc_test(value):
432      value = bool(value)
433    
434      return FfiConverterBool.lift(rust_call(_UniFFILib.library_eb66_bool_inc_test,
435          FfiConverterBool.lower(value)))
```

This code calls other FFI code (generated by uniffi) that performs the actual functions of calling into the library, sending / retrieving parameters, etc.  For fun, feel free to browse through the rest of the *library.py* file to see the FFI complexity that is saved by uniffi.

Please note that the Python function has been formatted in the style of other Python source code.  Additionally, this Python function invokes (on line 611) the function, \_UniFFILib.library\_eb66\_bool\_inc\_test, that was generated in during the scaffolding creation step of the build process as desribed above.  

## Swift Application: Calling the Rust Library

Once the library has been created, the scaffolding layer generated, and the Swift language wrapper generated, it is time to test importing the library into a Swift application.  To test this part of the tutorial, a macOS Swift app will be created.  To create the test app, do the following:

1. Launch Xcode and select File | New | Project  
2. Click *macOS* for the new project template
3. Select *Command Line Tool* and click *Next*
4. Name the project *swift\_test\_app* and click *Next*
5. A dialog box will appear asking where to save the project.  Select the main tutorial directory used for this tutorial and press *Create*

The preceeding steps will result in an empty, but runnable, Swift-based command line tool for macOS.  Next, the library must be linked and the scaffolding layer and language bindings must be added to the Xcode project, as follows:

1. In Xcode, select the target *swift_test_app*, select *General*, and add the Rust library (../library/target/debug/liblibrary.dylib) to the *Frameworks and Libraries* section, as follows:
![](./docs/xcode_project_library.png)
2. Add the directory containing the Rust library (dylib) to the Xcode project's *Library Search Paths*
3. Add the Swift language files generated by uniffi above.  The files to be added include
	1. libraryFFI.h
	2. libraryFFI.modulemap
	3. library.swift

	![](./docs/xcode_project_files.png)
4. Add the bridging header to the Xcode target by adding *../library/src/libraryFFI.h* to *Swift Compiler - General*

At this point, the test app should import the required files, link to the library, and run ... without doing anything.  To test each of the functions provided by the library, it is necessary to add the Swift function calls to *main.swift*, as follows:

```
  1 //
  2 //  main.swift
  3 //  test_app
  4 //
  5 //  Created by Steven H. McCown on 2/9/21.
  6 //
  7 
  8 import Foundation
  9 
 10 print(" --- Running Tests --- ")
 11 
 12 print("Running boolean test...")
 13 let valueBool: Bool = false
 14 var resultBool: Bool = boolIncTest(value: valueBool)
 15 assert(!valueBool == resultBool, "Bool test failed")
 16 
 17 
 18 print("Running signed int tests...");
 19 let valueI8: Int8 = 0;
 20 var resultI8: Int8 = i8IncTest(value: valueI8);
 21 assert(resultI8 == (valueI8 + 1), "i8 test failed");
 22 
 23 let valueI16: Int16 = 0;
 24 var resultI16: Int16 = i16IncTest(value: valueI16);
 25 assert(resultI16 == (valueI16 + 1), "i16 test failed");
 26 
 27 let valueI32: Int32 = 0;
 28 var resultI32: Int32 = i32IncTest(value: valueI32);
 29 assert(resultI32 == (valueI32 + 1), "i32 test failed");
 30 
 31 let valueI64: Int64 = 0;
 32 var resultI64: Int64 = i64IncTest(value: valueI64);
 33 assert(resultI64 == (valueI64 + 1), "i64 test failed");
 34 
 35 
 36 print("Running unsigned int tests...");
 37 let valueU8: UInt8 = 0;
 38 var resultU8: UInt8 = u8IncTest(value: valueU8);
 39 assert(resultI8 == (valueI8 + 1), "u8 test failed");
 40 
 41 let valueU16: UInt16 = 0;
 42 var resultU16: UInt16 = u16IncTest(value: valueU16);
 43 assert(resultI16 == (valueI16 + 1), "u16 test failed");
 44 
 45 let valueU32: UInt32 = 0;
 46 var resultU32: UInt32 = u32IncTest(value: valueU32);
 47 assert(resultI32 == (valueI32 + 1), "u32 test failed");
 48 
 49 let valueU64: UInt64 = 0;
 50 var resultU64: UInt64 = u64IncTest(value: valueU64);
 51 assert(resultI64 == (valueI64 + 1), "u64 test failed");
 52 
 53 
 54 print("Running float test...");
 55 let floatValue: Float32 = 0.0;
 56 assert(floatIncTest(value: floatValue) == (floatValue + 1.0), "float test failed");
 57 
 58 
 59 print("Running double test...");
 60 let doubleValue: Double = 0.0;
 61 assert(doubleIncTest(value: doubleValue) == (doubleValue + 1.0), "double test failed");
 62 
 63 
 64 print("Running String test...");
 65 let message: String = "Hello World!";
 66 let targetMessage: String = "\(message)\(message)";
 67 assert(stringIncTest(value: message) == targetMessage, "string test failed");
 68 
 69 
 70 print("Running byRef test...");
 71 let x0 = 1.0;
 72 let y0 = 2.0;
 73 let byrefValue: Point = Point(x: x0, y: y0);
 74 byrefIncTest(value: byrefValue);
 75 assert(byrefValue.getX() == (x0 + 1.0), "byRef test failed");
 76 assert(byrefValue.getY() == (y0 + 1.0), "byRef test failed");
 77 
 78 
 79 print("Running option type test...");
 80 let optionalValue : Int32 = 0;
 81 var optionalResult : Int32 = optionalTypeIncTest(value: optionalValue) ?? -1;
 82 assert(optionalResult == (optionalValue + 1), "optional (Int32) test failed");
 83 
 84 
 85 print("Running vector test...");
 86 let arrayValue: [String] = ["one", "two", "three"]
 87 var arrayResult: [String] = []
 88 arrayResult = vectorIncTest(value: arrayValue)
 89 assert(arrayResult == (arrayValue + arrayValue), "Vector (array) test failed")
 90 
 91 
 92 print("Running HashMap test...");
 93 var arrayDictionaryValue = [String : Int32] ()
 94 arrayDictionaryValue["one"] = 1
 95 arrayDictionaryValue["two"] = 2
 96 arrayDictionaryValue["three"] = 3
 97 var arrayDictionaryResult = [String : Int32] ()
 98 arrayDictionaryResult = hashMapIncTest(value: arrayDictionaryValue)
 99 arrayDictionaryValue["zero"] = 0;
100 assert(arrayDictionaryValue == arrayDictionaryResult, "HashMap (Dictionary) test failed")
101 
102 
103 print("Running void test...")
104 let voidValue : Int32 = 0
105 var voidResult : () = voidIncTest(value: voidValue)
106 assert(voidResult == (), "Void test failed")
107 
108 
109 print("Running Error Code Test On Success test...");
110 let value1: UInt64 = 0;
111 let value2: UInt64 = 1;
112 do {
113     let rValue = try errorIncTest(a: value1, b: value2);
114     print("     Returned value = \(rValue)");
115 } catch (let exception) {
116     print("     Returned value = \(exception)");
117 }
118 
119 
120 print("Running Error Code Test On Failure test...");
121 let val1: UInt64 = UInt64.max;
122 let val2: UInt64 = 1;
123 do {
124     let rValue = try errorIncTest(a: val1, b: val2);
125     print("     Returned value = \(rValue)");
126 } catch (let exception) {
127     print("     Returned value = \(exception)");
128 }
129 
130 
131 print(" --- End of Tests ---\n");
```

In these tests, initial values a created and passed into the various library functions, which do some simple calculations and then return the calculated value. For numeric values, the library functions increment the input value and return the calculated result.  For string functions, the library functions return a concatenation of the input string with itself.  For Vector and HashMap tests, the library functions return the input value with a new member added.  Finally, the exception handling test calls the errorIncTest( ) twice.  The first time errorIncTest( ) is called, it is called with valid input values in order to generate a successful result.  The second time errorInctest( ) is called, it is intentionally called with one value containing the maximum value of a UInt64 type, so that when added to the second input value, it will overflow the UInt64 range and generate an IntegerOverflow exception.

If the library is successfully linked and the public functions correctly called, the following messages should be displayed:

```
 --- Running Tests --- 
Running boolean test...
Running signed int tests...
Running unsigned int tests...
Running float test...
Running double test...
Running String test...
Running byRef test...
Running option type test...
Running vector test...
Running HashMap test...
Running void test...
Running Error Code Test On Success test...
     Returned value = 1
Running Error Code Test On Failure test...
     Returned value = IntegerOverflow(message: "Integer overflow on an operation with 18446744073709551615 and 1")
 --- End of Tests ---
```
<BR>

## Python Application: Calling the Rust Library

Creating the Python test application is much simpler than the Swift version, because it does not need a project configuration.  To create the Python test application, do the following:

1. Go to the tutorial main directory and create a sub-directory called *python_test_app* and navigate into it
2. Copy the required library files into *python_test_app* (or they can be referenced via command line parameters)
	1. ./library/target/debug/liblibrary.dylib.dylib (*Note:  in this version of uniffi, this library must be renamed to libuniffi_library.dylib.  This should be fixed in an upcoming version.*)
	2. ./library/src/library.py
3. Create the main Python application file (main.py).  Natively, Python provides int, float, and complex as its supported numeric value types.  Since the Rust library generated above uses numeric values with specific bit lengths and sign values, it is necessary to import a third-party library.  For these tests, *numpy* is used to provide finer control over numeric type values.  (If *numpy* is not installed, please install it by typing ```pip3 install numpy``` on the command line.)  Please add the following to main.py:

```
  1 import numpy
  2 
  3 import library
  4 
  5 print("\n --- Running Tests --- \n")
  6 
  7 print("Running boolean test...", end="  ")
  8 valueBool = False
  9 resultBool = library.bool_inc_test(valueBool)
 10 assert ((not valueBool) == resultBool), "Bool test failed"
 11 print("Passed")
 12 
 13 print("Running signed int tests...", end="  ")
 14 valueI8: numpy.int8 = 0
 15 resultI8: numpy.int8 = library.i8_inc_test(valueI8)
 16 assert (resultI8 == (valueI8 + 1)), "i8 test failed"
 17 
 18 valueI16: numpy.int16 = 0
 19 resultI16: numpy.int16 = library.i16_inc_test(valueI16)
 20 assert (resultI16 == (valueI16 + 1)), "i16 test failed"
 21 
 22 valueI32: numpy.int32 = 0
 23 resultI32: numpy.int32 = library.i32_inc_test(valueI32)
 24 assert (resultI32 == (valueI32 + 1)), "i32 test failed"
 25 
 26 valueI64: numpy.int64 = 0
 27 resultI64: numpy.int64 = library.i64_inc_test(valueI64)
 28 assert (resultI64 == (valueI64 + 1)), "i64 test failed"
 29 print("Passed")
 30 
 31 
 32 print("Running unsigned int tests...", end="  ")
 33 valueU8: numpy.uint8 = 0
 34 resultU8: numpy.uint8 = library.u8_inc_test(valueU8)
 35 assert (resultU8 == (valueU8 + 1)), "u8 test failed"
 36 
 37 valueU16: numpy.uint16 = 0
 38 resultU16: numpy.uint16 = library.u16_inc_test(valueU16)
 39 assert (resultU16 == (valueU16 + 1)), "u16 test failed"
 40 
 41 valueU32: numpy.uint32 = 0
 42 resultU32: numpy.uint32 = library.u32_inc_test(valueU32)
 43 assert (resultU32 == (valueU32 + 1)), "u32 test failed"
 44 
 45 valueU64: numpy.uint64 = 0
 46 resultU64: numpy.uint64 = library.u64_inc_test(valueU64)
 47 assert (resultU64 == (valueU64 + 1)), "u64 test failed"
 48 print("Passed")
 49 
 50 
 51 print("Running float test...", end="  ")
 52 floatValue: numpy.float32 = 0.0
 53 assert (library.float_inc_test(floatValue) == (floatValue + 1.0)), "float test failed"
 54 print("Passed")
 55 
 56 
 57 print("Running double test...", end="  ")
 58 doubleValue: numpy.double = 0.0
 59 assert (library.double_inc_test(doubleValue) == (doubleValue + 1.0)), "double test failed"
 60 print("Passed")
 61 
 62 
 63 print("Running String test...", end="  ")
 64 message = "Hello World!"
 65 targetMessage = message + message
 66 assert (library.string_inc_test(message) == targetMessage), "string test failed"
 67 print("Passed")
 68 
 69 
 70 print("Running byRef test...", end="\t")
 71 x0: numpy.int32 = 1.0
 72 y0: numpy.int32 = 2.0
 73 byrefValue: library.Point = library.Point(x0, y0)
 74 library.byref_inc_test(byrefValue)
 75 assert (byrefValue.get_x() == (x0 + 1.0)), "byRef test failed"
 76 assert (byrefValue.get_y() == (y0 + 1.0)), "byRef test failed"
 77 print("Passed")
 78 
 79 
 80 print("Running option type test (test for int32)...", end="  ")
 81 optionalValue : numpy.int32 = 0
 82 optionalResult : numpy.int32 = library.optional_type_inc_test(optionalValue)
 83 if optionalResult != None:
 84     assert(optionalResult == (optionalValue + 1)), "optional type test returned None"
 85     print("Passed")
 86     print("\tReturned value = " + str(optionalResult))
 87 else:
 88     print("Failed")
 89     print("\tReturned value = None when an int32 was expected")
 90 
 91 
 92 print("Running option type test (test for None)...", end="  ")
 93 optionalValue : numpy.int32 = None
 94 optionalResult : numpy.int32 = library.optional_type_inc_test(optionalValue)
 95 if optionalResult != None:
 96     print("Failed")
 97     print("\tReturned value = " + str(optionalResult) + " when None was expected")
 98 else:
 99     print("Passed")
100     print("\tReturned value = None")
101 
102 
103 print("Running vector test...", end="  ");
104 arrayValue = ["one", "two", "three"]
105 arrayResult = library.vector_inc_test(arrayValue)
106 assert(arrayResult == (arrayValue + arrayValue)), "Vector (array) test failed"
107 print("Passed")
108 print ("\tarrayResult = ", end=" ")
109 print (' '.join(arrayResult))
110 
111 
112 print("Running HashMap test...", end="  ");
113 arrayDictionaryValue = {
114     "one" : 1,
115     "two" : 2,
116     "three" : 3 }
117 arrayDictionaryResult = library.hash_map_inc_test(arrayDictionaryValue)
118 arrayDictionaryValue["zero"] = 0
119 assert(arrayDictionaryValue == arrayDictionaryResult), "HashMap (Dictionary) test failed"
120 print("Passed")
121 
122 print("Running void test...", end="  ")
123 voidValue : numpy.int32 = 0
124 voidResult = library.void_inc_test(voidValue)
125 assert (voidResult == None), "Void test failed"
126 print("Passed")
127 
128 
129 print("Running Error Code Test On Success test...", end="  ")
130 value1: numpy.uint64 = 0
131 value2: numpy.uint64 = 1
132 try:
133     rValue = library.error_inc_test(value1, value2)
134     print("Passed")
135     print("\tReturned value = " + str(rValue))
136 except ArithmeticError.IntegerOverflow:
137     print("Failed")
138     print("\tReturned value = " + str(exception))
139 
140 
141 print("Running Error Code Test On Failure test...", end="  ")
142 value1: numpy.uint64 = numpy.iinfo(numpy.uint64).max
143 value2: numpy.uint64 = 1
144 try:
145     rValue = library.error_inc_test(value1, value2)
146     print("Failed")
147     print("\tReturned value = " + str(rValue))
148 except library.ArithmeticError.IntegerOverflow as ex:
149     print("Passed")
150     print("\tReturned value = error" + ex.args[0])
151 
152 
153 print("\n --- End of Tests ---\n")
```

To execute main.py, type

`python3 main.py`

If the test routines successfully invoked the library routines, the following output should be displayed int the terminal:

```
% python3 main.py

 --- Running Tests --- 

Running boolean test...  Passed
Running signed int tests...  Passed
Running unsigned int tests...  Passed
Running float test...  Passed
Running double test...  Passed
Running String test...  Passed
Running byRef test...	Passed
Running option type test (test for int32)...  Passed
	Returned value = 1
Running option type test (test for None)...  Passed
	Returned value = None
Running vector test...  Passed
	arrayResult =  one two three one two three
Running HashMap test...  Passed
Running void test...  Passed
Running Error Code Test On Success test...  Passed
	Returned value = 1
Running Error Code Test On Failure test...  Passed
	Returned value = errorRustError(code=1, message=Integer overflow on an operation with 18446744073709551615 and 1)

 --- End of Tests ---

% 
```

## Conclusion

Developing reusable libraries in Rust is an exellent way to build the business logic once and then reuse it across several languages and platforms.  While FFI makes it possible to call Rust libraries from a variety of different programming languages, its requirement for application developers to make C-language calls into linked libraries is confusing and burdensome.  The uniffi tool from Mozilla dramatically simplifies the software development process by automatically generating the scaffolding layer and building language-specific bindings, which simplify the integration effort for application developers.
