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

export let defaultPrimaryColor: string = '#6DF';
export let defaultSecondaryColor: string = '#333';

export const convertHexToRGBA = (hex: string, opacity?: number): string | null => {
    let tempHex = hex.replace('#', '');
    if (tempHex.length === 3) {
        tempHex = tempHex.split('').map((hex) => hex + hex).join('');
    } else if (tempHex.length !== 6) {
        return null;
    }
    const r = parseInt(tempHex.substring(0, 2), 16);
    const g = parseInt(tempHex.substring(2, 4), 16);
    const b = parseInt(tempHex.substring(4, 6), 16);

    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

export const updateColorCSS = (primaryColor: string, secondaryColor: string): void => {
    const metaThemeColor = document.querySelector("meta[name=theme-color]");
    if (metaThemeColor) {
        metaThemeColor.setAttribute("content", primaryColor);
    }
    const html = document.querySelector("html");
    const body = document.querySelector("body");
    const fullScreenBackground = document.querySelector(".full-screen-background");
    const appHeader = document.querySelector(".App-header");
    if (html) {
        html.style.backgroundColor = primaryColor;
    }
    if (body) {
        body.style.backgroundColor = primaryColor;
    }
    if (fullScreenBackground) {
        (fullScreenBackground as HTMLElement).style.backgroundColor = primaryColor;
    }
    if (appHeader) {
        (appHeader as HTMLElement).style.color = primaryColor;
        (appHeader as HTMLElement).style.backgroundColor = secondaryColor;
    }
}
