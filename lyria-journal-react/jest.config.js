const nextJest = require('next/jest');
const createJestConfig = nextJest({
  dir: './',
});
const customJestConfig = {
  testEnvironment: 'node',
  transformIgnorePatterns: ['node_modules/(?!(uuid)/)'],
};
module.exports = createJestConfig(customJestConfig);