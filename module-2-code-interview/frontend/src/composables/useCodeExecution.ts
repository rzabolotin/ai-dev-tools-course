// Pyodide singleton instance
let pyodideInstance: any = null;
let pyodideLoading: Promise<any> | null = null;

async function loadPyodide() {
  if (pyodideInstance) {
    return pyodideInstance;
  }

  if (pyodideLoading) {
    return pyodideLoading;
  }

  pyodideLoading = (async () => {
    try {
      // Load Pyodide from CDN
      const pyodideScript = document.createElement('script');
      pyodideScript.src = 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js';

      await new Promise((resolve, reject) => {
        pyodideScript.onload = resolve;
        pyodideScript.onerror = reject;
        document.head.appendChild(pyodideScript);
      });

      // @ts-ignore - Pyodide is loaded globally
      pyodideInstance = await window.loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/',
      });

      return pyodideInstance;
    } catch (error) {
      pyodideLoading = null;
      throw error;
    }
  })();

  return pyodideLoading;
}

export async function executeCode(
  code: string,
  language: string
): Promise<{ output: string; error: string | null }> {
  if (language === 'javascript' || language === 'typescript') {
    return executeJavaScript(code);
  }

  if (language === 'python') {
    return executePython(code);
  }

  return {
    output: '',
    error: `Execution for ${language} is not supported yet.`,
  };
}

async function executePython(code: string): Promise<{ output: string; error: string | null }> {
  try {
    const pyodide = await loadPyodide();

    // Capture stdout
    const capturedOutput: string[] = [];

    // Redirect Python stdout to capture prints
    await pyodide.runPythonAsync(`
import sys
from io import StringIO

sys.stdout = StringIO()
sys.stderr = StringIO()
`);

    // Execute the user code
    let result;
    try {
      result = await pyodide.runPythonAsync(code);
    } catch (execError: any) {
      // Get stderr output
      const stderr = await pyodide.runPythonAsync('sys.stderr.getvalue()');
      return {
        output: '',
        error: stderr || execError.message || 'Python execution error',
      };
    }

    // Get stdout output
    const stdout = await pyodide.runPythonAsync('sys.stdout.getvalue()');

    if (stdout) {
      capturedOutput.push(stdout);
    }

    // If there's a return value (not None), add it to output
    if (result !== undefined && result !== null) {
      capturedOutput.push(String(result));
    }

    // Reset stdout/stderr for next execution
    await pyodide.runPythonAsync(`
sys.stdout = StringIO()
sys.stderr = StringIO()
`);

    return {
      output: capturedOutput.join('\n') || 'Code executed (no output)',
      error: null,
    };
  } catch (error: any) {
    if (error.message && error.message.includes('loading')) {
      return {
        output: '',
        error: 'Loading Python interpreter... Please try again in a moment.',
      };
    }
    return {
      output: '',
      error: error.message || 'Failed to execute Python code',
    };
  }
}

function executeJavaScript(code: string): { output: string; error: string | null } {
  try {
    const logs: string[] = [];
    const originalLog = console.log;

    console.log = (...args: any[]) => {
      logs.push(args.map((arg) => JSON.stringify(arg)).join(' '));
    };

    const result = eval(code);
    if (result !== undefined) {
      logs.push(String(result));
    }

    console.log = originalLog;

    return {
      output: logs.join('\n') || 'Code executed (no output)',
      error: null,
    };
  } catch (error: any) {
    return {
      output: '',
      error: error.message || 'Unknown error',
    };
  }
}
