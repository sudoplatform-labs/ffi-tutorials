uniffi::include_scaffolding!("library");

//------------------------------------------------------------
//------ Tests -----------------------------------------------

// ----- Boolean Test -----
fn bool_inc_test(value: bool) -> bool {

    return !value
}

//------------------------------------------------------------
//------ Tests -----------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    pub fn internal() {
        println!("\n");
        println!("Running boolean test...");
        assert_eq!(false, bool_inc_test(true));

     }
}
