import re
from collections import defaultdict

def analyze_semantics(code):
    issues = []
    
    try:
        if not code.strip():
            return issues
            
        lines = code.split('\n')
        
        # Memory leak detection
        malloc_no_free = re.findall(r'(\w+)\s*=\s*malloc\(.*\)', code)
        for var in malloc_no_free:
            if f'free({var})' not in code:
                line = code[:code.index(f'{var} = malloc')].count('\n') + 1
                issues.append({
                    'type': 'error',
                    'message': f'Potential memory leak: {var} allocated with malloc but not freed',
                    'line': line,
                    'suggestion': 'Add free() call for this variable when done using it'
                })
        
        # Uninitialized variables
        declarations = re.findall(r'int\s+(\w+)\s*;', code)
        for var in declarations:
            if not re.search(fr'{var}\s*=', code):
                line = code[:code.index(f'int {var};')].count('\n') + 1
                issues.append({
                    'type': 'warning',
                    'message': f'Variable {var} declared but not initialized',
                    'line': line,
                    'suggestion': 'Initialize variables when declaring them to avoid undefined behavior'
                })
        
        # Unused variables
        variables = re.findall(r'(int|char|float|double)\s+(\w+)\s*[;=]', code)
        var_usage = defaultdict(int)
        
        for var in variables:
            var_name = var[1]
            var_usage[var_name] = 0
        
        for var_name in var_usage:
            var_usage[var_name] = len(re.findall(fr'\b{var_name}\b', code))
        
        for var_name, count in var_usage.items():
            if count <= 1:
                line = code[:code.index(f'{var_name} ')].count('\n') + 1
                issues.append({
                    'type': 'warning',
                    'message': f'Variable {var_name} declared but possibly unused',
                    'line': line,
                    'suggestion': 'Remove unused variables or check if they should be used'
                })
        
        # Dangerous functions
        dangerous_funcs = [
            ('gets', 'gets() is dangerous and deprecated', 'Use fgets() instead'),
            ('strcpy', 'strcpy() is unsafe', 'Use strncpy() or other safe alternatives'),
            ('sprintf', 'sprintf() is unsafe', 'Use snprintf() instead'),
            ('scanf', 'scanf() can cause buffer overflows', 'Use fgets() + sscanf() with length checks')
        ]
        
        for func, msg, suggestion in dangerous_funcs:
            if func + '(' in code:
                matches = re.finditer(re.escape(func) + r'\(', code)
                for match in matches:
                    line = code[:match.start()].count('\n') + 1
                    issues.append({
                        'type': 'error',
                        'message': msg,
                        'line': line,
                        'suggestion': suggestion
                    })
                    
    except Exception as e:
        issues.append({
            'type': 'error',
            'message': f'Semantic analysis failed: {str(e)}',
            'line': 'unknown',
            'suggestion': 'Check for complex patterns that might confuse the analyzer'
        })
    
    return issues