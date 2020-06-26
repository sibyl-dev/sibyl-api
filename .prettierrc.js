module.exports = {
  semi: true,
  trailingComma: 'all',
  singleQuote: true,
  printWidth: 120,
  tabWidth: 2,
  overrides: [
    {
      files: ['*.scss', '*.css', '*.json'],
      options: {
        tabWidth: 4,
        singleQuote: false,
      },
    },
    {
      files: ['*.html', '*.yml'],
      options: {
        singleQuote: false,
      },
    },
  ],
};
