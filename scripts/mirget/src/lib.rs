use std::error::Error;
use std::fs;
use std::path;

mod program;

extern crate serde;

extern crate serde_json;
#[macro_use]
extern crate serde_derive;

pub struct Config {
    directory: String,
}

impl Config {
    pub fn new(mut args: std::env::Args) -> Result<Config, &'static str> {
        args.next(); // Skip the name of the command

        let directory = match args.next() {
            Some(arg) => arg,
            None => return Err("Didn't get a directory"),
        };

        Ok(Config { directory })
    }
}


pub fn run(config: Config) -> Result<(), Box<Error>> {
    // The given directory contains all versions of the program
    let root = fs::read_dir(&config.directory)?;

    // Each sub-directory is a version of the program
    for version in root.map(|dir| dir.expect("IO error").path()).filter(|path| path.is_dir()) {
        let mut output_file_name = path::PathBuf::from(version.clone());
        output_file_name.push("gadgets");

        // Find all functions in the directory
        let files = fs::read_dir(version)?;
        let mut raw = Vec::new();
        for file in files.map(|file| file.expect("IO error").path())
            .filter(|path| path.is_file()) {
                let file_name = file.file_name().expect(&format!("Couldn't find name of file for {:?}", file));
                if file_name != "cost" && file_name != "gadgets" {
                    raw.push( file.clone() );
                }
        }

        // Find the gadgets and write them to file
        let program = program::read_program(raw)?;
        let gadgets = program.gadgets();

        let output_file_handle = fs::OpenOptions::new()
            .create(true)
            .truncate(true) // Always overwrite the old stuff
            .write(true)
            .open(output_file_name)
            .unwrap();
        serde_json::to_writer(output_file_handle, &gadgets)?;
    }

    Ok(())
}
