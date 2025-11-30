export const useCodeExecution = () => {
  const executeJavaScript = (code: string): { output: string; error: string | null } => {
    try {
      const logs: string[] = []
      const originalLog = console.log
      const originalError = console.error
      const originalWarn = console.warn

      // Capture console output
      console.log = (...args: any[]) => {
        logs.push(args.map(arg => JSON.stringify(arg)).join(' '))
      }
      console.error = (...args: any[]) => {
        logs.push('ERROR: ' + args.map(arg => JSON.stringify(arg)).join(' '))
      }
      console.warn = (...args: any[]) => {
        logs.push('WARN: ' + args.map(arg => JSON.stringify(arg)).join(' '))
      }

      // Execute code
      const result = eval(code)
      if (result !== undefined) {
        logs.push(String(result))
      }

      // Restore console
      console.log = originalLog
      console.error = originalError
      console.warn = originalWarn

      return {
        output: logs.join('\n') || 'Code executed successfully (no output)',
        error: null,
      }
    } catch (error: any) {
      return {
        output: '',
        error: error.message || 'Unknown error occurred',
      }
    }
  }

  const executePython = async (code: string): Promise<{ output: string; error: string | null }> => {
    try {
      // For now, return a message that Python execution requires Pyodide
      return {
        output: 'Python execution is not yet implemented. Install Pyodide for in-browser Python support.',
        error: null,
      }
    } catch (error: any) {
      return {
        output: '',
        error: error.message || 'Unknown error occurred',
      }
    }
  }

  const executeCode = async (
    code: string,
    language: string
  ): Promise<{ output: string; error: string | null }> => {
    switch (language) {
      case 'javascript':
      case 'typescript':
        return executeJavaScript(code)
      case 'python':
        return await executePython(code)
      default:
        return {
          output: '',
          error: `Execution for ${language} is not supported yet. Only JavaScript and Python are currently supported.`,
        }
    }
  }

  return {
    executeCode,
  }
}
