import {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    api_touchpad,
    api_touchpad_reposition
} from '../../api/touchpad';
import {Typography} from "@mui/material";

function throttle(func, limit) {
    let inThrottle;
    return function () {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

class Touchpad extends Component {
    constructor(props) {
        super(props);
        this.state = {
            xPercent: 0,
            yPercent: 0,
            initialX: 0,
            initialY: 0,
            screenWidth: window.innerWidth,
            screenHeight: window.innerHeight,
            touchStartTime: 0,
            lastTouchTime: 0,
            touchCount: 0,
        };
        this.handleTouchMove = throttle(this.handleTouchMove.bind(this), 1000 * 0.05);
        this.longPressTimer = null;
        this.doubleTapTimer = null;
    }

    componentDidMount() {
        // 获取窗口尺寸
        // noinspection JSUnresolvedFunction
        window.addEventListener('resize', this.updateWindowDimensions);
        // // 禁用页面滚动
        // // 移动到 GeneralDidMount.js 实现
        // document.body.style.overflow = 'hidden';
        // document.documentElement.style.overflow = 'hidden';
    }

    handleLongPress = () => {
        // console.log('Long press detected');
        api_touchpad_reposition();
    }

    handleDoubleClick = () => {
        // console.log('Double click detected');
    }

    handleTripleClick = () => {
        // console.log('Triple click detected');
    }

    handleTouchStart = (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        const now = Date.now();
        const timeSinceLastTouch = now - this.state.lastTouchTime;

        if (timeSinceLastTouch < 1000 && this.state.touchCount) {
            this.setState(prevState => ({touchCount: prevState.touchCount + 1}));
        } else {
            this.setState({touchCount: 1});
        }

        if (this.state.touchCount === 1) {
            this.longPressTimer = setTimeout(this.handleLongPress, 1000);
        } else if (this.state.touchCount === 2) {
            clearTimeout(this.longPressTimer);
            this.doubleTapTimer = setTimeout(this.handleDoubleClick, 300);
        } else if (this.state.touchCount === 3) {
            clearTimeout(this.doubleTapTimer);
            this.handleTripleClick();
            this.setState({touchCount: 0});
        }

        this.setState({
            initialX: touch.clientX,
            initialY: touch.clientY,
            lastTouchTime: now,
        });
    }

    handleTouchMove = (e) => {
        e.preventDefault();
        clearTimeout(this.longPressTimer);

        const touch = e.touches[0];
        const {initialX, initialY, screenWidth, screenHeight} = this.state;
        const shorterSide = screenWidth < screenHeight ? screenWidth : screenHeight;
        const xRelative = touch.clientX - initialX;
        const yRelative = touch.clientY - initialY;
        const xPercent = (xRelative / (shorterSide / 2)) * 100 * this.context.tPadSensitivity;
        const yPercent = (yRelative / (shorterSide / 2)) * 100 * this.context.tPadSensitivity;

        this.setState({
            xPercent: xPercent.toFixed(2),
            yPercent: yPercent.toFixed(2),
        });

        api_touchpad(xPercent.toFixed(2), yPercent.toFixed(2));
    }

    handleTouchEnd = () => {
        this.setState({
            xPercent: 0,
            yPercent: 0,
        });
        api_touchpad(0, 0);
        clearTimeout(this.longPressTimer);
    }

    render() {
        const {screenWidth, screenHeight} = this.state;
        let touchPadStyle = {
            position: 'fixed',
            width: '100%',
            height: '100%',
            top: '60px',
            backgroundColor: 'transparent',
        };
        if (screenWidth < 280) {
            touchPadStyle.fontSize = `${(screenWidth / 280.0) * 10.0}px`;
        }
        if (screenHeight < 400) {
            touchPadStyle.top = `${400.0 / screenHeight * (61.0 - 380.0 / screenHeight * 12.0)}%`;
        }
        return (
            <>
                {this.context.buttonSW1 ?
                    <>
                        <div
                            onTouchStart={this.handleTouchStart}
                            onTouchMove={this.handleTouchMove}
                            onTouchEnd={this.handleTouchEnd}
                            style={touchPadStyle}
                            id={'touchPad'}
                        >
                            <Typography style={{fontSize: '1.1rem'}}>
                                Touchpad Coordinates ({parseInt(this.state.xPercent)}%, {parseInt(this.state.yPercent)}%)
                            </Typography>
                            <Typography style={{fontSize: '0.6rem'}}>
                                *Long press to reposition cursor to the center
                            </Typography>
                        </div>
                    </> : null
                }
            </>
        );
    }
}

Touchpad.contextType = Context;

export default Touchpad;
