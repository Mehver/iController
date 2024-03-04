import React from 'react';
import {EyeOutlined, EyeInvisibleOutlined} from '@ant-design/icons';

class TopBarButtons extends React.Component {
    constructor(props) {
        super(props);
        // 初始化状态，buttonSW1为true时显示EyeOutlined图标，为false时显示EyeInvisibleOutlined图标
        this.state = {
            buttonSW1: true,
        };
    }

    componentDidMount() {
        let pressButtonEffect = (buttonId) => {
            let button = document.getElementById(buttonId);
            button.style.backgroundColor = "#fff";
            setTimeout(function () {
                button.style.backgroundColor = "#6df";
            }, 100);
        };

        document.getElementById("button-sw1").addEventListener("click", () => {
            pressButtonEffect("button-sw1");
            // 切换图标的显示状态
            this.setState(prevState => ({
                buttonSW1: !prevState.buttonSW1,
            }));
        });

        document.getElementById("button-sw2").addEventListener("click", () => {
            pressButtonEffect("button-sw2");
            // 切换图标的显示状态
            this.setState(prevState => ({
                buttonSW2: !prevState.buttonSW2,
            }));
        });

        document.getElementById("button-sw3").addEventListener("click", () => {
            pressButtonEffect("button-sw3");
            // 切换图标的显示状态
            this.setState(prevState => ({
                buttonSW3: !prevState.buttonSW3,
            }));
        });
    }

    render() {
        let width_button = 33;
        let iconSize = 16;
        if (window.innerWidth < 420) {
            width_button = (window.innerWidth - 200) / 7;
            iconSize = window.innerWidth / 34;
        }
        const buttonCss = {
            float: 'left',
            cursor: 'pointer',
            left: 10,
            width: width_button,
            backgroundColor: '#6df',
            border: '2px solid #fff',
            height: '22px',
        };

        const iconCss = {
            fontSize: iconSize,
            color: '#fff',
        };
        const barCss = {
            position: 'absolute',
            top: '3.4px',
            left: '120px',
            height: '22px',
            backgroundColor: 'transparent',
            overflow: 'hidden',
        };

        return (
            <>
                <div id="buttonBar" style={barCss}>
                    <button id="button-sw1" style={buttonCss}>
                        {this.state.buttonSW1 ? <EyeOutlined style={iconCss}/> :
                            <EyeInvisibleOutlined style={iconCss}/>}
                    </button>
                    <button id="button-sw2" style={buttonCss}>
                        {this.state.buttonSW2 ? <EyeInvisibleOutlined style={iconCss}/> :
                            <EyeOutlined style={iconCss}/>}
                    </button>
                    <button id="button-sw3" style={buttonCss}>
                        {this.state.buttonSW3 ? <EyeInvisibleOutlined style={iconCss}/> :
                            <EyeOutlined style={iconCss}/>}
                    </button>
                </div>
            </>
        );
    }
}

export default TopBarButtons;
