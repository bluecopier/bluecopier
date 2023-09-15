/* SPDX-FileCopyrightText: 2021 @koistya */
/* SPDX-License-Identifier: MIT */

import * as React from "react";
import { ThemeProvider as MuiThemeProvider } from "@mui/material";
import * as themes from "../theme";
import { ToggleThemeContext } from "../theme";

type ThemeProviderProps = { children: React.ReactNode };

function ThemeProvider(props: ThemeProviderProps): JSX.Element {
  const [theme, setTheme] = React.useState(themes.light);

  const toggleTheme = React.useCallback(() => {
    setTheme((theme) =>
      theme.palette.mode === "light" ? themes.dark : themes.light
    );
  }, []);

  return (
    <MuiThemeProvider theme={theme}>
      <ToggleThemeContext.Provider value={toggleTheme}>
        {props.children}
      </ToggleThemeContext.Provider>
    </MuiThemeProvider>
  );
}

export { ThemeProvider };
