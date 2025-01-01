from lexer import *

variables = {}
while True:
    try:
        text = input(">>> ")

        # Generate tokens
        lexer_ = Lexer(text)
        tokens = lexer_.tokenize()

        if tokens is not None:
            print(tokens)

            # Generate AST
            parser_ = Parser(tokens)
            ast = parser_.parse()
            if ast is not None:
                print(ast)

                interpreter_ = Interpreter(ast, variables)
                result = interpreter_.interpret()
                if result.value is not None:
                    print(result)
    
    except EOFError:
        print("")
        break
    except KeyboardInterrupt:
        print("")
        continue
    except Exception as e:
        print(e)
