import llvmlite.ir as irimport llvmlite.binding as llvmfrom .parse.ast import *class CodegenError(Exception):    passclass LLVMCodeGenerator:    def __init__(self):        self.module = ir.Module()        self.builder = None        self.funcsymtab = {}    def generate_code(self, node):        # assert isinstance(node, (Prototype, Function))        return self._codegen(node)    def _codegen(self, node):        method = '_codegen_' + node.__class__.__name__.lower()        return getattr(self, method)(node)    def _codegen_number(self, node):        return ir.Constant(ir.DoubleType(), float(node.val))    def _codegen_variable(self, node):        return self.funcsymtab[node.name]    def _codegen_binary(self, node):        lhs = self._codegen(node.lhs)        rhs = self._codegen(node.rhs)        if node.op == '+':            return self.builder.fadd(lhs, rhs, 'addtmp')        if node.op == '-':            return self.builder.fsub(lhs, rhs, 'subtmp')        if node.op == '*':            return self.builder.fmul(lhs, rhs, 'multmp')        if node.op == '<':            cmp = self.builder.fcmp_unordered('<', lhs, rhs, 'cmptmp')            return self.builder.uitofp(cmp, ir.DoubleType(), 'booltmp')        else:            raise CodegenError('Unknown binary operator', node.op)    def _codegen_call(self, node):        callee_func = self.module.globals.get(node.callee, None)        if callee_func is None or not isinstance(callee_func, ir.Function):            raise CodegenError('Call to unknown function', node.callee)        if len(callee_func.args) != len(node.args):            raise CodegenError('Call argument length mismatch', node.callee)        call_args = [self._codegen(arg) for arg in node.args]        return self.builder.call(callee_func, call_args, 'calltmp')    def _codegen_prototype(self, node):        funcname = node.name        func_ty = ir.FunctionType(ir.DoubleType(),                                  [ir.DoubleType()] * len(node.argnames))        if funcname in self.module.globals:            existing_func = self.module[funcname]            if not isinstance(existing_func, ir.Function):                raise CodegenError('Function/Global name collision', funcname)            if not existing_func.is_declaration():                raise CodegenError('Redefinition of {0}'.format(funcname))            if len(existing_func.function_type.args) != len(func_ty.args):                raise CodegenError(                    'Redefinition with different number of arguments')            func = self.module.globals[funcname]        else:            func = ir.Function(self.module, func_ty, funcname)        for i, arg in enumerate(func.args):            arg.name = node.argnames[i]            self.funcsymtab[arg.name] = arg        return func    def _codegen_function(self, node):        self.funcsymtab = {}        func = self._codegen(node.proto)        bb_entry = func.append_basic_block('entry')        self.builder = ir.IRBuilder(bb_entry)        retval = self._codegen(node.body)        self.builder.ret(retval)        return func