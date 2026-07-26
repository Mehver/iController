// BSD 3-Clause License
//
// Copyright (c) 2024 Mehver (https://github.com/Mehver). All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
//    contributors may be used to endorse or promote products derived from
//    this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import React from 'react';
import ReactDOM from 'react-dom/client';
import {ContextProvider} from './utils/Context';
import GeneralDidMount from "./components/GeneralDidMount";
import TopBar from "./components/TopBar";
import Screen from "./components/Screen";
import SideBar from "./components/SideBar";
import {defaultPrimaryColor, defaultSecondaryColor} from './utils/Theme';

const globalStyle = document.createElement("style");
globalStyle.innerHTML = `
html {
    overflow: hidden;
    width: 100%;
    height: 100%;
    background-color: ${defaultPrimaryColor};
}

.full-screen-background {
    background-color: ${defaultPrimaryColor};
    min-height: 100vh;
    min-width: 100vw;
    overflow: hidden;
}

body {
    background-color: ${defaultPrimaryColor};
    overflow: hidden;
    width: 100%;
    height: 100%;
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

.App {
    text-align: center;
}

.App-header {
    background-color: ${defaultSecondaryColor};
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: calc(10px + 2vmin);
    color: ${defaultPrimaryColor};
}

* {
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}
`;
document.head.appendChild(globalStyle);

let resizeTimer: ReturnType<typeof setTimeout>;
const handleResize = () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        window.location.reload();
    }, 500);
};

window.addEventListener('resize', handleResize);

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
    <React.StrictMode>
        <div className="App">
            <header className="App-header">
                <ContextProvider>
                        <GeneralDidMount/>
                        <TopBar/>
                        <Screen/>
                        <SideBar/>
                </ContextProvider>
            </header>
        </div>
    </React.StrictMode>
);
