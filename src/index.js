import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import * as serviceWorker from './serviceWorker';
import {ButtonProvider} from './utils/Context';
import TopBar from "./component/TopBar";
// import TopBarButtons from "./component/TopBarButtons";
import SideBar from "./component/SideBar";
import Touchpad from "./component/Touchpad";
import MouseDPadButtons from "./component/MouseDPadButtons";

// 设置延时函数
let resizeTimer;
const handleResize = () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        // 刷新页面
        window.location.reload();
    }, 500); // 延迟500毫秒
};

// 监听屏幕大小改变或旋转事件
window.addEventListener('resize', handleResize);

ReactDOM.render(
    <React.StrictMode>
        <div className="App">
            <header className="App-header">
                <ButtonProvider>
                    <TopBar/>
                    {/*<TopBarButtons/>*/}
                    <SideBar/>
                    <Touchpad/>
                    <MouseDPadButtons/>
                </ButtonProvider>
            </header>
        </div>
    </React.StrictMode>,
    document.getElementById('root')
);

// PWA设置
serviceWorker.unregister();
