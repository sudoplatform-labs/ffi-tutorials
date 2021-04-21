# Creating Simple Language Wrappers for Rust Libraries
<BR>
  
## Background

Modern software development efforts often use statically-linked or dynamically-linked libraries in order to facilitate code reuse between applications. When libraries are created using programming languages that are different from the importing applications, the library is considered *foreign code* by the application. In order to communicate between the application and library, a common function calling and data exchange protocol must be established. This common protocol is referred to as a *Foreign Function Interface (FFI)*.

This set of tutorials starts with a demonstration of how FFI layers are created and goes on to discuss some of the difficulties that application programmers may face when linking to such libraries.  Next, it presents a method whereby FFI layers can be automatically generated and customized to the target development languages that application developers use.  Finally, an explaination of how data types are exchanged with the linked libraries is discussed.

For these tutorials, Rust is used for the underlying libraries and test applications are demonstrated using C, Swift, and Python.

## Tutorials

1. [Simple Rust Library Foreign Function Interface](./Quick_FFI_Intro) - this tutorial introduces the basic concepts of creating a Rust library, adding an FFI layer, and consuming the library in a C application.

2. [Creating Language Wrappers For Rust Libraries - Part 1](./Wrapper_Intro) - discusses the need for language specific library wrapper layers and demonstrates how to use the Mozilla uniffi tool for creating wrappers.

3. [Creating Language Wrappers For Rust Libraries - Part 2](./Wrapper_Data_Types) - this tutorial builds upon the previous tutorial and demonstrates how to convert data types between Rust, Swift, and Python.
