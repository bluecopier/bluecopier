import test from "node:test";
import { main } from "./index";

test('should log Hello World', () => {
  const logSpy = jest.spyOn(console, 'log');
  main();
  expect(logSpy).toHaveBeenCalledWith('Hello World!');
})
