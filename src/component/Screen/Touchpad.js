import {Component} from 'react';
import {Context} from '../../utils/Context';
import {primaryColor} from '../../utils/Theme';
import {api_touchpad} from '../../api/touchpad';

function throttle(func, limit) {
    let inThrottle;
    // 节流函数，用于减少函数的调用频率
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
            xPercent: 0, // 相对于触摸开始位置的X坐标百分比
            yPercent: 0, // 相对于触摸开始位置的Y坐标百分比
            initialX: 0, // 触摸开始的X坐标
            initialY: 0, // 触摸开始的Y坐标
            screenWidth: window.innerWidth,
            screenHeight: window.innerHeight,
        };
        // 使用throttle包装handleTouchMove方法
        this.handleTouchMove = throttle(this.handleTouchMove.bind(this), 1000 * 0.05); // refreshRate以秒为单位
    }

    componentDidMount() {
        // 获取窗口尺寸
        // noinspection JSUnresolvedFunction
        window.addEventListener('resize', this.updateWindowDimensions);
        // 禁用页面滚动
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
    }

    handleTouchStart = (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        this.setState({
            initialX: touch.clientX,
            initialY: touch.clientY,
        });
    }

    handleTouchMove = (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        const {initialX, initialY, screenWidth, screenHeight} = this.state;
        const shorterSide = screenWidth < screenHeight ? screenWidth : screenHeight;

        // 计算相对于初始触摸位置的坐标
        const xRelative = touch.clientX - initialX;
        const yRelative = touch.clientY - initialY;

        const xPercent = (xRelative / (shorterSide / 2)) * 100 * this.context.tPadSensitivity;
        const yPercent = (yRelative / (shorterSide / 2)) * 100 * this.context.tPadSensitivity;

        this.setState({
            xPercent: xPercent.toFixed(2),
            yPercent: yPercent.toFixed(2),
        });

        // 发送坐标至后端
        api_touchpad(xPercent.toFixed(2), yPercent.toFixed(2));
    }

    handleTouchEnd = () => {
        this.setState({
            xPercent: 0,
            yPercent: 0,
        });
        // 发送坐标至后端
        api_touchpad(0, 0);
    }

    render() {
        const {screenWidth, screenHeight} = this.state;
        let touchPadStyle = {
            position: 'absolute',
            left: '50%',
            top: '50%',
            width: `${screenWidth * 0.84}px`,
            height: `${screenHeight * 0.84}px`,
            transform: 'translate(-50%, -50%)',
            backgroundColor: 'transparent',
            color: primaryColor,
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
                    <div
                        onTouchStart={this.handleTouchStart}
                        onTouchMove={this.handleTouchMove}
                        onTouchEnd={this.handleTouchEnd}
                        style={touchPadStyle}
                        id={'touchPad'}
                    >
                        Touchpad Acting ({this.state.xPercent}%, {this.state.yPercent}%)
                    </div> : null
                }
            </>
        );
    }
}

Touchpad.contextType = Context;

export default Touchpad;
