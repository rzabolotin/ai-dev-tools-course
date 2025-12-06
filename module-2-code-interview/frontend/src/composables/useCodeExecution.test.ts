import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { executeCode } from './useCodeExecution';

describe('useCodeExecution', () => {
  let originalConsoleLog: typeof console.log;

  beforeEach(() => {
    originalConsoleLog = console.log;
  });

  afterEach(() => {
    console.log = originalConsoleLog;
  });

  describe('JavaScript execution', () => {
    it('should execute simple JavaScript code', async () => {
      const result = await executeCode('1 + 1', 'javascript');

      expect(result.error).toBeNull();
      expect(result.output).toBe('2');
    });

    it('should capture console.log output', async () => {
      const code = 'console.log("Hello, World!")';
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBeNull();
      expect(result.output).toBe('"Hello, World!"');
    });

    it('should capture multiple console.log calls', async () => {
      const code = `
        console.log("First")
        console.log("Second")
        console.log("Third")
      `;
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBeNull();
      expect(result.output).toContain('"First"');
      expect(result.output).toContain('"Second"');
      expect(result.output).toContain('"Third"');
    });

    it('should handle code with return value and logs', async () => {
      const code = `
        console.log("Before")
        const result = 5 + 3
        console.log("After")
        result
      `;
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBeNull();
      expect(result.output).toContain('"Before"');
      expect(result.output).toContain('"After"');
      expect(result.output).toContain('8');
    });

    it('should show message when code has no output', async () => {
      const code = 'const x = 5';
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBeNull();
      expect(result.output).toBe('Code executed (no output)');
    });

    it('should handle errors in JavaScript code', async () => {
      const code = 'throw new Error("Test error")';
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBe('Test error');
      expect(result.output).toBe('');
    });

    it('should handle syntax errors', async () => {
      const code = 'const x = {';
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBeTruthy();
      expect(result.output).toBe('');
    });

    it('should handle undefined references', async () => {
      const code = 'undefinedVariable.toString()';
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBeTruthy();
      expect(result.output).toBe('');
    });

    it('should restore console.log after execution', async () => {
      const mockLog = vi.fn();
      console.log = mockLog;

      await executeCode('console.log("test")', 'javascript');

      // After execution, console.log should be restored
      expect(console.log).toBe(mockLog);
    });
  });

  describe('TypeScript execution', () => {
    it('should execute TypeScript code without type annotations', async () => {
      // TypeScript with type annotations will fail in eval
      // Only plain JavaScript syntax works
      const result = await executeCode('const x = 42; x', 'typescript');

      expect(result.error).toBeNull();
      expect(result.output).toBe('42');
    });

    it('should capture console.log in TypeScript (without type annotations)', async () => {
      const code = 'const msg = "Hello"; console.log(msg)';
      const result = await executeCode(code, 'typescript');

      expect(result.error).toBeNull();
      expect(result.output).toBe('"Hello"');
    });

    it('should fail when executing TypeScript with type annotations', async () => {
      const code = 'const x: number = 42; x';
      const result = await executeCode(code, 'typescript');

      expect(result.error).toBeTruthy();
      expect(result.output).toBe('');
    });
  });

  describe('Python execution', () => {
    it('should return not implemented message for Python', async () => {
      const result = await executeCode('print("Hello")', 'python');

      expect(result.error).toBeNull();
      expect(result.output).toBe('Python execution is not yet implemented.');
    });
  });

  describe('Unsupported languages', () => {
    it('should return error for Java', async () => {
      const result = await executeCode('System.out.println("Hello");', 'java');

      expect(result.error).toBe('Execution for java is not supported yet.');
      expect(result.output).toBe('');
    });

    it('should return error for C++', async () => {
      const result = await executeCode('cout << "Hello";', 'cpp');

      expect(result.error).toBe('Execution for cpp is not supported yet.');
      expect(result.output).toBe('');
    });

    it('should return error for Go', async () => {
      const result = await executeCode('fmt.Println("Hello")', 'go');

      expect(result.error).toBe('Execution for go is not supported yet.');
      expect(result.output).toBe('');
    });

    it('should return error for Rust', async () => {
      const result = await executeCode('println!("Hello");', 'rust');

      expect(result.error).toBe('Execution for rust is not supported yet.');
      expect(result.output).toBe('');
    });

    it('should return error for PHP', async () => {
      const result = await executeCode('echo "Hello";', 'php');

      expect(result.error).toBe('Execution for php is not supported yet.');
      expect(result.output).toBe('');
    });
  });

  describe('Complex JavaScript scenarios', () => {
    it('should handle objects and arrays', async () => {
      const code = `
        const obj = { name: "John", age: 30 }
        const arr = [1, 2, 3]
        console.log(obj)
        console.log(arr)
      `;
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBeNull();
      expect(result.output).toContain('"name"');
      expect(result.output).toContain('"John"');
    });

    it('should handle functions', async () => {
      const code = `
        function add(a, b) {
          return a + b
        }
        const sum = add(5, 3)
        console.log(sum)
      `;
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBeNull();
      expect(result.output).toContain('8');
    });

    it('should handle async operations (but they complete synchronously in eval)', async () => {
      const code = `
        const result = Promise.resolve(42)
        result
      `;
      const result = await executeCode(code, 'javascript');

      expect(result.error).toBeNull();
      // Will show Promise object, not resolved value
      expect(result.output).toBeTruthy();
    });
  });
});
