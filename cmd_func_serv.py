from flask import Flask, render_template, request, jsonify
import io
import sys
import traceback
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('cmd-index.html')

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

# New route to handle command line input
@app.route('/terminal', methods=['POST'])
def terminal_command():
    command = request.form.get('command')
    if not command:
        return jsonify({'error': 'No command provided'}), 400

    try:
        # Execute the command in a subshell and capture output
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        error = result.stderr
        return jsonify({'output': output, 'error': error})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
