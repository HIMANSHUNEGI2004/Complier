import re
from pycparser import c_parser, c_ast

def analyze_syntax(code):
    issues = []

    try:
        # 🔥 Strip preprocessor directives like #include, #define, etc.
        clean_code = '\n'.join(
            line for line in code.split('\n')
            if not line.strip().startswith('#')
        )

        # Parse cleaned code
        parser = c_parser.CParser()
        parser.parse(clean_code)

    except Exception as e:
        error_msg = str(e)
        line_match = re.search(r'line (\d+)', error_msg)
        line = line_match.group(1) if line_match else 'unknown'
        
        suggestion = "Check for syntax errors"
        if 'expected' in error_msg.lower():
            suggestion = "Check for missing or misplaced syntax elements"
        elif 'before' in error_msg.lower():
            suggestion = "Check the syntax before the indicated position"
        
        issues.append({
            'type': 'error',
            'message': f'Syntax error: {error_msg}',
            'line': line,
            'suggestion': suggestion
        })
    
    # Additional checks
    try:
        # Check for missing semicolons
        lines = code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped.endswith('}') or stripped.endswith('{') or 
                stripped.endswith(';') or not stripped or 
                stripped.startswith('#') or stripped.startswith('//')):
                continue
                
            if not re.search(r'[;\{\}]$', stripped):
                issues.append({
                    'type': 'error',
                    'message': 'Missing semicolon',
                    'line': i + 1,
                    'suggestion': 'Add semicolon at the end of the statement'
                })
        
        # Check for assignment in condition
        assign_in_cond = re.finditer(r'if\s*\(.*=.*\)', code)
        for match in assign_in_cond:
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'type': 'warning',
                'message': 'Assignment in condition (possible typo for ==)',
                'line': line,
                'suggestion': 'Did you mean to use == instead of =?'
            })
        
        # Check for empty if/while/for bodies
        empty_bodies = re.finditer(r'(if|while|for)\s*\(.*\)\s*;', code)
        for match in empty_bodies:
            line = code[:match.start()].count('\n') + 1
            issues.append({
                'type': 'warning',
                'message': f'Empty {match.group(1)} body with just a semicolon',
                'line': line,
                'suggestion': 'This might be a mistake. Add proper body or comment if intentional'
            })
            
    except Exception as e:
        issues.append({
            'type': 'error',
            'message': f'Syntactic pattern matching failed: {str(e)}',
            'line': 'unknown',
            'suggestion': 'Check for complex syntax patterns'
        })
    
    return issues