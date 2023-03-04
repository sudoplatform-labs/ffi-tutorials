use std::collections::HashMap;

uniffi::include_scaffolding!("library");

//------------------------------------------------------------
//----- Custom Error Types -----------------------------------
#[derive(Debug, thiserror::Error)]
pub enum ArithmeticError {
    #[error("Integer overflow on an operation with {a} and {b}")]
    IntegerOverflow { a: u64, b: u64 },
}

//------------------------------------------------------------
//----- Custom Structure Types -----------------------------------
#[derive(Debug, Clone)]
#[derive(PartialEq, PartialOrd)]
pub struct Point {
    x: f64,
    y: f64,
}

//------------------------------------------------------------
//------ API: Public Methods ---------------------------------

// ----- Boolean Test -----
fn bool_inc_test(value: bool) -> bool {

    return !value
}

// ----- Integer Tests -----
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

// ----- Unsigned Integer Tests -----
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

// ----- Float Tests -----
pub fn float_inc_test(value: f32) -> f32 {

    return value + 1.0
}

// ----- Double Tests -----
pub fn double_inc_test(value: f64) -> f64 {

    return value + 1.0
}

// ----- String Tests -----
pub fn string_inc_test(value: String) -> String {

    return format!("{}{}", value, value);
}

// ----- ByRef Tests -----
pub fn byref_inc_test(value: &Point) -> Point {

    // Clone the input value & increment its members.
    let mut new_value = value.clone();
    new_value.x = value.x + 1.0;
    new_value.y = value.y + 1.0;

    return new_value;
}

// ----- Optional Type Tests -----
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

// ----- Vector Tests -----
pub fn vector_inc_test(mut value: Vec<String>) -> Vec<String> {

    let mut new_value: Vec<String> = value.to_vec();
    new_value.append(&mut value);

    return new_value;
}

// ----- HashMap Tests -----
pub fn hash_map_inc_test(value: HashMap<String, i32>) -> HashMap<String, i32> {     // Only string keys are supported.

    let mut result = value.clone();
    result.insert(String::from("zero"), 0);

    return result;
}

// ----- Void Test -----
pub fn void_inc_test(_value: i32) -> () {

    return ();
}

// ----- Error Code Test -----
pub fn error_inc_test(a: u64, b: u64) -> Result<u64, ArithmeticError> {

    let a1: u64 = a;
    a1.checked_add(b).ok_or(ArithmeticError::IntegerOverflow { a, b })
}

//------------------------------------------------------------
//------ Library Tests ---------------------------------------
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

        print!("Running byRef test...");
        let x0: f64 = 1.0;
        let y0: f64 = 2.0;
        let point: Point = Point { x: x0, y: y0 };
        let point2: Point = byref_inc_test(&point);
        assert_eq!(point.x + 1.0, point2.x);
        assert_eq!(point.y + 1.0, point2.y);
        println!("Passed");

        print!("Running option type test...");
        assert_eq!(Some(1), optional_type_inc_test(Some(0)));
        println!("Passed");

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
        let value_1: u64 = 0;
        let value_2: u64 = 5;
        let r_value: Result<u64, ArithmeticError> = error_inc_test(value_1, value_2);
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
        let value_1: u64 = u64::MAX;
        let value_2: u64 = 1;
        let r_value: Result<u64, ArithmeticError> = error_inc_test(value_1, value_2);
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
