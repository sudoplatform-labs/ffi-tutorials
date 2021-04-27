# Simple Rust Library Foreign Function Interface


## Overview

Modern software development uses statically-linked or dynamically-linked libraries to facilitate code reuse across applications.  When libraries are created using programming languages that are different from the importing applications, the library is considered *foreign code* by the application.  In order to communicate between the application and library, a common calling and data exchange protocol must be established.  This common protocol is referred to as a [*Foreign Function Interface (FFI)*](https://en.wikipedia.org/wiki/Foreign_function_interface).  

This tutorial demonstrates how to create a Rust library with a single exportable function that receives a C-String, converts it to Rust's native string format, counts the number of bytes, and returns an unsigned integer containing the number of characters in the input string.  An FFI is created, so that the library function can be made accessible to an integrating application.  A test application, written in the C programming language, is used to demonstrate how to interface with the Rust library.


## Rust Installation

In order to build and run this example, it is first necessary to install the Rust development environment.  Rust is easily installed and executed via a command-line terminal.

1. Curl will be used to install Rust.  To install curl, type:
	
	 `brew install curl`
	 
2. Install Rust and the update tool Rustup.  To install these, type:
 
	 `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
	 
3. To test the installation, type:

	 `rustc --version`

Note:  for additional details on the installation process, please see: [https://www.rust-lang.org/tools/install](https://www.rust-lang.org/tools/install) 


## Building the Sample from GitHub
To quickly build and test the sample code, please do the following:

1. Download the application code:

	 `git clone git@github.com:sudoplatform-labs/ffi-tutorials.git`
	 
2. Build the library
	1. Navigate into the "ffi-tutorial/countchars" sub-directory and type
	
		`cargo build`
		
	2. The created libraries (libcharcount.a and libcharcount.dylib) will be created in ./target/debug/
3. Build and run the sample C-language test app
	1. Navigate into the project sub-directory "test_app/" and build the test application by typing:
		
		`gcc main.c -L ../countchars/target/debug -lcountchars -o main`
		
	2. Run the test app by typing:
		
		`./main`
		
	2. The output displayed should show:
	
		*There are 12 chars in "Hello World!"*

## Create Sample By Hand
To create the FFI Tutorial library and applications from scratch, please do the following:

1. Create a sub-directory for the test library and app by typing the following at the command line:

	1. `mkdir FFI_Tutorial`

	2. `cd FFI_Tutorial`

2. Create the Rust library
	1. Create a new Rust library by typing:
	
		1. `cargo new --lib countchars`
		
		2. `cd countchars`
		
	2. Add the following to the Cargo.toml file (omitting line numbers):
		
		```
		 1 [package]
		 2 name = "countchars"
		 3 version = "0.1.0"
		 4 authors = ["Steven H. McCown <smccown@anonyome.com>"]
		 5 edition = "2018"
		 6 
		 7 # See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html
		 8 
		 9 [lib]
		10 name = "countchars"
		11 crate-type = ["staticlib", "dylib"]
		12 
		13 [dependencies]
		```
		
	3. Now, create ./src/lib.rs and add the following (omitting line numbers):

		```
		 1 use std::os::raw::c_char;
		 2 use std::ffi::CStr;
		 3 use std::ffi::CString;
		 4 
		 5 #[no_mangle]
		 6 pub extern "C" fn count_characters(ptr: *const c_char) -> u32 {
		 7 
		 8     // Dereference and wrap the incoming raw pointer.
		 9     let c_string = unsafe {
		10         assert!(!ptr.is_null());
		11 
		12         CStr::from_ptr(ptr)
		13     };
		14 
		15     // Convert into a rust string.
		16     let rust_string = c_string.to_str().unwrap();
		17 
		18     // Return the number of characters.
		19     rust_string.chars().count() as u32
		20 }
		21 
		22 #[cfg(test)]
		23 mod tests {
		24     use super::*;
		25 
		26     #[test]
		27     pub fn internal() {
		28 
		29         // Simulate a call over the C interface by creating a CString.
		30         let message = "Hello World!";
		31         let c_string = CString::new(message).expect("CString::new failed");
		32 
		33         // Convert the c_string into a raw c_pointer. 
		34         let c_pointer = c_string.into_raw();
		35 
		36         // Call into the library function to count the characters.
		37         let count = count_characters(c_pointer);
		38         println!("\nThe number of characters in {} = {}", message, count);
		39     }
		40 }
		```
		
		*count_characters( )* will be the only function accessible to importing applications.  To make this function externally-callable, receive a String value, count the characters, and return the count, the following steps are necessary:
		
		1. **Line 5**:  instruct the Rust compiler to disable *'name mangling'*.  Name mangling is the process of encoding function and variable names to ensure that they are unique (for more details, please see [name mangling](https://en.wikipedia.org/wiki/Name_mangling)).  Adding the following line will disable name mangling for count_characters( ):
		
			`#[no_mangle]`  
		
		2. **Line 6**:  in the function declaration, specify that the function will be visible and callable from outside of the library by adding the following snippet to the function declaration:

			`pub extern "C"`
		
		3. **Lines 8-13**:  C-language strings are pointers to memory addresses and these must be converted into CStr representations for use within Rust.  The *unsafe* modifier denotes that using memory addresses in this manner, while necessary, is an unsafe operation and that the Rust compiler will not be doing its normal error checking for that operation.
		
		4. **Line 16**:  with the native CStr object, a native Rust string can be created by unwrapping to gain access to the data content, as follows:

			`let rust_string = c_string.to_str().unwrap();`
			
		5.  **Line 19**:  once the native Rust string has been created, it is easy to request a count of the characters and return that value to the caller, as follows:

			`rust_string.chars().count() as u32`
		
	4. Next, build the Rust library for testing by navigating to ./countchars and typing:
	
		`cargo test -- --nocapture`
		
		This will invoke the cargo build tool, which will build the library and run the specified tests (i.e., see line 23 "mod tests").  The "-- --nocapture" flag will instruct cargo to print any print statements to the console.  If successful, the output should look like this:
			
		```
		% cargo test -- --nocapture
			Finished test [unoptimized + debuginfo] target(s) in 0.04s
   			 Running target/debug/deps/countchars-277278e44b221f11

		running 1 test
		test tests::internal ... 
		The number of characters in Hello World! = 12
		ok

		test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

		% 
		```

	5. Now, build the library for execution by typing:
	
		`cargo build`
		
		This will invoke the cargo build tool and create the Rust library, so that it can be linked into the C test application.
		
3. Create, build, and execute the sample C test application

	1. Make a sub-directory for the test application by typing:
	
		`mkdir test_app`
		
	2. Navigate to ./test_app/ and create a file called *main.c* and add the following code (omitting line numbers):
	
		```
		 1 #include <stdint.h>
		 2 #include <stdio.h>
		 3 
		 4 uint32_t count_characters(const char* str);
		 5 
		 6 int main() {
		 7 
		 8     char *str = "Hello World!";
		 9     uint32_t count = count_characters(str);
		10     printf("There are %d chars in \"%s\"\n", count, str);
		11 
		12     return 0;
		13 }
		```
		
		In the above source, a very simple C program is created.  Line 4 shows how the public function from the previously-built Rust library can be referenced within the C application.  More commonly, such external prototypes are created in a separate header file (often generated with a tool called [cbindgen](https://github.com/eqrion/cbindgen), but the function is declared in this file for simplicity.  The count_characters( ) function is then invoked on line 9 and the results are printed on line 10.
		
	2. The main.c source file is compiled and linked with the Rust countchars library by typing:
	
	 `gcc main.c -L ../countchars/target/debug -lcountchars -o main`
	 
	3. The resulting application *main* is executed by typing:
	
		`./main`
		
		and, if everything was successful, the following output is displayed:
		
		*There are 12 chars in "Hello World!"*
		
## Conclusion
This tutorial has demonstrated how Rust can be used to create a linkable library and import it into a C-language application.  Creating linkable libraries in Rust is a vary nice way of writing the business logic of an application once and then packaging it so that it can be imported in other applications.  This facilitates code reuse that both increases development speed and also reduces the level of quality assurance testing normally associated with developing separate libraries for other languages or platforms.

While developing linkable Rust libraries had a number of signifcant benefits, it also introduces some added complexity for upper level applications calling into the linked library along with the need to manage allocated data types across the FFI layer.  One method of reducing this complexity is presented in the next tutorial [Creating Language Wrappers For Rust Libraries - Part 1](https://github.com/sudoplatform-labs/ffi-tutorials/blob/main/Wrapper_Intro).

