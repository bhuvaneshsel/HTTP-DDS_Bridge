from antlr4 import *
from antlr4_generated.IDLLexer import IDLLexer
from antlr4_generated.IDLParser import IDLParser
from antlr4_generated.IDLListener import IDLListener

class StructFieldCollector(IDLListener):
    def __init__(self):
        self.structs = {}
        self.current_struct = None

    def enterStruct_type(self, ctx):
        struct_name = ctx.identifier().getText()
        self.current_struct = struct_name
        self.structs[struct_name] = []

    def exitStruct_type(self, ctx):
        self.current_struct = None

    def exitMember(self, ctx):
        if not self.current_struct:
            return

        type_spec = ctx.type_spec()
        type_text = type_spec.getText()

        for declarator in ctx.declarators().declarator():
            if declarator.complex_declarator():
                complex_decl = declarator.complex_declarator()
                array_decl = complex_decl.array_declarator()

                # Get the variable name before the first '['
                name = declarator.getText().split('[')[0]

                # Join all dimensions, e.g., "[3][4]"
                size_list = array_decl.fixed_array_size()
                sizes = "][".join(dim.getText() for dim in size_list)

                # Build full type: short[3][4]
                full_type = f"{type_text}[{sizes}]"
                self.structs[self.current_struct].append((full_type, name))
            else:
                name = declarator.getText()
                self.structs[self.current_struct].append((type_text, name))
        

def parse_structs_with_antlr(idl_path):
    input_stream = FileStream(idl_path)
    lexer = IDLLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = IDLParser(token_stream)
    tree = parser.specification()

    walker = ParseTreeWalker()
    listener = StructFieldCollector()
    walker.walk(listener, tree)

    return listener.structs