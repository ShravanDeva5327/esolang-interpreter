from utils import *

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
            self.current_token = Token()
        return self.current_token
    
    def move_back(self) -> Token:
        self.idx -= 1
        if self.idx >= 0:
            self.current_token = self.tokens[self.idx]
        else:
            self.current_token = Token()
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
                PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line, token.start_col + 1)
                return None
            return (BinOpNode(Token(type_=TT_MUL), Node(Token(type_=TT_INT, value_=1)), right) if token.type == TT_PLUS else BinOpNode(Token(type_=TT_MUL), Node(Token(type_=TT_INT, value_=-1)), right))
        elif token.type == TT_LPAREN:
            self.advance()
            result = self.expr()
            if self.current_token.type == TT_RPAREN:
                self.advance()
                return result
            else:
                PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line)
                return None
        elif token.type == TT_KEYWORD:
            if token.value == "IF":
                else_block = None
                self.advance()
                condition = self.expr()
                if condition == None:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line)
                    return None
                if self.current_token == Token():
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line)
                    return None
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="THEN")):
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
                    return None
                self.advance()
                if_block = [self.expr()]
                while self.current_token.type == TT_NEWLINE:
                    self.advance()
                    if_block.append(self.expr())
                if if_block == None:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line)
                    return None
                if self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="END")):
                    ifcase = (condition, if_block)
                    self.advance()
                    return ifNode(ifcase, else_block)
                elif self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="ELSE")):
                    ifcase = (condition, if_block)
                    else_ln = self.current_token.line
                    self.advance()
                    else_block = [self.expr()]
                    while self.current_token.type == TT_NEWLINE:
                        self.advance()
                        else_block.append(self.expr())
                    if else_block == None:
                        PrintError(self.text, "Syntax Error", "Invalid Syntax", else_ln)
                        return None
                    if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="END")):
                        PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line)
                        return None
                    self.advance()
                    return ifNode(ifcase, else_block)
                else:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line)
                    return None
            elif token.value == "FOR":
                self.advance()
                if self.current_token == Token():
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line)
                if self.current_token.type != TT_IDENTIFIER:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
                var = self.current_token
                self.advance()
                if self.current_token == Token():
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line)
                if self.current_token.type != TT_EQUALS:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
                self.advance()
                start_ = self.expr()
                if start_ == None:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", var.line)
                
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="TO")):
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line, token.start_col + 1)
                self.advance()

                end_ = self.expr()
                if end_ == None:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
                
                step_ = Node(Token(type_=TT_INT, value_=1))
                if self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="STEP")):
                    self.advance()
                    step_ = self.expr()
                    if step_ == None:
                        PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
                
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="DO")):
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
                self.advance()
                block = [self.expr()]
                while self.current_token.type == TT_NEWLINE:
                    self.advance()
                    block.append(self.expr())
                if block == None:
                    PrintError(self.text, "Syntax Error", "Expected an expression after 'do'", self.current_token.line, self.current_token.start_col)
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="END")):
                    PrintError(self.text, "Syntax Error", "Expected ')' after statements", self.current_token.line, self.current_token.start_col)
                self.advance()
                return forNode(var, start_, end_, step_, block)

            elif token.value == "WHILE":    
                self.advance()
                condition = self.expr()
                if condition == None:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", token.line, token.start_col)
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="DO")):
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
                self.advance()
                block = [self.expr()]
                while self.current_token.type == TT_NEWLINE:
                    self.advance()
                    block.append(self.expr())
                if block == None:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
                if not self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="END")):
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
                self.advance()
                return WhileNode(condition, block)
            
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
                                PrintError(self.text, "Syntax Error", "Invalid Syntax", lparen_ln, lparen_col)
                        elif self.current_token.type == TT_RPAREN:
                            self.advance()
                            return printNode(tokens)
                        else:
                            PrintError(self.text, "Syntax Error", "Invalid Syntax", lparen_ln)
                else:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", pr_ln, pr_col)
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
                PrintError(self.text, "Syntax Error", "Invalid Syntax'", ln)
                return None
            return BinOpNode(Token(type_=TT_ISEQ), Node(Token(type_=TT_INT, value_=0)), right)
        return self.bin_op(self.arith_expr, COMPARATORS)

    def expr(self) -> BinOpNode:        
        if self.current_token.type == TT_IDENTIFIER:
            var_name = self.current_token
            self.advance()
            if self.current_token.type == TT_EQUALS:
                ln = self.current_token.line
                col = self.current_token.start_col
                self.advance()
                value = self.expr()
                if value == None:
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", ln, col)
                    return None
                return varAssignNode(var_name, value)
            else:
                self.move_back()

        return self.and_or()

    def bin_op(self, func, ops: list[str]) -> BinOpNode:
        left = func()
        while self.current_token.type in ops:
            op = self.current_token
            if left == None:
                PrintError(self.text, "Syntax Error", "Invalid Syntax", op.line, op.start_col - 1)
                return None
            self.advance()
            right = func()
            if right == None:
                PrintError(self.text, "Syntax Error", "Invalid Syntax", op.line, op.start_col + 1)
            left = BinOpNode(op, left, right)
        return left

    def and_or(self) -> Node:
        left = self.comp_expr()
        while self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="AND")) or self.current_token.__eq__(Token(type_=TT_KEYWORD, value_="OR")):
            op = self.current_token
            opidx = self.idx
            if left == None:
                PrintError(self.text, "Syntax Error", "Invalid Syntax", op.line, op.start_col)
                return None
            self.advance()
            right = self.comp_expr()
            if right == None:
                PrintError(self.text, "Syntax Error", "Invalid Syntax", op.line, op.start_col)
                return None
            left = BinOpNode(op, left, right)
        return left

    def parse(self) -> list[Node]:
        res = [self.expr()]
        while self.current_token.type == TT_NEWLINE:
            self.advance()
            res.append(self.expr())
        if self.idx < len(self.tokens):
            PrintError(self.text, "Syntax Error", "Invalid Syntax", self.current_token.line, self.current_token.start_col)
            return None
        return res