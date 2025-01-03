import string

LETTERS = string.ascii_letters
DIGITS = "0123456789"
NUMERALS = ".0123456789"
BOOL_VAR = ("true", "false")

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_STR = "STRING"
TT_BOOL = "BOOL"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_POW = "POW"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_COMMA = "COMMA"

DATA_TYPES = (TT_INT, TT_FLOAT, TT_STR, TT_BOOL)
NUM_DATA_TYPES = (TT_INT, TT_FLOAT)
ARITH_OP = (TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_POW)
PAREN = (TT_LPAREN, TT_RPAREN)

TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_EQUALS = "EQUALS"

TT_ISEQ = "ISEQ"
TT_NOTEQ = "NOTEQ"
TT_LT = "LT"
TT_GT = "GT"
TT_LTE = "LTE"
TT_GTE = "GTE"

COMPARATORS = (TT_ISEQ, TT_NOTEQ, TT_LT, TT_GT, TT_LTE, TT_GTE)

KEYWORDS = ["and", "or", "not", "print", "true", "false",
            "if", "then", "elif", "else","for", "to", "step", "while", "do"]

def line_in_text(text: str, line: int) -> str:
    lines = text.split("\n")
    return lines[line - 1] if line - 1 < len(lines) else ""


class Token:
    def __init__(self, line: int = 0, start_col: int = 0, type_: str = None, value_: str = None):
        self.line = line
        self.start_col = start_col
        self.type = type_
        self.value = value_

    def __repr__(self) -> str:
        if self.type == TT_STR:
            return f"{self.type}('{self.value}')"
        return f"{self.type}({self.value})" if self.value is not None else self.type

    def __eq__(self, other: "Token") -> bool:
        return self.type == other.type and self.value == other.value

class Position:
    def __init__(self, ln: int, col: int, idx: int):
        self.ln = ln
        self.col = col
        self.idx = idx

    def advance(self, current_char: str) -> None:
        self.col += 1
        self.idx += 1
        if current_char == "\n":
            self.col = 1
            self.ln += 1

    def copy(self) -> "Position":
        return Position(self.ln, self.col)


class PrintError:
    def __init__(self, text: str, error_name: str, details: str, line: int, start_col: int):
        error_line = line_in_text(text, line) + "\n"
        wiggle = " " * (start_col - 1) + "^^" + "\n"
        message = f"{error_line}{wiggle}{error_name}: {details}\nline {line}, column {start_col}"
        raise Exception(message)


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = Position(1, 0, -1)
        self.current_char = None
        self.advance()

    def advance(self) -> None:
        self.pos.advance(self.current_char)
        self.current_char = (self.text[self.pos.idx] if self.pos.idx < len(self.text) else None)

    def tokenize(self):
        tokens = []

        while self.current_char != None:
            ln = self.pos.ln
            col = self.pos.col
            if self.current_char in " \t":
                self.advance()
                continue
            elif self.current_char in NUMERALS:
                num_str = ""
                while self.current_char != None and self.current_char in NUMERALS:
                    num_str += self.current_char
                    if self.current_char == "." and num_str.count(".") > 1:
                        PrintError(self.text, "Syntax Error", "Invalid Syntax", self.pos.ln, self.pos.col)
                        return None
                    self.advance()
                if num_str.count(".") == 0: 
                    tokens.append(Token(self.pos.ln, self.pos.col, TT_INT, int(num_str)))
                elif num_str.count(".") == 1: 
                    tokens.append(Token(self.pos.ln, self.pos.col, TT_FLOAT, float(num_str)))
            elif self.current_char in LETTERS + '_':
                str_ = ""
                while (self.current_char != None and self.current_char in LETTERS + DIGITS + '_'):
                    str_ += self.current_char
                    self.advance()
                if str_ in BOOL_VAR:
                    tokens.append(Token(ln, col, TT_BOOL, str_))
                else:
                    tokens.append(Token(ln, col, TT_KEYWORD, str_.upper()) if str_ in KEYWORDS else Token(ln, col, TT_IDENTIFIER, str_))
            elif self.current_char in "'\"":
                start_quote = self.current_char
                self.advance()
                str_ = ""
                while self.current_char != None and self.current_char != start_quote:
                    str_ += self.current_char
                    self.advance()
                if self.current_char == None:
                    PrintError(self.text, "Syntax Error", "Invalid String", self.pos.ln, self.pos.col)
                    return None
                self.advance()
                tokens.append(Token(ln, col, TT_STR, str_))
            elif self.current_char == "+":
                tokens.append(Token(ln, col, TT_PLUS))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(ln, col, TT_MINUS))
                self.advance()
            elif self.current_char == "*":
                self.advance()
                if self.current_char == "*":
                    tokens.append(Token(ln, col, TT_POW))
                    self.advance()
                else:
                    tokens.append(Token(ln, col, TT_MUL))
            elif self.current_char == "/":
                tokens.append(Token(ln, col, TT_DIV))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(ln, col, TT_LPAREN))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(ln, col, TT_RPAREN))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(ln, col, TT_COMMA))
                self.advance()
            elif self.current_char == "=":
                self.advance()
                if self.current_char == "=":
                    tokens.append(Token(ln, col, TT_ISEQ))
                    self.advance()
                else:
                    tokens.append(Token(ln, col, TT_EQUALS))
            elif self.current_char == "!":
                self.advance()
                if self.current_char == "=":
                    tokens.append(Token(ln,col, TT_NOTEQ))
                    self.advance()
                else:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", ln, col - 1)
                    return None
            elif self.current_char == "<":
                self.advance()
                if self.current_char == "=":
                    tokens.append(Token(ln, col, TT_LTE))
                    self.advance()
                else:
                    tokens.append(Token(ln, col, TT_LT))
            elif self.current_char == ">":
                self.advance()
                if self.current_char == "=":
                    tokens.append(Token(ln, col, TT_GTE))
                    self.advance()
                else:
                    tokens.append(Token(ln, col, TT_GT))
            else:
                PrintError(self.text, "Syntax Error", "Invalid Syntax", ln, col)
                return None
        for i in range(len(tokens) - 1):
            if tokens[i].type == TT_INT and tokens[i + 1].type == TT_LPAREN:
                raise Exception(f"Invalid Syntax: int cannot be called")
            if tokens[i].type == TT_FLOAT and tokens[i + 1].type == TT_LPAREN:
                raise Exception(f"Invalid Syntax: float cannot be called")
        return tokens


class Node:
    def __init__(self, token: Token):
        self.token = token

    def __repr__(self) -> str:
        return f"{self.token}"


class varAssignNode:
    def __init__(self, var_name: Token, value: Node):
        self.var_name = var_name
        self.value = value

    def __repr__(self) -> str:
        return f"{{assign {self.var_name.value} = {self.value}}}"


class varAccessNode:
    def __init__(self, var_name: Token):
        self.var_name = var_name

    def __repr__(self) -> str:
        return f"{{access {self.var_name.value}}}"
    

class BinOpNode:
    def __init__(self, op: Token, left_node: Node, right_node: Node):
        self.op = op
        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self) -> str:
        return f"{{{self.left_node} {self.op} {self.right_node}}}"
class printNode:
    def __init__(self, tokens: list[Node|varAccessNode|varAssignNode|BinOpNode]):
        self.tokens = tokens
    
    def __repr__(self) -> str:
        return f"{{print {self.tokens}}}"
    
class ifNode:
    def __init__(self, cases: list[tuple[Node, Node]], else_case: Node):
        self.cases = cases
        self.else_case = else_case

    def __repr__(self) -> str:
        string = ""
        for i in range(len(self.cases)):
            string += f"if {self.cases[i][0]} then {self.cases[i][1]}\n" if i == 0 else f"elif {self.cases[i][0]} then {self.cases[i][1]}\n"
        if self.else_case != None:
            string += f"else {self.else_case}"
        
        return f"{string}"
            
class forNode:
    def __init__(self, identifier: Token, start: Node, end: Node, step: Node, body: Node):
        self.identifier = identifier
        self.start = start
        self.end = end
        self.step = step
        self.body = body
    
    def __repr__(self) -> str:
        return f"for {self.start} to {self.end} step {self.step} do {self.body}"
    
class WhileNode:
    def __init__(self, condition: Node, body: Node):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"while {self.condition} do {self.body}"

class Parser:
    def __init__(self, text: str, tokens: list[Token]):
        self.text = text
        self.tokens = tokens
        self.idx = -1
        self.advance()

    def advance(self) -> Token:
        self.idx += 1
        if self.idx < len(self.tokens):
            self.current_token = self.tokens[self.idx]
        else:
            self.current_token = Token(None)
        return self.current_token
    
    def move_back(self) -> Token:
        self.idx -= 1
        if self.idx >= 0:
            self.current_token = self.tokens[self.idx]
        else:
            self.current_token = Token(None)
        return self.current_token

    def factor(self) -> Node:
        if self.idx >= len(self.tokens):
            return None
        token = self.current_token
        if token.type in DATA_TYPES:
            self.advance()
            if token.type == TT_BOOL:
                return (Node(Token(token.line, token.start_col, TT_INT, 1)) if token.value == "true" else Node(Token(token.line, token.start_col, TT_INT, 0)))
            return Node(token)
        elif token.type == TT_IDENTIFIER:
            self.advance()
            return varAccessNode(token)
        elif token.type in (TT_PLUS, TT_MINUS):
            self.advance()
            right = self.factor()
            if right == None:
                PrintError(self.text, "Syntax Error", "Expected an expression after operator", token.line, token.start_col + 1)
                return None
            return (BinOpNode(Token(type_=TT_MUL), Node(Token(type_=TT_INT, value_=1)), right) if token.type == TT_PLUS else BinOpNode(Token(type_=TT_MUL), Node(Token(type_=TT_INT, value_=-1)), right))
        elif token.type == TT_LPAREN:
            lParenidx = self.idx
            self.advance()
            result = self.expr()
            if self.current_token.type == TT_RPAREN:
                self.advance()
                return result
            else:
                PrintError(self.text, "Syntax Error", "'(' Never closed", token.line, token.start_col)
                return None
        elif token.type == TT_KEYWORD:
            if token.value == "IF":
                cases = []
                else_case = None
                self.advance()
                condition = self.expr()
                if condition == None:
                    PrintError(self.text, "Syntax Error", "Expected an expression after 'if'", token.line, token.start_col)
                    return None
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="THEN")):
                    PrintError(self.text, "Syntax Error", "Expected 'then' after condition", self.current_token.line, self.current_token.start_col)
                    return None
                self.advance()
                then = self.expr()
                if then == None:
                    PrintError(self.text, "Syntax Error", "Expected an expression after 'then'", self.current_token.line, self.current_token.start_col)
                    return None
                cases.append((condition, then))
                while self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="ELIF")):
                    self.advance()
                    condition = self.expr()
                    if condition == None:
                        PrintError(self.text, "Syntax Error", "Expected an expression after 'elif'", self.current_token.line, self.current_token.start_col)
                        return None
                    if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="THEN")):
                        if not self.current_token == None:
                            PrintError(self.text, "Syntax Error", "Expected 'then' after condition", self.current_token.line, self.current_token.start_col)
                        else:
                            PrintError(self.text, "Syntax Error", "Expected 'then' after condition", token.line, token.start_col)                    
                    self.advance()
                    then = self.expr()
                    if then == None:
                        PrintError(self.text, "Syntax Error", "Expected an expression after 'then'", self.current_token.line, self.current_token.start_col)
                        return None
                    cases.append((condition, then))
                if self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="ELSE")):
                    self.advance()
                    else_case = self.expr()
                    if else_case == None:
                        PrintError(self.text, "Syntax Error", "Expected an expression after 'else'", self.current_token.line, self.current_token.start_col)
                        return None
                
                return ifNode(cases, else_case)
            elif token.value == "FOR":
                self.advance()
                if self.current_token.type != TT_IDENTIFIER:
                    PrintError(self.text, "Syntax Error", "Expected an identifier after 'for'", token.line, token.start_col)
                var = self.current_token
                self.advance()
                if self.current_token.type != TT_EQUALS:
                    PrintError(self.text, "Syntax Error", "Expected '=' after identifier", self.current_token.line, self.current_token.start_col)
                self.advance()
                start_ = self.expr()
                if start_ == None:
                    PrintError(self.text, "Syntax Error", "Expected an expression after identifier", var.line, var.start_col)
                
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="TO")):
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line, token.start_col + 1)
                self.advance()

                end_ = self.expr()
                if end_ == None:
                    PrintError(self.text, "Syntax Error", "Expected an expression after 'to'", self.current_token.line, self.current_token.start_col)
                
                step_ = Node(Token(type_=TT_INT, value_=1))
                if self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="STEP")):
                    self.advance()
                    step_ = self.expr()
                    if step_ == None:
                        PrintError(self.text, "Syntax Error", "Expected an expression after 'step'", self.current_token.line, self.current_token.start_col)
                
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="DO")):
                    PrintError(self.text, "Syntax Error", "Expected 'do' after step", self.current_token.line, self.current_token.start_col)
                self.advance()
                body = self.expr()
                if body == None:
                    PrintError(self.text, "Syntax Error", "Expected an expression after 'do'", self.current_token.line, self.current_token.start_col)
                
                return forNode(var, start_, end_, step_, body)

            elif token.value == "WHILE":    
                self.advance()
                condition = self.expr()
                if condition == None:
                    PrintError(self.text, "Syntax Error", "Expected an expression after 'while'", token.line, token.start_col)
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="DO")):
                    PrintError(self.text, "Syntax Error", "Expected 'do' after condition", self.current_token.line, self.current_token.start_col)
                self.advance()
                body = self.expr()
                if body == None:
                    PrintError(self.text, "Syntax Error", "Expected an expression after 'do'", self.current_token.line, self.current_token.start_col)
                return WhileNode(condition, body)
            
            elif token.value == "PRINT":
                pr_ln = self.current_token.line
                pr_col = self.current_token.start_col
                self.advance()
                if self.current_token.type == TT_LPAREN:
                    lparen_ln = self.current_token.line
                    lparen_col = self.current_token.start_col
                    self.advance()
                    tokens = []
                    while self.current_token.type != TT_RPAREN:
                        tokens.append(self.expr())
                        if self.current_token.type != TT_RPAREN:
                            if self.current_token.type == TT_COMMA:
                                self.advance()
                            else:
                                PrintError(self.text, "Syntax Error", "Expected ',' after expression", lparen_ln, lparen_col)
                        elif self.current_token.type == TT_RPAREN:
                            self.advance()
                            return printNode(tokens)
                        else:
                            PrintError(self.text, "Syntax Error", "'(' Never closed", lparen_ln, lparen_col)
                else:
                    PrintError(self.text, "Syntax Error", "Expected '(' after 'print'", pr_ln, pr_col)
                    return None
                

    def pow(self) -> BinOpNode:
        return self.bin_op(self.factor, (TT_POW,))

    def term(self) -> BinOpNode:
        res = self.bin_op(self.pow, (TT_MUL, TT_DIV))
        return res

    def arith_expr(self) -> BinOpNode:
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self) -> BinOpNode:
        if self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="NOT")):
            ln = self.current_token.line
            col = self.current_token.start_col
            self.advance()
            right = self.comp_expr()
            if right == None:
                PrintError(self.text, "Syntax Error", "Expected an expression after 'not'", ln, col)
                return None
            return BinOpNode(Token(type_=TT_ISEQ), Node(Token(type_=TT_INT, value_=0)), right)
        return self.bin_op(self.arith_expr, COMPARATORS)

    def expr(self) -> BinOpNode:
        # if self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="PRINT")):
        #     pr_ln = self.current_token.line
        #     pr_col = self.current_token.start_col
        #     self.advance()
        #     if self.current_token.type == TT_LPAREN:
        #         lparen_ln = self.current_token.line
        #         lparen_col = self.current_token.start_col
        #         self.advance()
        #         tokens = []
        #         while self.current_token.type != TT_RPAREN:
        #             tokens.append(self.expr())
        #             if self.current_token.type != TT_RPAREN:
        #                 if self.current_token.type == TT_COMMA:
        #                     self.advance()
        #                 else:
        #                     PrintError(self.text, "Syntax Error", "Expected ',' after expression", lparen_ln, lparen_col)
        #             elif self.current_token.type == TT_RPAREN:
        #                 self.advance()
        #                 return printNode(tokens)
        #             else:
        #                 PrintError(self.text, "Syntax Error", "'(' Never closed", lparen_ln, lparen_col)
        #     else:
        #         PrintError(self.text, "Syntax Error", "Expected '(' after 'print'", pr_ln, pr_col)
        #         return None
        
        if self.current_token.type == TT_IDENTIFIER:
            var_name = self.current_token
            self.advance()
            if self.current_token.type == TT_EQUALS:
                ln = self.current_token.line
                col = self.current_token.start_col
                self.advance()
                value = self.expr()
                if value == None:
                    PrintError(self.text, "Syntax Error", "Expected an expression after assignment", ln, col)
                    return None
                return varAssignNode(var_name, value)
            else:
                self.move_back()

        return self.and_or()

    def bin_op(self, func, ops: list[str]) -> BinOpNode:
        left = func()
        while self.current_token.type in ops:
            op = self.current_token
            opidx = self.idx
            if left == None:
                PrintError(self.text, "Syntax Error", "Expected an expression before operator", op.line, op.start_col - 1)
                return None
            self.advance()
            right = func()
            if right == None:
                PrintError(self.text, "Syntax Error", "Expected an expression after operator", op.line, op.start_col + 1)
            left = BinOpNode(op, left, right)
        return left

    def and_or(self) -> Node:
        left = self.comp_expr()
        while self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="AND")) or self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="OR")):
            op = self.current_token
            opidx = self.idx
            if left == None:
                PrintError(self.text, "Syntax Error", "Expected an expression before operator", op.line, op.start_col)
                return None
            self.advance()
            right = self.comp_expr()
            if right == None:
                PrintError(self.text, "Syntax Error", "Expected an expression after operator", op.line, op.start_col)
                return None
            left = BinOpNode(op, left, right)
        return left

    def parse(self):
        res = self.expr()
        if self.idx < len(self.tokens):
            PrintError(self.text, "Syntax Error", "Expected an operator", self.current_token.line, self.current_token.start_col,)
            return None
        return res


class VariablelTable:
    def __init__(self, variables: dict[str, int | float | str] = {}):
        self.variables = variables

    def get(self, var_name: str):
        value = self.variables.get(var_name, None)
        return value

    def set(self, var_name: str, value):
        self.variables[var_name] = value

    def remove(self, var_name: str):
        del self.variables[var_name]


class Interpreter:
    def __init__(self, text, tree: BinOpNode | Node, variables: dict[str, int | float | str] = {}):
        self.text = text
        self.tree = tree
        self.variable_table = VariablelTable(variables)

    def visit(self, node: BinOpNode | Node | varAccessNode | varAssignNode) -> Token:
        if isinstance(node, Node):
            return node.token
        elif isinstance(node, ifNode):
            for case in node.cases:
                if self.visit(case[0]).__eq__(Token()):
                    PrintError(self.text, "Runtime Error", "Expected an expression after 'if'", 1, 1)
                if self.visit(case[0]).value:
                    return self.visit(case[1])
            if node.else_case != None:
                return self.visit(node.else_case)
            return Token()
        elif isinstance(node, forNode):
            self.variable_table.set(node.identifier.value, self.visit(node.start).value)
            i = self.visit(node.start).value
            while (self.visit(node.start).value - self.visit(node.end).value) * (i - self.visit(node.end).value) >= 0:
                self.variable_table.set(node.identifier.value, i)
                self.visit(node.body)
                i += self.visit(node.step).value
            return Token()
        elif isinstance(node, WhileNode):
            while self.visit(node.condition).value:
                self.visit(node.body)
            return Token()
        elif isinstance(node, printNode):
            for token in node.tokens:
                print(self.visit(token).value, end="")
            print()
            return Token()
        elif isinstance(node, varAssignNode):
            self.variable_table.set(node.var_name.value, self.visit(node.value).value)
            return Token()
        elif isinstance(node, varAccessNode):
            value = self.variable_table.get(node.var_name.value)
            if value is None:
                PrintError(self.text, "Runtime Error", f"Variable {node.var_name.value} is not defined", node.var_name.line, node.var_name.start_col)
            return (Token(type_=TT_INT, value_=value) if isinstance(value, int) else (Token(type_=TT_FLOAT, value_=value) if isinstance(value, float) else Token(type_=TT_STR, value_=value)))
        elif isinstance(node, BinOpNode):
            if node.op.type == TT_PLUS:
                if ((self.visit(node.left_node).type == TT_STR) ^ (self.visit(node.right_node).type == TT_STR)):
                    PrintError(self.text, "Runtime Error", "Cannot add string to a non-string", node.op.line, node.op.start_col,)
                val = (self.visit(node.left_node).value + self.visit(node.right_node).value)
                type = (TT_STR if self.visit(node.left_node).type == TT_STR else TT_INT if self.visit(node.left_node).type == TT_INT and self.visit(node.right_node).type == TT_INT else TT_FLOAT)
                return Token(type_=type, value_=val)
            elif node.op.type == TT_MINUS:
                if (self.visit(node.left_node).type == TT_STR or self.visit(node.right_node).type == TT_STR):
                    PrintError(self.text, "Runtime Error", "Invalid operator ' - ' for strings", node.op.line, node.op.start_col)
                val = (self.visit(node.left_node).value - self.visit(node.right_node).value)
                type = (TT_INT if self.visit(node.left_node).type == TT_INT and self.visit(node.right_node).type == TT_INT else TT_FLOAT)
                return Token(type_=type, value_=val)
            elif node.op.type == TT_MUL:
                if self.visit(node.left_node).type == TT_STR:
                    if self.visit(node.right_node).type == TT_INT:
                        return Token(type_=TT_STR, value_=self.visit(node.left_node).value * self.visit(node.right_node).value)
                    else:
                        PrintError(self.text, "Runtime Error", "Cannot multiply string with a non-integer", node.op.line, node.op.start_col)
                elif self.visit(node.right_node).type == TT_STR:
                    if self.visit(node.left_node).type == TT_INT:
                        return Token(type_=TT_STR, value_=self.visit(node.left_node).value * self.visit(node.right_node).value)
                    else:
                        PrintError(self.text, "Runtime Error", "Cannot multiply string with a non-integer", node.op.line, node.op.start_col)
                val = (self.visit(node.left_node).value * self.visit(node.right_node).value)
                type = (TT_INT if self.visit(node.left_node).type == TT_INT and self.visit(node.right_node).type == TT_INT else TT_FLOAT)
                return Token(type_=type, value_=val)
            elif node.op.type == TT_DIV:
                if self.visit(node.right_node).value == 0:
                    PrintError(self.text, "Runtime Error", "Division by zero", node.op.line, node.op.start_col,)
                if (self.visit(node.left_node).type == TT_STR or self.visit(node.right_node).type == TT_STR):
                    PrintError(self.text, "Runtime Error", "Invalid operator ' / ' for strings", node.op.line, node.op.start_col)
                val = (self.visit(node.left_node).value / self.visit(node.right_node).value)
                type = (TT_FLOAT)
                return Token(type_=type, value_=val)
            elif node.op.type == TT_POW:
                if (self.visit(node.left_node).type == TT_STR or self.visit(node.right_node).type == TT_STR):
                    PrintError(self.text, "Runtime Error", "Invalid operator ' ** ' for strings", node.op.line, node.op.start_col)
                val = (self.visit(node.left_node).value ** self.visit(node.right_node).value)
                type = (TT_INT if self.visit(node.left_node).type == TT_INT and self.visit(node.right_node).type == TT_INT and self.visit(node.right_node).value >= 0 else TT_FLOAT)
                return Token(type_=type, value_=val)
            elif node.op.type == TT_ISEQ:
                if ((self.visit(node.left_node).type == TT_STR) ^ (self.visit(node.right_node).type == TT_STR)):
                    PrintError(self.text, "Runtime Error", "Invalid operator ' == ' for string and non string", node.op.line, node.op.start_col)
                return Token(type_=TT_INT,value_=(1 if self.visit(node.left_node).value == self.visit(node.right_node).value else 0))
            elif node.op.type == TT_NOTEQ:
                if ((self.visit(node.left_node).type == TT_STR) ^ (self.visit(node.right_node).type == TT_STR)):
                    PrintError(self.text, "Runtime Error", "Invalid operator ' != ' for string and non string", node.op.line, node.op.start_col)
                return Token(type_=TT_INT,value_=(1 if self.visit(node.left_node).value != self.visit(node.right_node).value else 0))
            elif node.op.type == TT_LT:
                if ((self.visit(node.left_node).type == TT_STR) ^ (self.visit(node.right_node).type == TT_STR)):
                    PrintError(self.text, "Runtime Error", "Invalid operator ' < ' for string and non string", node.op.line, node.op.start_col)
                return Token(type_=TT_INT, value_=(1 if self.visit(node.left_node).value < self.visit(node.right_node).value else 0))
            elif node.op.type == TT_GT:
                if ((self.visit(node.left_node).type == TT_STR) ^ (self.visit(node.right_node).type == TT_STR)):
                    PrintError(self.text, "Runtime Error", "Invalid operator ' > ' for string and non string", node.op.line, node.op.start_col)
                return Token(type_=TT_INT, value_=(1 if self.visit(node.left_node).value > self.visit(node.right_node).value else 0))
            elif node.op.type == TT_LTE:
                if ((self.visit(node.left_node).type == TT_STR) ^ (self.visit(node.right_node).type == TT_STR)):
                    PrintError(self.text, "Runtime Error", "Invalid operator ' <= ' for string and non string", node.op.line, node.op.start_col)
                return Token(type_=TT_INT, value_=(1 if self.visit(node.left_node).value <= self.visit(node.right_node).value else 0))
            elif node.op.type == TT_GTE:
                if ((self.visit(node.left_node).type == TT_STR) ^ (self.visit(node.right_node).type == TT_STR)):
                    PrintError(self.text, "Runtime Error", "Invalid operator ' >= ' for string and non string", node.op.line, node.op.start_col)
                return Token(type_=TT_INT, value_=(1 if self.visit(node.left_node).value >= self.visit(node.right_node).value else 0))
            elif node.op.type == TT_KEYWORD:
                if node.op.value == "AND":
                    if (self.visit(node.left_node).type == TT_STR or self.visit(node.right_node).type == TT_STR):
                        PrintError(self.text, "Runtime Error", "Invalid operator ' and ' for strings", node.op.line, node.op.start_col)
                    return Token(type_=TT_INT, value_=(1 if self.visit(node.left_node).value and self.visit(node.right_node).value else 0))
                elif node.op.value == "OR":
                    if (self.visit(node.left_node).type == TT_STR or self.visit(node.right_node).type == TT_STR):
                        PrintError(self.text, "Runtime Error", "Invalid operator ' or ' for strings", node.op.line, node.op.start_col)
                    return Token(type_=TT_INT, value_=(1 if self.visit(node.left_node).value or self.visit(node.right_node).value else 0))
                elif node.op.value == "NOT":
                    if self.visit(node.right_node).type == TT_STR:
                        PrintError(self.text, "Runtime Error", "Invalid operator ' not ' for strings", node.op.line, node.op.start_col)
                    return Token(type_=TT_INT, value_=1 if 0 == self.visit(node.right_node).value else 0)
        return None

    def interpret(self) -> Token:
        return self.visit(self.tree)
