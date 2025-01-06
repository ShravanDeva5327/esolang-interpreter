from utils import *

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

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = Position(1, 0, -1)
        self.current_char = None
        self.advance()

    def advance(self) -> None:
        self.pos.advance(self.current_char)
        self.current_char = (self.text[self.pos.idx] if self.pos.idx < len(self.text) else None)

    def tokenize(self) -> list[Token]:
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
                    PrintError(self.text, "Syntax Error", "Invalid Syntax", self.pos.ln, self.pos.col)
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
            elif self.current_char in ";\n":
                tokens.append(Token(ln, col, TT_NEWLINE))
                self.advance()
            else:
                PrintError(self.text, "Syntax Error", "Invalid Syntax", ln, col)
                return None
        return tokens