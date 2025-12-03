export async function executeCode(code: string, language: string): Promise<{ output: string; error: string | null }> {
  if (language === 'javascript' || language === 'typescript') {
    return executeJavaScript(code)
  }

  if (language === 'python') {
    return {
      output: 'Python execution is not yet implemented.',
      error: null,
    }
  }

  return {
    output: '',
    error: `Execution for ${language} is not supported yet.`,
  }
}

function executeJavaScript(code: string): { output: string; error: string | null } {
  try {
    const logs: string[] = []
    const originalLog = console.log

    console.log = (...args: any[]) => {
      logs.push(args.map(arg => JSON.stringify(arg)).join(' '))
    }

    const result = eval(code)
    if (result !== undefined) {
      logs.push(String(result))
    }

    console.log = originalLog

    return {
      output: logs.join('\n') || 'Code executed (no output)',
      error: null,
    }
  } catch (error: any) {
    return {
      output: '',
      error: error.message || 'Unknown error',
    }
  }
}
