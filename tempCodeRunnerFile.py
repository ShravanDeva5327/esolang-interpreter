from lexer import *
from parser import *
from interpreter import *
import readline
import argparse

arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('file', nargs='?', default=None, help='File to run')
args = arg_parser.parse_args()

if args.file is None:
    print("Basic Esolang Interpreter Written in Python")
    variables = {}
    while True:
        try:
            text = input(">>> ")
            lexer_ = Lexer(text)
            tokens = lexer_.tokenize()

            if tokens is not None:
                parser_ = Parser(text, tokens)
                ast_list = parser_.parse()
                for ast in ast_list:
                    interpreter_ = Interpreter(text, ast, variables)
                    result = interpreter_.interpret()
                    if result.value is not None:
                        print(f'{result.type}({result.value})')
        
        except EOFError:
            print("")
            break
        except KeyboardInterrupt:
            print("")
            continue
        except Exception as e:
            print(e)

else:
    try:
        with open(args.file, 'r') as f:
            variables = {}
            text = f.read()
            lexer_ = Lexer(text)
            tokens = lexer_.tokenize()

            if tokens is not None:
                parser_ = Parser(text, tokens)
                ast_list = parser_.parse()
                for ast in ast_list:
                    interpreter_ = Interpreter(text, ast, variables)
                    result = interpreter_.interpret()

    except Exception as e:
        print(e)
