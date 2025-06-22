import ast
from collections import defaultdict

def analyze_python(code):
    issues = {
        'lexical': [],
        'syntactic': [],
        'semantic': []
    }

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        issues['syntactic'].append({
            'type': 'error',
            'message': f'SyntaxError: {e.msg}',
            'line': e.lineno,
            'suggestion': 'Fix the syntax'
        })
        return issues

    defined_vars = set()
    used_vars = set()
    defined_funcs = set()
    used_funcs = set()
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defined_funcs.add(node.name)
            if not node.body or all(isinstance(stmt, ast.Pass) for stmt in node.body):
                issues['semantic'].append({
                    'type': 'warning',
                    'message': f"Function '{node.name}' has an empty body",
                    'line': node.lineno,
                    'suggestion': 'Add implementation or remove the function'
                })
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                used_funcs.add(node.func.id)
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            imports.append((node.lineno, node))
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined_vars.add(target.id)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_vars.add(node.id)

    # Unused variables
    for var in defined_vars:
        if var not in used_vars:
            issues['semantic'].append({
                'type': 'warning',
                'message': f"Variable '{var}' is defined but not used",
                'line': 'unknown',
                'suggestion': 'Remove or use this variable'
            })

    # Unused functions
    for func in defined_funcs:
        if func not in used_funcs:
            issues['semantic'].append({
                'type': 'warning',
                'message': f"Function '{func}' is defined but not used",
                'line': 'unknown',
                'suggestion': 'Remove or call this function if needed'
            })

    # Unused imports
    for lineno, imp in imports:
        names = [n.name for n in imp.names]
        for name in names:
            if name not in used_vars and name not in used_funcs:
                issues['lexical'].append({
                    'type': 'info',
                    'message': f"Import '{name}' appears unused",
                    'line': lineno,
                    'suggestion': 'Remove unused import to keep code clean'
                })

    return issues
