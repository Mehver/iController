import React, {Component} from 'react';

// 节流函数，限制函数调用频率，避免过多的请求
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
        window.addEventListener('resize', this.updateWindowDimensions);
        document.body.style.overflow = 'hidden';
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.updateWindowDimensions);
        document.body.style.overflow = '';
    }

    updateWindowDimensions = () => {
        this.setState({
            screenWidth: window.innerWidth,
            screenHeight: window.innerHeight,
        });
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

        const xPercent = (xRelative / (shorterSide / 2)) * 100;
        const yPercent = (yRelative / (shorterSide / 2)) * 100;

        this.setState({
            xPercent: xPercent.toFixed(2),
            yPercent: yPercent.toFixed(2),
        });

        // 发送坐标至后端
        this.sendCoordinates(xPercent.toFixed(2), yPercent.toFixed(2));
    }


    sendCoordinates(xPercent, yPercent) {
        // 创建一个足够存储两个float32值的缓冲区
        const buffer = new ArrayBuffer(8); // 每个float32占用4字节
        const view = new DataView(buffer);

        // 将x和y值写入缓冲区
        // 第三个参数设置为true表示使用小端序
        view.setFloat32(0, xPercent, true); // 从缓冲区的起始位置写入x
        view.setFloat32(4, yPercent, true); // 从缓冲区的第4字节位置写入y

        // 发送二进制数据
        fetch('/receive_coordinates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/octet-stream',
            },
            body: buffer,
        })
            .then(response => response.json())
            .then(data => console.log('Success:', data))
            .catch((error) => {
                console.error('Error:', error);
            });
    }


    handleTouchEnd = () => {
        this.setState({
            xPercent: 0,
            yPercent: 0,
        });
        // 发送坐标至后端
        this.sendCoordinates(0, 0);
    }

    render() {
        const {screenWidth, screenHeight} = this.state;
        const touchPadStyle = {
            position: 'absolute',
            left: '50%',
            top: '50%',
            width: `${screenWidth * 0.84}px`,
            height: `${screenHeight * 0.84}px`,
            transform: 'translate(-50%, -50%)',
            backgroundColor: 'transparent', // 背景透明
        };

        return (
            <div
                onTouchStart={this.handleTouchStart}
                onTouchMove={this.handleTouchMove}
                onTouchEnd={this.handleTouchEnd}
                style={touchPadStyle}
            >
                Touch coordinates: ({this.state.xPercent}%, {this.state.yPercent}%)
            </div>
        );
    }
}

export default Touchpad;
