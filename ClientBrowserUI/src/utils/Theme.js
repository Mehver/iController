import {createTheme} from "@mui/material/styles";

export let primaryColor = '#6df';
export let primaryColorTrans = 'rgba(102, 204, 255, 0.5)';
export let secondaryColor = '#333';
export let secondaryColorTrans = 'rgba(51, 51, 51, 0.5)';

// 自动检测颜色格式并转换为半透明颜色值
const convertHexToRGBA = (hex, opacity) => {
    let tempHex = hex.replace('#', '');
    // 检测并转换3位十六进制颜色为6位
    if (tempHex.length === 3) {
        tempHex = tempHex.split('').map((hex) => hex + hex).join('');
    } else if (tempHex.length !== 6) {
        // 如果不是3位也不是6位，则返回null
        return null;
    }
    const r = parseInt(tempHex.substring(0, 2), 16);
    const g = parseInt(tempHex.substring(2, 4), 16);
    const b = parseInt(tempHex.substring(4, 6), 16);

    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

// 更新主题
const updateTheme = () => {
    customTheme.palette.primary.main = primaryColor;
    customTheme.palette.secondary.main = secondaryColor;
};

export const setPrimaryColor = (color) => {
    const newColorTrans = convertHexToRGBA(color, 0.5);
    if (newColorTrans) {
        primaryColor = color;
        primaryColorTrans = newColorTrans;
        updateTheme();
        // 修改 head 中的 <meta name="theme-color" content="#66ddff"/>
        const metaThemeColor = document.querySelector("meta[name=theme-color]");
        if (metaThemeColor) {
            metaThemeColor.setAttribute("content", color);
        }
        // 改变CSS中的background-color
        const html = document.querySelector("html");
        const body = document.querySelector("body");
        const fullScreenBackground = document.querySelector(".full-screen-background");
        const appHeader = document.querySelector(".App-header");
        if (html) {
            html.style.backgroundColor = color;
        }
        if (body) {
            body.style.backgroundColor = color;
        }
        if (fullScreenBackground) {
            fullScreenBackground.style.backgroundColor = color;
        }
        if (appHeader) {
            appHeader.style.color = color;
        }
    }
};

export const setSecondaryColor = (color) => {
    const newColorTrans = convertHexToRGBA(color, 0.5);
    if (newColorTrans) {
        secondaryColor = color;
        secondaryColorTrans = newColorTrans;
        updateTheme();
        const appHeader = document.querySelector(".App-header");
        if (appHeader) {
            appHeader.style.backgroundColor = color;
        }
    }
};

export let customTheme = createTheme({
    palette: {
        primary: {
            main: primaryColor,
        },
        secondary: {
            main: secondaryColor,
        },
    },
});
