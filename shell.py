from lexer import *

variables = {}
while True:
    try:
        text = input(">>> ")

        # Generate tokens
        lexer_ = Lexer(text)
        tokens = lexer_.tokenize()

        if tokens is not None:
            # print(tokens)

            # Generate AST
            parser_ = Parser(text, tokens)
            ast_list = parser_.parse()
            if ast_list is not None:
                # print(ast_list)
                for ast in ast_list:
                    interpreter_ = Interpreter(text, ast, variables)
                    result = interpreter_.interpret()
                    # if result is not None:
                        # print(f'{result.value}: {result.type}')
    
    except EOFError:
        print("")
        break
    except KeyboardInterrupt:
        print("")
        continue
    # except Exception as e:
    #     print(e)
