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
    /*缺少下面这些会导致 iOS Safari 的屏幕键盘改变可是视窗尺寸*/
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

/* 关闭文本选择，避免触屏操作时长按触发文本复制 */
* {
    -webkit-user-select: none; /* Safari */
    -moz-user-select: none; /* Firefox */
    -ms-user-select: none; /* IE 10+ 和 Edge */
    user-select: none; /* 标准语法 */
}
`;
document.head.appendChild(globalStyle);

// 设置延时函数
let resizeTimer;
const handleResize = () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        // 刷新页面
        window.location.reload();
    }, 500); // 延迟500毫秒，避免线性调整尺寸时频繁刷新
};

// 监听屏幕大小改变或旋转事件
window.addEventListener('resize', handleResize);

const root = ReactDOM.createRoot(document.getElementById('root'));
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
    </React.StrictMode>,
    document.getElementById('root')
);
