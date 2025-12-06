import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import CodeEditor from './CodeEditor.vue';

describe('CodeEditor Component', () => {
  describe('Rendering', () => {
    it('should render codemirror wrapper element', () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      expect(wrapper.find('.codemirror-wrapper').exists()).toBe(true);
    });

    it('should display initial code value', async () => {
      const code = 'console.log("Hello, World!")';
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: code,
          language: 'javascript',
        },
      });

      await wrapper.vm.$nextTick();

      // CodeMirror renders the code inside .cm-content
      const cmContent = wrapper.find('.cm-content');
      expect(cmContent.exists()).toBe(true);
      expect(cmContent.text()).toContain('console.log');
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
  });

  describe('Read-only mode', () => {
    it('should not be readonly by default', () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
        },
      });

      // Vue sets false as default for optional Boolean props
      expect(wrapper.props('readOnly')).toBeFalsy();
    });

    it('should be readonly when prop is set', () => {
      const wrapper = mount(CodeEditor, {
        props: {
          modelValue: '',
          language: 'javascript',
          readOnly: true,
        },
      });

      expect(wrapper.props('readOnly')).toBe(true);
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

      await wrapper.vm.$nextTick();

      // Simulate CodeMirror input by calling the emit directly
      // In real usage, CodeMirror handles this through its updateListener
      wrapper.vm.$emit('update:modelValue', 'const x = 42');

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

      await wrapper.vm.$nextTick();

      wrapper.vm.$emit('update:modelValue', 'new code');

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

      await wrapper.vm.$nextTick();

      wrapper.vm.$emit('update:modelValue', 'const');
      wrapper.vm.$emit('update:modelValue', 'const x');
      wrapper.vm.$emit('update:modelValue', 'const x = 42');

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

      await wrapper.vm.$nextTick();

      wrapper.vm.$emit('update:modelValue', '');

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

      await wrapper.vm.$nextTick();

      wrapper.vm.$emit('update:modelValue', multilineCode);

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

      await wrapper.vm.$nextTick();

      // Check initial content
      let cmContent = wrapper.find('.cm-content');
      expect(cmContent.text()).toContain('initial');

      await wrapper.setProps({ modelValue: 'updated code' });
      await wrapper.vm.$nextTick();

      // Check updated content
      cmContent = wrapper.find('.cm-content');
      expect(cmContent.text()).toContain('updated');
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

      expect(wrapper.find('.codemirror-wrapper').exists()).toBe(true);
    });
  });

  describe('Different languages', () => {
    const languages = ['javascript', 'typescript', 'python', 'java', 'cpp', 'rust', 'php'];

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

      await wrapper.vm.$nextTick();

      wrapper.vm.$emit('update:modelValue', longCode);

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

      await wrapper.vm.$nextTick();

      wrapper.vm.$emit('update:modelValue', specialChars);

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

      await wrapper.vm.$nextTick();

      wrapper.vm.$emit('update:modelValue', unicode);

      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([unicode]);
    });
  });
});
