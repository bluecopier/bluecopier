/* SPDX-FileCopyrightText: 2021 @koistya */
/* SPDX-License-Identifier: MIT */

import * as React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./components/App";

const root = createRoot(document.getElementById("root") as HTMLElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
