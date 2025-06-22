from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from analyzer.lexical_analyzer import analyze_lexical
from analyzer.syntactic_analyzer import analyze_syntax
from analyzer.semantic_analyzer import analyze_semantics
from analyzer.python_analyzer import analyze_python

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        code = request.json.get('code', '')
        language = request.json.get('language', 'c')  # default to C if not specified

        if language.lower() == 'python':
            python_issues = analyze_python(code)
            return jsonify({
                'lexical': python_issues.get('lexical', []),
                'syntactic': python_issues.get('syntactic', []),
                'semantic': python_issues.get('semantic', []),
                'status': 'success'
            })
        else:
            return jsonify({
                'lexical': analyze_lexical(code),
                'syntactic': analyze_syntax(code),
                'semantic': analyze_semantics(code),
                'status': 'success'
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("\n[SUCCESS] Backend running at http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)