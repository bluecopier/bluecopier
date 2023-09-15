import * as React from "react";
import { CssBaseline, Container } from "@mui/material";
import { AppToolbar, Toolbar } from "./AppToolbar";
import { ThemeProvider } from "./ThemeProvider";
import Wizard from "./Wizard";

export function App(): JSX.Element {
  return (
    <ThemeProvider>
      <CssBaseline />
      <AppToolbar />
      <Toolbar />

      <Container sx={{ my: 4 }}>
        <Wizard />
      </Container>
    </ThemeProvider>
  );
}
