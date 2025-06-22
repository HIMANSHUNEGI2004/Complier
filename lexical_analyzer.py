import re
from collections import defaultdict

def analyze_lexical(code):
    issues = []
    
    try:
        # Check for non-ASCII characters
        non_ascii = re.findall(r'[^\x00-\x7F]', code)
        if non_ascii:
            issues.append({
                'type': 'warning',
                'message': 'Non-ASCII characters detected',
                'line': 'multiple',
                'suggestion': 'Use only ASCII characters in your code'
            })
        
        # Check for tabs vs spaces
        if '\t' in code and ' ' in code:
            issues.append({
                'type': 'warning',
                'message': 'Mixed tabs and spaces',
                'line': 'multiple',
                'suggestion': 'Consistently use either tabs or spaces for indentation'
            })
        
        # Check for suspicious character sequences
        suspicious_sequences = [
            ('->', 'Pointer access operator'),
            ('&&', 'Logical AND operator'),
            ('||', 'Logical OR operator'),
            ('==', 'Equality operator (ensure this is not assignment =)')
        ]
        
        for seq, desc in suspicious_sequences:
            if seq in code:
                issues.append({
                    'type': 'info',
                    'message': f'{desc} detected: {seq}',
                    'line': 'multiple',
                    'suggestion': f'Ensure proper usage of {desc}'
                })
        
    except Exception as e:
        issues.append({
            'type': 'error',
            'message': f'Lexical analysis failed: {str(e)}',
            'line': 'unknown',
            'suggestion': 'Check for unusual characters or formatting issues'
        })
    
    return issues