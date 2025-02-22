export let defaultPrimaryColor = '#6DF';
export let defaultSecondaryColor = '#333';

// 自动检测颜色格式并转换为半透明颜色值
export const convertHexToRGBA = (hex, opacity) => {
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

export const updateColorCSS = (primaryColor, secondaryColor) => {
    // 修改 head 中的 <meta name="theme-color" content="primaryColor"/>
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
        fullScreenBackground.style.backgroundColor = primaryColor;
    }
    if (appHeader) {
        appHeader.style.color = primaryColor;
        appHeader.style.backgroundColor = secondaryColor;
    }
}

