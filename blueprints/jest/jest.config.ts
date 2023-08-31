import type {Config} from 'jest';

let reporters: Config['reporters'] = ['default', 'summary'];
if (process.env.GITHUB_ACTIONS) {
  reporters = [["github-actions", { silent: false }], 'summary'];
}
const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  reporters
};
export default config;
