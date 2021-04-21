fn main() {

	// This doesn't copy the files from the build dirs back into OUT_DIR, because
	// cargo isn't setting OUT_DIR.  As a result, we can't call this function
	// and need to call it manually.
        // uniffi_build::generate_scaffolding("./src/library.uniffi.udl").unwrap();
}

