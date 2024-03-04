import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import * as serviceWorker from './serviceWorker';
import ToolBar from "./component/TopBar";
import Touchpad from "./component/Touchpad";
import TopBarButtons from "./component/TopBarButtons";
import MouseButton from "./component/MouseButton";

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
            <ToolBar/>
            <TopBarButtons/>
            <Touchpad/>
            <MouseButton/>
        </header>
    </div>
  </React.StrictMode>,
  document.getElementById('root')
);

// PWA设置
serviceWorker.unregister();
