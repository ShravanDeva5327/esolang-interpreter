from utils import *

class VariableTable:
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
        self.variable_table = VariableTable(variables)

    def visit(self, node: BinOpNode | Node | varAccessNode | varAssignNode) -> Token:
        if isinstance(node, Node):
            return node.token
        elif isinstance(node, ifNode):
            if self.visit(node.if_case[0]).value:
                for statement in node.if_case[1]:
                    self.visit(statement)
            if node.else_case != None:
                return self.visit(node.else_case)
            return Token()
        elif isinstance(node, forNode):
            self.variable_table.set(node.identifier.value, self.visit(node.start).value)
            i = self.visit(node.start).value
            while (self.visit(node.start).value - self.visit(node.end).value) * (i - self.visit(node.end).value) >= 0:
                self.variable_table.set(node.identifier.value, i)
                for statement in node.body:
                    self.visit(statement)
                i += self.visit(node.step).value
            return Token()
        elif isinstance(node, WhileNode):
            while self.visit(node.condition).value:
                for statement in node.body:
                    self.visit(statement)
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
            lvalue = self.visit(node.left_node).value
            ltype = self.visit(node.left_node).type
            rvalue = self.visit(node.right_node).value
            rtype = self.visit(node.right_node).type

            result_value = None
            result_type = None

            def no_type_mismatch(op):
                if ltype != rtype:
                    if ltype not in NUM_DATA_TYPES or rtype not in NUM_DATA_TYPES:
                        PrintError(self.text, "Runtime Error", f"Invalid operator '{op}' for '{ltype}' and '{rtype}'", node.op.line, node.op.start_col)

            if node.op.type == TT_PLUS:
                no_type_mismatch("+")
                result_value = lvalue + rvalue
                result_type = (TT_STR if ltype == TT_STR else TT_INT if ltype == TT_INT and rtype == TT_INT else TT_FLOAT)
            elif node.op.type == TT_MINUS:
                if ltype == TT_STR or rtype == TT_STR:
                    PrintError(self.text, "Runtime Error", "Invalid operator '-' for string", node.op.line, node.op.start_col)
                result = lvalue - rvalue
                result_type = TT_FLOAT if ltype == TT_FLOAT or rtype == TT_FLOAT else TT_INT
            elif node.op.type == TT_MUL:
                if ltype == TT_STR and rtype == TT_INT or ltype == TT_INT and rtype == TT_STR:
                    result_value = lvalue * rvalue
                    result_type = TT_STR
                elif ltype == TT_STR or rtype == TT_STR:
                    PrintError(self.text, "Runtime Error", "Invalid operator '*' for string and non-integer", node.op.line, node.op.start_col)
                else:
                    result_value = lvalue * rvalue
                    result_type = TT_INT if ltype == TT_INT and rtype == TT_INT else TT_FLOAT
            elif node.op.type == TT_DIV:
                if ltype == TT_STR or rtype == TT_STR:
                    PrintError(self.text, "Runtime Error", "Invalid operator '/' for string", node.op.line, node.op.start_col)
                if rvalue == 0:
                    PrintError(self.text, "Runtime Error", "Division by zero", node.op.line, node.op.start_col)
                result_value = lvalue / rvalue
                result_type = TT_FLOAT
            elif node.op.type == TT_POW:
                if ltype == TT_STR or rtype == TT_STR:
                    PrintError(self.text, "Runtime Error", "Invalid operator '**' for string", node.op.line, node.op.start_col)
                result_value = lvalue ** rvalue
                result_type = TT_INT if ltype == TT_INT and rtype == TT_INT and rvalue >= 0 else TT_FLOAT
            elif node.op.type in COMPARATORS:
                opertations = {
                    TT_ISEQ: lambda: no_type_mismatch("==") or (1 if lvalue == rvalue else 0),
                    TT_NOTEQ: lambda: no_type_mismatch("!=") or (1 if lvalue != rvalue else 0),
                    TT_LT: lambda: no_type_mismatch("<") or (1 if lvalue < rvalue else 0),
                    TT_GT: lambda: no_type_mismatch(">") or (1 if lvalue > rvalue else 0),
                    TT_LTE: lambda: no_type_mismatch("<=") or (1 if lvalue <= rvalue else 0),
                    TT_GTE: lambda: no_type_mismatch(">=") or (1 if lvalue >= rvalue else 0),
                }
                result_value = opertations[node.op.type]()
                result_type = TT_INT
            elif node.op.type == TT_KEYWORD:
                if node.op.value == "AND":
                    if ltype == TT_STR or rtype == TT_STR:
                        PrintError(self.text, "Runtime Error", "Invalid operator 'AND' for string", node.op.line, node.op.start_col)
                    result_value = (1 if lvalue and rvalue else 0)
                if node.op.value == "OR":
                    if ltype == TT_STR or rtype == TT_STR:
                        PrintError(self.text, "Runtime Error", "Invalid operator 'OR' for string", node.op.line, node.op.start_col)
                    result_value = (1 if lvalue or rvalue else 0)
                if node.op.value == "NOT":
                    if ltype == TT_STR:
                        PrintError(self.text, "Runtime Error", "Invalid operator 'NOT' for string", node.op.line, node.op.start_col)
                    result_value = (1 if rvalue == 0 else 0)
                result_type = TT_INT
            
            return Token(type_=result_type, value_=result_value)
        
        return None

    def interpret(self) -> Token:
        return self.visit(self.tree)