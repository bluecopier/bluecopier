export const main = () => {
  console.log("Hello World!");
}

if (require.main === module) {
  try {
    main();
  } finally {
    process.exit();
  }
}
