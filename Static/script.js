// Configuration - MUST match your Flask server
const BACKEND_URL = 'http://localhost:8080';

// Initialize editor
const editor = CodeMirror.fromTextArea(document.getElementById('editor'), {
    mode: 'text/x-csrc',
    theme: 'dracula',
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    lineWrapping: true,
    autoCloseBrackets: true,
    matchBrackets: true,
    extraKeys: {
        'Ctrl-Enter': analyzeCode,
        'Cmd-Enter': analyzeCode
    }
});

// Main analysis function
async function analyzeCode() {
    const issuesList = document.getElementById('issues-list');
    issuesList.innerHTML = '<div class="loading">Analyzing code...</div>';

    try {
        const response = await fetch(`${BACKEND_URL}/analyze`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
            code: editor.getValue(),
            language: document.getElementById('language-select').value
            })
        });

        if (!response.ok) {
            throw new Error('Server returned error');
        }

        const data = await response.json();
        
        // Clear previous errors if any
        issuesList.innerHTML = '';
        
        // Display all issues
        const allIssues = [
            ...(data.lexical || []),
            ...(data.syntactic || []),
            ...(data.semantic || [])
        ];

        if (allIssues.length === 0) {
            issuesList.innerHTML = '<div class="issue info">No issues found</div>';
            return;
        }

        allIssues.forEach(issue => {
            const div = document.createElement('div');
            div.className = `issue ${issue.type}`;
            div.innerHTML = `
                <h3>${issue.message}</h3>
                <div class="meta">
                    <span>Line: ${issue.line || 'unknown'}</span>
                    <span>Type: ${issue.type}</span>
                </div>
                <div class="suggestion">${issue.suggestion}</div>
            `;
            issuesList.appendChild(div);
        });

        // Apply current filter after loading new issues
        const activeFilter = document.querySelector('.filter-btn.active').dataset.type;
        if (activeFilter !== 'all') {
            document.querySelectorAll('.issue').forEach(issue => {
                if (!issue.classList.contains(activeFilter)) {
                    issue.style.display = 'none';
                }
            });
        }

    } catch (error) {
        issuesList.innerHTML = `
            <div class="issue error">
                <h3>Connection Error</h3>
                <p>Could not reach analysis server</p>
                <div class="suggestion">
                    <ol>
                        <li>Make sure the Python server is running</li>
                        <li>Run: <code>python app.py</code></li>
                        <li>Verify the server starts on port 8080</li>
                        <li>Test with: <code>curl ${BACKEND_URL}/analyze -X POST -H "Content-Type: application/json" -d '{"code":"int main(){}"}'</code></li>
                    </ol>
                </div>
            </div>`;
        console.error('Analysis failed:', error);
    }
}

// Initialize analyze button
document.getElementById('analyze-btn').addEventListener('click', analyzeCode);

// Filter functionality
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // Update active button
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const filterType = this.dataset.type;
        const issues = document.querySelectorAll('.issue');
        
        issues.forEach(issue => {
            if (filterType === 'all') {
                issue.style.display = 'block';
            } else {
                issue.style.display = issue.classList.contains(filterType) ? 'block' : 'none';
            }
        });
    });
});