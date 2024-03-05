import React from 'react';
import {EyeOutlined, EyeInvisibleOutlined} from '@ant-design/icons';

class TopBarButtons extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            buttonSW1: true,
            buttonSW2: true,
            buttonSW3: true,
            buttonSW4: false,
        };
    }

    componentDidMount() {
        let pressButtonEffect = (buttonId) => {
            let button = document.getElementById(buttonId);
            button.style.backgroundColor = "#6df";
            setTimeout(function () {
                button.style.backgroundColor = "#333";
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

        document.getElementById("button-sw4").addEventListener("click", () => {
            pressButtonEffect("button-sw4");
            // 切换图标的显示状态
            this.setState(prevState => ({
                buttonSW4: !prevState.buttonSW4,
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
            backgroundColor: '#333',
            border: '2px solid #6df',
            height: '23px',
        };

        const iconCss = {
            fontSize: iconSize,
            color: '#6df',
        };
        const barCss = {
            position: 'absolute',
            top: '3.5px',
            left: '120px',
            height: '23px',
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
                        {this.state.buttonSW2 ? <EyeOutlined style={iconCss}/> :
                            <EyeInvisibleOutlined style={iconCss}/>}
                    </button>
                    <button id="button-sw3" style={buttonCss}>
                        {this.state.buttonSW3 ? <EyeOutlined style={iconCss}/> :
                            <EyeInvisibleOutlined style={iconCss}/>}
                    </button>
                    <button id="button-sw4" style={buttonCss}>
                        {this.state.buttonSW4 ? <EyeOutlined style={iconCss}/> :
                            <EyeInvisibleOutlined style={iconCss}/>}
                    </button>
                </div>
            </>
        );
    }
}

export default TopBarButtons;
