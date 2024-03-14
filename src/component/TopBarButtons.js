import {Component} from 'react';
import {EyeOutlined, EyeFilled, EyeInvisibleOutlined} from '@ant-design/icons';
import GamepadIcon from '@mui/icons-material/Gamepad';
import MouseIcon from '@mui/icons-material/Mouse';
import TouchAppIcon from '@mui/icons-material/TouchApp';

class TopBarButtons extends Component {
    constructor(props) {
        super(props);
        this.state = {
            buttonSW1: true,
            button23: 0,
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

        document.getElementById("button-23").addEventListener("click", () => {
            pressButtonEffect("button-23");
            // 切换 0 1 2 三档状态
            this.setState(prevState => ({
                button23: (prevState.button23 + 1) % 3,
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
        const buttonCss = {
            float: 'left',
            cursor: 'pointer',
            left: 10,
            width: 30,
            backgroundColor: '#333',
            border: '2px solid #6df',
            height: '23px',
        };
        ////////////////////////////////////////////////
        const iconCss = {
            fontSize: 16,
            color: '#6df',
            position: 'relative',
        };
        // 在Safari浏览器上向左偏移
        const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
        if (isSafari) {
            iconCss.left = '-5px';
        }
        ////////////////////////////////////////////////
        const barCss = {
            position: 'absolute',
            top: '3.5px',
            left: '120px',
            height: '23px',
            backgroundColor: 'transparent',
            overflow: 'hidden',
        };
        ////////////////////////////////////////////////
        // let buttonId;
        // if (this.state.buttonSW2 || (this.state.buttonSW3 && this.state.buttonSW4 === false)) {
        //     buttonId = "button-sw2";
        // } else {
        //     buttonId = "button-sw3";
        // }
        return (
            <>
                <div id="buttonBar" style={barCss}>
                    <button style={{...buttonCss, backgroundColor: '#6df'}}>
                        <TouchAppIcon style={{...iconCss, color: '#333'}}/>
                    </button>
                    <button id="button-sw1" style={buttonCss}>
                        {this.state.buttonSW1 ? <EyeOutlined style={iconCss}/> :
                            <EyeInvisibleOutlined style={iconCss}/>}
                    </button>
                    <button style={{...buttonCss, backgroundColor: '#6df'}}>
                        <MouseIcon style={{...iconCss, color: '#333'}}/>
                    </button>
                    <button id="button-23" style={buttonCss}>
                        {this.state.button23 === 0 ? <EyeOutlined style={iconCss}/> :
                            this.state.button23 === 1 ? <EyeFilled style={iconCss}/> :
                                <EyeInvisibleOutlined style={iconCss}/>}
                    </button>
                    <button style={{...buttonCss, backgroundColor: '#6df'}}>
                        <GamepadIcon style={{...iconCss, color: '#333'}}/>
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
