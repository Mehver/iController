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

import {Component} from 'react';
import {Context} from '../../utils/Context';
import {api_touchpad, api_touchpad_reposition} from '../../api/touchpad';
import {Typography} from "@mui/material";
import i18n from '../../utils/i18n';

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
        // 对 handleTouchMove 进行 throttle 限制
        this.handleTouchMove = throttle(this.handleTouchMove.bind(this), 50);
        this.longPressTimer = null;
        this.doubleTapTimer = null;
    }

    componentDidMount() {
        window.addEventListener('resize', this.updateWindowDimensions);
    }

    updateWindowDimensions = () => {
        this.setState({
            screenWidth: window.innerWidth,
            screenHeight: window.innerHeight
        });
    }

    handleLongPress = () => {
        console.log('Long press detected');
        api_touchpad_reposition();
        alert(i18n.Screen.Touchpad.LongPressDetect[this.context.i18n]);
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
        const touch = e.touches[0];
        const {initialX, initialY, screenWidth, screenHeight} = this.state;
        const shorterSide = screenWidth < screenHeight ? screenWidth : screenHeight;
        const xRelative = touch.clientX - initialX;
        const yRelative = touch.clientY - initialY;
        const xPercent = (xRelative / (shorterSide / 2)) * 100 * this.context.tPadSensitivity;
        const yPercent = (yRelative / (shorterSide / 2)) * 100 * this.context.tPadSensitivity;

        // 计算滑动的整体百分比幅度，采用欧几里得距离
        const movementDistance = Math.sqrt(xPercent * xPercent + yPercent * yPercent);
        // 如果滑动幅度超过5%，则取消长按定时器
        if (movementDistance > 5) {
            clearTimeout(this.longPressTimer);
        }

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
                    <div
                        onTouchStart={this.handleTouchStart}
                        onTouchMove={this.handleTouchMove}
                        onTouchEnd={this.handleTouchEnd}
                        style={touchPadStyle}
                        id={'touchPad'}
                    >
                        <Typography style={{fontSize: '1.1rem'}}>
                            {i18n.Screen.Touchpad.TouchpadCoordinates[this.context.i18n]} (
                            {parseInt(this.state.xPercent)}%, {parseInt(this.state.yPercent)}%)
                        </Typography>
                        <Typography style={{fontSize: '0.6rem'}}>
                            *{i18n.Screen.Touchpad.LongPress[this.context.i18n]}
                        </Typography>
                    </div>
                    : null
                }
            </>
        );
    }
}

Touchpad.contextType = Context;

export default Touchpad;
