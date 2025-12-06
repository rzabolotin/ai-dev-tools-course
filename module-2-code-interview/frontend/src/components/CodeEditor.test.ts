import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import CodeEditor from './CodeEditor.vue';

describe('CodeEditor Component', () => {
  describe('Rendering', () => {
    it('should render textarea element', () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      expect(wrapper.find('textarea').exists()).toBe(true);
      expect(wrapper.find('.code-editor').exists()).toBe(true);
    });

    it('should display initial code value', () => {
      const code = 'console.log("Hello, World!")';
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: code,
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      expect(textarea.element.value).toBe(code);
    });

    it('should accept language prop', () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'python',
        },
      });

      expect(wrapper.props('language')).toBe('python');
    });

    it('should have spellcheck disabled', () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      expect(textarea.attributes('spellcheck')).toBe('false');
    });
  });

  describe('Read-only mode', () => {
    it('should not be readonly by default', () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      expect(textarea.attributes('readonly')).toBeUndefined();
    });

    it('should be readonly when prop is set', () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
          readOnly: true,
        },
      });

      const textarea = wrapper.find('textarea');
      expect(textarea.attributes('readonly')).toBeDefined();
    });
  });

  describe('Input handling', () => {
    it('should emit update:modelValue on input', async () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      await textarea.setValue('const x = 42');

      expect(wrapper.emitted('update:modelValue')).toBeTruthy();
      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['const x = 42']);
    });

    it('should emit update:modelValue with new value when code changes', async () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: 'old code',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      await textarea.setValue('new code');

      expect(wrapper.emitted('update:modelValue')).toBeTruthy();
      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['new code']);
    });

    it('should emit multiple updates as user types', async () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');

      await textarea.setValue('const');
      await textarea.setValue('const x');
      await textarea.setValue('const x = 42');

      expect(wrapper.emitted('update:modelValue')).toHaveLength(3);
      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['const']);
      expect(wrapper.emitted('update:modelValue')?.[1]).toEqual(['const x']);
      expect(wrapper.emitted('update:modelValue')?.[2]).toEqual(['const x = 42']);
    });

    it('should handle empty string input', async () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: 'some code',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      await textarea.setValue('');

      expect(wrapper.emitted('update:modelValue')).toBeTruthy();
      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['']);
    });

    it('should handle multiline code', async () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      const multilineCode = `function hello() {
  console.log("Hello")
  return true
}`;

      const textarea = wrapper.find('textarea');
      await textarea.setValue(multilineCode);

      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([multilineCode]);
    });
  });

  describe('Props reactivity', () => {
    it('should update displayed code when modelValue prop changes', async () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: 'initial code',
          language: 'javascript',
        },
      });

      let textarea = wrapper.find('textarea');
      expect(textarea.element.value).toBe('initial code');

      await wrapper.setProps({ modelValue: 'updated code' });

      textarea = wrapper.find('textarea');
      expect(textarea.element.value).toBe('updated code');
    });

    it('should accept language prop changes', async () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      expect(wrapper.props('language')).toBe('javascript');

      await wrapper.setProps({ language: 'python' });

      expect(wrapper.props('language')).toBe('python');
    });
  });

  describe('Styling', () => {
    it('should have correct CSS classes', () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      expect(textarea.classes()).toContain('code-editor');
    });
  });

  describe('Different languages', () => {
    const languages = ['javascript', 'typescript', 'python', 'java', 'cpp', 'go', 'rust', 'php'];

    languages.forEach((language) => {
      it(`should accept ${language} as language`, () => {
        const wrapper = mount(CodeEditor, {
          props: {
            modelValue: '',
            language,
          },
        });

        expect(wrapper.props('language')).toBe(language);
      });
    });
  });

  describe('Edge cases', () => {
    it('should handle very long code', async () => {
      const longCode = 'x'.repeat(10000);
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      await textarea.setValue(longCode);

      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([longCode]);
    });

    it('should handle special characters', async () => {
      const specialChars = '!@#$%^&*()_+-=[]{}|;:\'",.<>?/~`';
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      await textarea.setValue(specialChars);

      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([specialChars]);
    });

    it('should handle unicode characters', async () => {
      const unicode = '你好世界 こんにちは мир 🚀';
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      const textarea = wrapper.find('textarea');
      await textarea.setValue(unicode);

      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([unicode]);
    });
  });
});
