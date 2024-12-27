import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import {ContextProvider} from './utils/Context';
import GeneralDidMount from "./components/GeneralDidMount";
import TopBar from "./components/TopBar";
import Screen from "./components/Screen";
import SideBar from "./components/SideBar";

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
