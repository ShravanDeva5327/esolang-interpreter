# Basic Esolang Interpreter

This project is an interpreter for a basic esoteric programming language (esolang) written in Python. The interpreter can read and execute code written in this esolang, which supports basic arithmetic operations, variable assignments, control flow statements like `if`, `for`, and `while` loops, and print statements.

## Project Directory Structure
```structure
Basic Esolang Interpreter
├── main.py                # Main entry point for the interpreter
├── lexer.py               # Handles tokenizing the source code
├── parser.py              # Parses tokens into an Abstract Syntax Tree (AST)
├── interpreter.py         # Executes the code by interpreting the AST
├── utils.py               # Shared utility functions and classes
├── grammar.txt            # Defines the esolang grammar and syntax rules
├── examples
│   ├── fibonacci.txt      # Example program to calculate Fibonacci sequence
└── README.md              # Project documentation
```

- **Supported Constructs**:
  - Arithmetic and logical operations (addition, subtraction, multiplication, division, exponentiation, and, or, not).
  - Variable assignments.
  - Control flow statements (`if`, `for`, and `while` loops).
  - Print statements.

 ## Esolang Grammar
 The grammar of the esolang is defined in `grammar.txt`. Here is an overview:

 ```plaintext
program     : statements
statements  : NEWLINE* (expr NEWLINE*)*
expr        : identifier (EQUALS expr)?
              comp-expr ((AND|OR) comp-expr)*
comp-expr   : NOT comp-expr ? arith-expr ((ISE|NE|LT|GT|LTE|GTE) arit-expr)*
arith-expr  : term ((PLUS|MINUS) term)*
term        : power ((MUL|DIV) power)*
power       : factor (POW factor)*
factor      : INT|FLOAT|(expr)|identifier|if-block|for-block|while-block

if-block    : if expr then statements (else statements)? end
for-block   : for identifier EQUALS expr to expr (step expr)? do statements end
while-block : while expr do statements end
```

## Example: Fibonacci Sequence
The following example program calculates the Fibonacci sequence up to the 10th number:

```code
fib_n_2 = 0
fib_n_1 = 1

for n = 0 to 10 do
    if n == 0 then
        print("Fibonacci number ", n, " is ", 0)
    else
        if n == 1 then
            print("Fibonacci number ", n, " is ", 1)
        else
            fib_n = fib_n_1 + fib_n_2
            fib_n_2 = fib_n_1
            fib_n_1 = fib_n
            print("Fibonacci number ", n, " is ", fib_n)
        end
    end
end
```

## Error Handling
The interpreter includes robust error handling for various stages of code execution:

- Lexer Errors: Identifies invalid tokens in the source code.
  ### input
  ``` code
  1 + (2*3)@
  ```
  ### output
  ```code
  1 + (2*3)@
           ^^

  Syntax Error: Invalid Syntax
  line 1, column 10
  ```
- Parser Errors: Reports syntax errors.
  ### input
  ``` code
  if 5 > 2 do print(a) end
  ```
  ### output
  ```code
  if 5 > 2 do print(a) end
           ^^

  Syntax Error: Invalid Syntax
  line 1, column 10
  ```
- Runtime Errors: Handles issues such as division by zero or undefined variables.
  ### input
  ``` code
  1 + 'string'
  ```
  ### output
  ```code
  1 + 'string'
    ^^

  Runtime Error: Invalid operator '+' for 'INT' and 'STRING'
  line 1, column 3
  ```

## How to Run the Interpreter
To execute the interpreter, use the following command:
```code
  python main.py [file]
```

- REPL Mode: If no file is provided, the interpreter will run in interactive mode, allowing you to enter and execute code interactively.
- Script Mode: If a file is provided, the interpreter will execute the code contained in the file.

## Future Enhancements
- Add support for functions and user-defined procedures.
- Implement enhanced debugging features.
- Extend the language with additional built-in functions and data structures.

Happy Coding!!