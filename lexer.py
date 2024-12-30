import string

LETTERS = string.ascii_letters
DIGITS = '0123456789'

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_STR = 'STRING'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_POW = 'POW'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_EQUALS = 'EQUALS'

KEYWORDS = ['var']

class Token:
    def __init__(self, type_: str, value_ : str = None):
        self.type = type_
        self.value = value_
    
    def __repr__(self) -> str:
        if self.type == TT_STR:
            return f'{self.type}(\'{self.value}\')'
        return f'{self.type}({self.value})' if self.value is not None else self.type

    def __eq__(self, other: 'Token') -> bool:
        return self.type == other.type and self.value == other.value
    
    def to_str(self):
        if self.type in (TT_INT, TT_FLOAT, TT_KEYWORD, TT_IDENTIFIER):
            return f'{self.value} '
        elif self.type == TT_PLUS:
            return f'+ '
        elif self.type == TT_MINUS:
            return f'- '
        elif self.type == TT_MUL:
            return f'* '
        elif self.type == TT_DIV:
            return f'/ '
        elif self.type == TT_POW:
            return f'** '
        elif self.type == TT_LPAREN:
            return f'('
        elif self.type == TT_RPAREN:
            return f') '
        elif self.type == TT_EQUALS:
            return f'= '
        elif self.type == TT_STR:
            return f'{self.value} '

class Position:
    def __init__(self, idx: int, ln: int, col: int, filename: str, filetxt: str):
        self.idx = idx
        self.ln =ln   
        self.col = col
        self.filename = filename
        self.filetxt =filetxt

    def advance(self, current_char) -> None:
        self.idx += 1
        self.col += 1
        if current_char == '\n':
            self.col = 0
            self.ln += 1
        

    def copy(self) -> 'Position':
        return Position(self.idx, self.ln, self.col, self.filename, self.filetxt)
    
class LexError():
    def __init__(self, pos: Position, error_name: str, details: str):
        message = f'{error_name}: {details}\nFile {pos.filename}, line {pos.ln}, column {pos.col}'
        raise Exception(message)
  

class Lexer:
    def __init__(self, filename, text):
        self.filename = filename
        self.text = text
        self.pos = Position(-1, 1, 0, filename, text)
        self.current_char = None
        self.advance()
    
    def advance(self) -> None:
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    
        
    def tokenize(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in " \t":
                self.advance()
                continue
            elif self.current_char in DIGITS  + '.':
                num_str = ''
                while self.current_char != None and self.current_char in DIGITS + '.':
                    num_str += self.current_char
                    if self.current_char == '.' and num_str.count('.') > 1:
                        LexError(self.pos.copy(),'Invalid Number', f'{num_str}')
                        return None
                    self.advance()

                if num_str.count('.') == 0: tokens.append(Token(TT_INT, int(num_str)))
                elif num_str.count('.') == 1: tokens.append(Token(TT_FLOAT, float(num_str)))
            elif self.current_char in LETTERS:
                str_ = ''
                while self.current_char != None and self.current_char in LETTERS + DIGITS:
                    str_ += self.current_char
                    self.advance()
                
                tokens.append(Token(TT_KEYWORD, str_) if str_ in KEYWORDS else Token(TT_IDENTIFIER, str_))
            elif self.current_char == '\'':
                self.advance()
                str_ = ''
                while self.current_char != None and self.current_char != '\'':
                    str_ += self.current_char
                    self.advance()
                if self.current_char == None:
                    LexError(self.pos.copy(),'Invalid String', f'\'{str_}')
                    return None
                self.advance()
                tokens.append(Token(TT_STR, str_))
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                self.advance()
                if self.current_char == '*':
                    tokens.append(Token(TT_POW))
                    self.advance()
                else: tokens.append(Token(TT_MUL))
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            elif self.current_char == '=':
                tokens.append(Token(TT_EQUALS))
                self.advance()
            
            else:
                LexError(self.pos.copy(),'Invalid Character', f'"{self.current_char}"')
                return None
        for i in range(len(tokens) - 1):
            if tokens[i].type == TT_INT and tokens[i + 1].type == TT_LPAREN:
                raise Exception(f'Invalid Syntax: int cannot be called')
            if tokens[i].type == TT_FLOAT and tokens[i + 1].type == TT_LPAREN:
                raise Exception(f'Invalid Syntax: float cannot be called')
        return tokens

class ParserError:
    def __init__(self, tokens: list[Token], idx: int, error_name: str, details: str):
        expr = ''
        highlight = ''
        for i in range(len(tokens)):
            if i == idx:
                if tokens[i].type in (TT_INT, TT_FLOAT, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_STR, TT_IDENTIFIER, TT_KEYWORD):
                    expr += f'{tokens[i].to_str()}'
                    highlight += '^'*len(tokens[i].to_str()) + ' '
                elif tokens[i].type == TT_POW:
                    expr += f'{tokens[i].to_str()}'
                    highlight += '^^ '
                elif tokens[i].type == TT_LPAREN:
                    expr += f'{tokens[i].to_str()}'
                    highlight += '^'
                elif tokens[i].type == TT_RPAREN:
                    if expr[-1] == ' ':
                        expr = expr[:-1]
                        highlight = highlight[:-1]
                    expr += f'{tokens[i].to_str()}'
                    highlight += '^'
            else:
                if tokens[i].type in (TT_INT, TT_FLOAT, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_STR, TT_IDENTIFIER, TT_KEYWORD):
                    expr += f'{tokens[i].to_str()}'
                    highlight += ' '*(len(tokens[i].to_str()) + 1)
                elif tokens[i].type == TT_POW:
                    expr += f'{tokens[i].to_str()}'
                    highlight += '   '
                elif tokens[i].type == TT_LPAREN:
                    expr += f'{tokens[i].to_str()}'
                    highlight += ' '
                elif tokens[i].type == TT_RPAREN:
                    if expr[-1] == ' ':
                        expr = expr[:-1]
                        highlight = highlight[:-1]
                    expr += f'{tokens[i].to_str()}'
                    highlight += '  '

        message = f'{expr}\n{highlight}\n{error_name}: {details}'
        raise Exception(message)

class Node:
    def __init__(self, token: Token):
        self.token = token
    
    def __repr__(self) -> str:
        return f'{self.token}'
    
class varAssignNode:
    def __init__(self, var_name: Token, value: Node):
        self.var_name = var_name
        self.value = value

    def __repr__(self) -> str:
        return f'{{assign {self.var_name.value} = {self.value}}}'
    
class varAccessNode:
    def __init__(self, var_name: Token):
        self.var_name = var_name

    def __repr__(self) -> str:
        return f'{{access {self.var_name.value}}}'
class BinOpNode:
    def __init__(self, op: Token, left_node: Node, right_node: Node):
        self.op = op
        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self) -> str:
        return f'{{{self.left_node} {self.op} {self.right_node}}}'
    
class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.idx = -1
        self.advance()

    def advance(self) -> Token:
        self.idx += 1
        if self.idx < len(self.tokens):
            self.current_token = self.tokens[self.idx]
        else :
            self.current_token = Token(None)
        return self.current_token
    
    def factor(self) -> Node:
        if self.idx >= len(self.tokens):
            return None
        token = self.current_token
        if token.type in (TT_INT, TT_FLOAT, TT_STR):
            self.advance()
            return Node(token)
        elif token.type == TT_IDENTIFIER:
            self.advance()
            return varAccessNode(token)
        elif token.type in (TT_PLUS, TT_MINUS):
            self.advance()
            right = self.factor()
            if right == None:
                ParserError(self.tokens, self.idx - 1, 'Syntax Error:', f'Expected an expression after {token.to_str()}')
                return None
            return BinOpNode(Token(TT_MUL), Node(Token(TT_INT, 1)), right) if token.type == TT_PLUS else BinOpNode(Token(TT_MUL), Node(Token(TT_INT, -1)), right)
        elif token.type == TT_LPAREN:
            lParenidx = self.idx
            self.advance()
            result = self.expr()
            if self.current_token.type == TT_RPAREN:
                self.advance()
                return result
            else:
                ParserError(self.tokens, lParenidx, 'Syntax Error', f'( never closed')
                return None
    
    def pow(self) -> BinOpNode:
        return self.bin_op(self.factor, (TT_POW,))
    def term(self) -> BinOpNode:
        res = self.bin_op(self.pow, (TT_MUL, TT_DIV))
        return res
    def expr(self) -> BinOpNode:
        if self.current_token.__eq__(Token(TT_KEYWORD, 'var')):
            self.advance()
            if self.current_token.type != TT_IDENTIFIER:
                ParserError(self.tokens, self.idx, 'Syntax Error', f'Expected an identifier after var')
                return None
            var_name = self.current_token
            self.advance()
            if self.current_token.type != TT_EQUALS:
                ParserError(self.tokens, self.idx, 'Syntax Error', f'Expected an \'=\' after {var_name.to_str()}')
                return None
            self.advance()
            
            expr_ = self.expr()
            return varAssignNode(var_name, expr_)

        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    
    def bin_op(self, func, ops: list[str]) -> BinOpNode:
        left = func()
        while self.current_token.type in ops:
            op = self.current_token
            opidx = self.idx
            if left == None:
                ParserError(self.tokens, opidx, 'Syntax Error', f'Expected an expression before {op.to_str()}')
                return None
            self.advance()
            right = func()
            if right == None:
                ParserError(self.tokens, opidx, 'Syntax Error', f'Expected an expression after {op.to_str()}')
                return None
            left = BinOpNode(op, left, right)
        return left
    
    def parse(self):
        res = self.expr()
        if self.idx < len(self.tokens):
            ParserError(self.tokens, self.idx, 'Syntax Error', f'Expected an operator')
            return None
        return res

class VariablelTable:
    def __init__(self, variables: dict[str, int|float|str] = {}):
        self.variables = variables
    
    def get(self, var_name: str):
        value =  self.variables.get(var_name, None)
        return value
    
    def set(self, var_name: str, value):
        self.variables[var_name] = value

    def remove(self, var_name: str):
        del self.variables[var_name]
class Interpreter:
    def __init__(self, tree: BinOpNode|Node, variables: dict[str, int|float|str] = {}):
        self.tree = tree
        self.variable_table = VariablelTable(variables)
    
    def visit(self, node: BinOpNode|Node|varAccessNode|varAssignNode) -> Token:
        if isinstance(node, Node):
            return node.token
        elif isinstance(node, varAssignNode):
            self.variable_table.set(node.var_name.value, self.visit(node.value).value)
            return Token(self.visit(node.value).type, self.visit(node.value).value)
        elif isinstance(node, varAccessNode):
            value = self.variable_table.get(node.var_name.value)
            if value is None:
                raise Exception(f'Runtime Error: Variable \'{node.var_name.value}\' not defined')
            return Token(TT_INT, value) if isinstance(value, int) else Token(TT_FLOAT, value) if isinstance(value, float) else Token(TT_STR, value)
        elif isinstance(node, BinOpNode):
            if node.op.type == TT_PLUS:
                if self.visit(node.left_node).type == TT_STR:
                    if self.visit(node.right_node).type == TT_STR:
                        return Token(TT_STR, self.visit(node.left_node).value + self.visit(node.right_node).value)
                    else:
                        raise Exception('Runtime Error: Cannot add string to a non-string')
                elif self.visit(node.right_node).type == TT_STR:
                    raise Exception('Runtime Error: Cannot add string to a non-string')
                val = self.visit(node.left_node).value + self.visit(node.right_node).value
                type = TT_INT if self.visit(node.left_node).type == TT_INT and self.visit(node.right_node).type == TT_INT else TT_FLOAT
                return Token(type, val)
            elif node.op.type == TT_MINUS:
                if self.visit(node.left_node).type == TT_STR or self.visit(node.right_node).type == TT_STR:
                    raise Exception('Runtime Error: Invalid operator \' - \' for strings')
                val = self.visit(node.left_node).value - self.visit(node.right_node).value
                type = TT_INT if self.visit(node.left_node).type == TT_INT and self.visit(node.right_node).type == TT_INT else TT_FLOAT
                return Token(type, val)
            elif node.op.type == TT_MUL:
                if self.visit(node.left_node).type == TT_STR:
                    if self.visit(node.right_node).type == TT_INT:
                        return Token(TT_STR, self.visit(node.left_node).value * self.visit(node.right_node).value)
                    else:
                        raise Exception('Runtime Error: Cannot multiply string with a non-integer')
                elif self.visit(node.right_node).type == TT_STR:
                    if self.visit(node.left_node).type == TT_INT:
                        return Token(TT_STR, self.visit(node.left_node).value * self.visit(node.right_node).value)
                    else:
                        raise Exception('Runtime Error: Cannot multiply string with a non-integer')
                val = self.visit(node.left_node).value * self.visit(node.right_node).value
                type = TT_INT if self.visit(node.left_node).type == TT_INT and self.visit(node.right_node).type == TT_INT else TT_FLOAT
                return Token(type, val)
            elif node.op.type == TT_DIV:
                if self.visit(node.right_node).value == 0:
                    raise Exception('Runtime Error: Division by zero')
                if self.visit(node.left_node).type == TT_STR or self.visit(node.right_node).type == TT_STR:
                    raise Exception('Runtime Error: Invalid operator \' / \' for strings')
                val = self.visit(node.left_node).value / self.visit(node.right_node).value
                type = TT_INT if self.visit(node.left_node).typ ==  TT_INT and self.visit(node.right_node).type == TT_INT else TT_FLOAT
                return Token(type, val)
            elif node.op.type == TT_POW:
                if self.visit(node.left_node).type == TT_STR or self.visit(node.right_node).type == TT_STR:
                    raise Exception('Runtime Error: Invalid operator \' ** \' for strings')
                val = self.visit(node.left_node).value ** self.visit(node.right_node).value
                type = TT_INT if self.visit(node.left_node).type == TT_INT and self.visit(node.right_node).type == TT_INT and self.visit(node.right_node).value >= 0 else TT_FLOAT
                return Token(type, val)
        
    def interpret(self) -> Token:
        return self.visit(self.tree)
