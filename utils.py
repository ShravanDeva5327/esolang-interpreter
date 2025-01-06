import string

LETTERS = string.ascii_letters
DIGITS = "0123456789"
NUMERALS = ".0123456789"
BOOL_VAR = {"true", "false"}

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
TT_NEWLINE = "NEWLINE"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_EQUALS = "EQUALS"
TT_ISEQ = "ISEQ"
TT_NOTEQ = "NOTEQ"
TT_LT = "LT"
TT_GT = "GT"
TT_LTE = "LTE"
TT_GTE = "GTE"

DATA_TYPES = (TT_INT, TT_FLOAT, TT_STR, TT_BOOL)
NUM_DATA_TYPES = (TT_INT, TT_FLOAT)
ARITH_OP = (TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_POW)
PAREN = (TT_LPAREN, TT_RPAREN)
COMPARATORS = (TT_ISEQ, TT_NOTEQ, TT_LT, TT_GT, TT_LTE, TT_GTE)

KEYWORDS = ["and", "or", "not", "print", "true", "false",
            "if", "then", "end", "elif", "else","for", "to", "step", "while", "do"]

def line_in_text(text: str, line: int) -> str:
    lines = text.split("\n")
    return lines[line - 1] if line - 1 < len(lines) else ""

class PrintError:
    def __init__(self, text: str, error_name: str, details: str, line: int, start_col: int = None):
        error_line = line_in_text(text, line) + "\n"
        if start_col is None:
            start_col = len(error_line)
        wiggle = " " * (start_col - 1) + "^^" + "\n"
        message = f"{error_line}{wiggle}{error_name}: {details}\nline {line}, column {start_col}"
        raise Exception(message)
    
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
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value
    
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
    def __init__(self, if_case: list[Node], else_case: list[Node]):
        self.if_case = if_case
        self.else_case = else_case

    def __repr__(self) -> str:
        string = ""
        string += f"if {self.if_case[0]} then {self.if_case[1]}\n"
        if self.else_case != None:
            string += f"else {self.else_case}"
        
        return f"{string}"
            
class forNode:
    def __init__(self, identifier: Token, start: Node, end: Node, step: Node, body: list[Node]):
        self.identifier = identifier
        self.start = start
        self.end = end
        self.step = step
        self.body = body
    
    def __repr__(self) -> str:
        return f"for {self.start} to {self.end} step {self.step} do {self.body}"
    
class WhileNode:
    def __init__(self, condition: Node, body: list[Node]):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"while {self.condition} do {self.body}"