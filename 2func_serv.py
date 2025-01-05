from flask import Flask, render_template, request, jsonify
import io
import sys
import traceback

app = Flask(__name__)

# In-memory storage for saved functions (for demonstration purposes)
saved_functions = {}

@app.route('/')
def index():
    return render_template('index.html', saved_functions=saved_functions.keys())

@app.route('/execute', methods=['POST'])
def execute_code():
    code = request.form.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    # Redirect stdout and stderr to capture output
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    try:
        # --- SECURITY WARNING: EXECUTING ARBITRARY CODE IS DANGEROUS! ---
        # BE VERY CAREFUL WHEN IMPLEMENTING THIS IN A REAL-WORLD SCENARIO.
        # Consider sandboxing techniques (see security section below).
        exec(code, globals())
        output = redirected_output.getvalue()
        error = redirected_error.getvalue()
    except Exception:
        error = traceback.format_exc()
        output = ""
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return jsonify({'output': output, 'error': error})

@app.route('/save', methods=['POST'])
def save_function():
    name = request.form.get('name')
    code = request.form.get('code')
    if not name or not code:
        return jsonify({'error': 'Name and code are required'}), 400
    saved_functions[name] = code
    return jsonify({'message': f'Function "{name}" saved successfully'}), 200

@app.route('/load/<name>')
def load_function(name):
    if name in saved_functions:
        return jsonify({'code': saved_functions[name]}), 200
    else:
        return jsonify({'error': 'Function not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)