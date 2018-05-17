use std::error::Error;
use std::io::prelude::*;
use std::fs::File;
use std::path::Path;

use std;


#[derive(Debug, Clone, Serialize)]
struct Instruction {
    src: bool,
    operation: String,
    operands: Vec<String>,
}
impl Eq for Instruction {}
impl PartialEq for Instruction {
    fn eq(&self, other: &Instruction) -> bool {
        self.src == other.src &&
        self.operation == other.operation &&
        self.operands.len() == other.operands.len() &&
        self.operands.iter()
            .zip(&other.operands) 
            .all(|(l, r)| *l == *r)
    }
}
impl Instruction {
    #[allow(dead_code)]
    pub fn print(&self) {
        let mut output = String::new();
        let mut ops = self.operands.iter();
        if self.src {
            output.push_str(&format!("{} = {} ", ops.next().unwrap(), self.operation));
        } else {
            output.push_str(&format!("{} ", self.operation));
        }

        while let Some(o) = ops.next() {
            output.push_str(&format!("{}, ", o));
        }
        println!("\t\t{}", output);
    }
}

#[derive(Debug)]
struct Bundle {
    instructions: Vec<Instruction>,
}
impl Eq for Bundle {}
impl PartialEq for Bundle {
    fn eq(&self, other: &Bundle) -> bool {
        self.instructions == other.instructions
    }
}

#[derive(Debug, Eq, PartialEq)]
enum Issuee {
    Instruction(Instruction),
    Bundle(Bundle),
}

#[derive(Debug)]
struct BasicBlock {
    issuees: Vec<Issuee>,
}
impl Eq for BasicBlock {}
impl PartialEq for BasicBlock {
    fn eq(&self, other: &BasicBlock) -> bool {
        self.issuees == other.issuees
    }
}

#[derive(Debug)]
struct Function {
    name: String,
    blocks: Vec<BasicBlock>,
}
impl Eq for Function {}
impl PartialEq for Function {
    fn eq(&self, other: &Function) -> bool {
        self.name == other.name &&
        self.blocks == other.blocks
    }
}

#[derive(Debug)]
pub struct Program {
    functions: Vec<Function>,
}
impl Eq for Program { }
impl PartialEq for Program {
    fn eq(&self, other: &Program) -> bool {
        self.functions == other.functions
    }
}

impl Program {
    #[allow(dead_code)]
    pub fn print(&self) {
        for function in &self.functions {
            println!("function_name: {}", function.name);
            for (i, ref block) in function.blocks.iter().enumerate() {
                println!("bb.{}", i);
                for issuee in &block.issuees {
                    match issuee {
                        &Issuee::Bundle(ref b) => {
                            println!("\tBUNDLE {{");
                            for _b in &b.instructions {
                                _b.print();
                            }
                            println!("\t}}");
                        },
                        &Issuee::Instruction(ref i) => i.print(),
                    }
                }
            }
        }
    }

    pub fn gadgets(&self) -> Vec<Gadget> {
        let mut gadgets = Vec::new();
        let mut offset: u64 = 0;

        for function in &self.functions {
            for block in &function.blocks {
                let mut insts = Vec::new(); // Hexagon is a RISC so one gadgets per block at most
                for issuee in &block.issuees {
                    offset += 32; // Count a bundle as one instruction in terms of offset
                    match issuee {
                        &Issuee::Bundle(ref b) => {
                            for _b in &b.instructions {
                                insts.push( _b.clone() );
                            }
                        },
                        &Issuee::Instruction(ref i) => insts.push( i.clone() ),
                    }
                }

                let last_inst = match insts.last() {
                    Some(li) => li.clone(),
                    None => continue,
                };

                // Hexagon has "jumpr R31" as the return instruction. "dealloc_return" does
                // "dealloc_frame" followed by "jumpr R31"
                if (last_inst.operation == "JMPret" && last_inst.operands[0] == "%r31")
                    || last_inst.operation.contains("return") {
                    let mut instructions: Vec<Instruction> = insts.into_iter().rev().take(4).collect();
                    instructions.reverse();
                    gadgets.push(Gadget{ offset, instructions });
                }
            }
        }
        gadgets
    }

    #[allow(dead_code)]
    pub fn shared_gadgets(&self, other: &Program) -> f32 {

        let gadgets = self.gadgets();
        let other_gadgets = other.gadgets();

        let mut shared: f32 = 0.0;
        for gadget in &gadgets {
            for other_gadget in &other_gadgets {
                if *gadget == *other_gadget {
                    shared += 1.0;
                }
            }
        }
        shared / gadgets.len() as f32
    }
}


#[derive(Debug, Clone, Serialize)]
pub struct Gadget {
    offset: u64,
    instructions: Vec<Instruction>,
}
impl Eq for Gadget {}
impl PartialEq for Gadget {
    fn eq(&self, other: &Gadget) -> bool {
        self.offset == other.offset &&
        self.instructions.len() == other.instructions.len() &&
        self.instructions.iter().zip(&other.instructions)
            .all(|(l, r)| *l == *r)
    }
}

fn read_operand(raw: &str) -> String {
    let mut s = String::new();
    for c in raw.chars() {
        if c == ',' || c == ' ' {
            break;
        } else {
            s.push(c);
        }
    }
    s
}

fn read_instruction(raw: &str) -> Instruction {
    let src: bool;
    let mut operands = Vec::new();
    let operation: String;

    let mut words = raw.split_whitespace();
    let first_word = words.next().unwrap();
    if first_word.starts_with("%") {
        // It is a register
        src = true;
        operands.push(read_operand(&first_word));

        // words[1] is "="
        words.next();

        // words[2] is the instruction
        operation = String::from(words.next().unwrap());

        // The rest are more operands
        while let Some(o) = words.next() {
            operands.push(read_operand(&o));
        }
    } else {
        // It is an instruction
        src = false;
        operation = String::from(first_word);

        // followed by operands
        while let Some(o) = words.next() {
            operands.push(read_operand(&o));
        }
    }
    Instruction{ src, operation, operands }
}

fn read_bundle(lines: &mut std::iter::Iterator<Item=&str>) -> Bundle {
    let mut instructions = Vec::new();
    while let Some(line) = lines.next() {
        let first_word = line.split_whitespace().next().unwrap();

        if first_word == "}" {
            break
        } else {
            let instruction = read_instruction(line);
            instructions.push( instruction );
        }
    }

    Bundle { instructions }
}

fn read_basic_block(mut lines: &mut std::iter::Iterator<Item=&str>) -> BasicBlock {
    // There is an empty line at the beginning and end of a basic block
    // Sometimes there is a "successor" line before the beginning empty one
    let first = lines.next();
    match first {
        Some(l) => match l.split_whitespace().next() {
            Some(x) => {
                if x.starts_with("successor") {
                    lines.next();
                }
            },
            None => (),
        },
        None => (),
    };

    let mut issuees = Vec::new();
    while let Some(line) = lines.next() {
        // Break if we are at end of bb
        if line.chars().all(char::is_whitespace) {
            break
        }

        let mut words = line.split_whitespace();
        let first_word = match words.next() {
            Some(w) =>  w,
            None => continue,
        };

        if first_word == "BUNDLE" {
            let bundle = read_bundle(&mut lines);
            issuees.push( Issuee::Bundle(bundle) );
            continue;
        }

        if first_word.starts_with("%") || first_word.chars().next().unwrap().is_alphabetic() {
            let instruction = read_instruction(&line);
            issuees.push( Issuee::Instruction(instruction) );
            continue
        }
    }
    
    BasicBlock { issuees }
}

// There is one function in every file
fn read_function<P: AsRef<Path>>(path: P) -> Result<Function, Box<Error>> {
    let mut file = File::open(path)?;
    let mut raw = String::new();
    file.read_to_string(&mut raw)?;

    let mut name = String::from("N/A");
    let mut blocks = Vec::new();

    let mut lines = raw.lines();

    while let Some(line) = lines.next() {
        let mut words = line.split_whitespace();
        let first_word = match words.next() {
            Some(w) =>  w,
            None => continue,
        };

        if first_word == "name:" {
            name = words.next().expect("Couldn't find name of function").to_string();
        }

        if first_word.starts_with("bb") {
            blocks.push(read_basic_block( &mut lines ) );
        }
    }

    // Name is required
    if name == "N/A" {
        panic!("Couldn't find function name for {:?}", file);
    }
    Ok(Function {name, blocks})
}

pub fn read_program<P: AsRef<Path>>(paths: Vec<P>) -> Result<Program, Box<Error>> {
    let mut functions = Vec::new();
    for path in paths {
        let function = read_function(path)?;
        functions.push(function);
    }
    functions.sort_unstable_by(|a, b| a.name.cmp(&b.name));
    Ok(Program {functions})
}

