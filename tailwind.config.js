import sharedConfig from 'school-erp-ui-shared/tailwind.shared.js';

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
    './node_modules/school-erp-ui-shared/dist/**/*.{js,mjs,cjs}',
  ],
  theme: {
    extend: {
      ...sharedConfig.theme.extend,
    },
  },
  plugins: [],
};
