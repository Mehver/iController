import {Component} from 'react';
import {EyeOutlined, EyeFilled, EyeInvisibleOutlined} from '@ant-design/icons';
import GamepadIcon from '@mui/icons-material/Gamepad';
import MouseIcon from '@mui/icons-material/Mouse';
import TouchAppIcon from '@mui/icons-material/TouchApp';
import {Context} from '../utils/Context';

class TopBarButtons extends Component {
    constructor(props) {
        super(props);
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
            this.context.toggleButtonSW1();
        });

        document.getElementById("button-23").addEventListener("click", () => {
            pressButtonEffect("button-23");
            this.context.setButton23((this.context.button23 + 1) % 3);
        });
        document.getElementById("button-sw4").addEventListener("click", () => {
            pressButtonEffect("button-sw4");
            this.context.toggleButtonSW4();
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
        return (
            <>
                <div id="buttonBar" style={barCss}>
                    <button style={{...buttonCss, backgroundColor: '#6df'}}>
                        <TouchAppIcon style={{...iconCss, color: '#333'}}/>
                    </button>
                    <button id="button-sw1" style={buttonCss}>
                        {this.context.buttonSW1 ? <EyeOutlined style={iconCss}/> :
                            <EyeInvisibleOutlined style={iconCss}/>}
                    </button>
                    <button style={{...buttonCss, backgroundColor: '#6df'}}>
                        <MouseIcon style={{...iconCss, color: '#333'}}/>
                    </button>
                    <button id="button-23" style={buttonCss}>
                        {this.context.button23 === 0 ? <EyeOutlined style={iconCss}/> :
                            this.context.button23 === 1 ? <EyeFilled style={iconCss}/> :
                                <EyeInvisibleOutlined style={iconCss}/>}
                    </button>
                    <button style={{...buttonCss, backgroundColor: '#6df'}}>
                        <GamepadIcon style={{...iconCss, color: '#333'}}/>
                    </button>
                    <button id="button-sw4" style={buttonCss}>
                        {this.context.buttonSW4 ? <EyeOutlined style={iconCss}/> :
                            <EyeInvisibleOutlined style={iconCss}/>}
                    </button>
                </div>
            </>
        );
    }
}

TopBarButtons.contextType = Context;

export default TopBarButtons;
