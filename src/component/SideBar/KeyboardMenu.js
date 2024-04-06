import {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    List,
    IconButton,
    ListItem,
    Radio,
    Typography
} from "@mui/material";
import {
    KeyboardDoubleArrowUpOutlined,
    BackspaceOutlined,
    SubdirectoryArrowLeftOutlined
} from '@mui/icons-material';
import {ThemeProvider} from '@mui/material/styles';
import {customTheme} from '../../utils/Theme';
import {
    api_keyboard_buttons,
    api_keyboard_typewriting,
    api_keyboard_pastetext
} from "../../api/keyboard";

class KeyboardMenu extends Component {
    constructor(props) {
        super(props);
        this.state = {
            inputText: '',
        };
    }

    // 输入框实时更新
    handleInputChange = (event) => {
        this.setState({inputText: event.target.value});
    };

    // 发送文本消息
    handleSendText = () => {
        const {inputText} = this.state;
        if (inputText.trim()) {
            if (this.context.keyboardDataSendMod === 'a') {
                api_keyboard_pastetext(inputText);
                console.log('api_keyboard_pastetext: ' + inputText);
            } else if (this.context.keyboardDataSendMod === 'b') {
                api_keyboard_typewriting(inputText);
                console.log('api_keyboard_typewriting: ' + inputText);
            }
            this.setState({inputText: ''});
        }
    };

    // 发送按键消息
    handleSendButton = (signal) => {
        api_keyboard_buttons(signal);
    };

    render() {
        return (
            <ThemeProvider theme={customTheme}>
                <List component="div" disablePadding>
                    <ListItem display="flex" alignItems="center">
                        {/* 使用TextField会有文字大小不匹配的bug */}
                        <div style={{
                            margin: '10px',
                            height: '40px',
                            border: '1px solid #333',
                            borderRadius: '4px',
                            backgroundColor: '#6df',
                            display: 'flex',
                            alignItems: 'center',
                        }}>
                            <input
                                type="text"
                                value={this.state.inputText}
                                onChange={this.handleInputChange}
                                style={{
                                    border: 'none', // 移除input的默认边框
                                    outline: 'none', // 移除聚焦时的轮廓
                                    caretColor: '#333', // 修改光标颜色
                                    color: '#333', // 修改文字颜色
                                    backgroundColor: 'transparent',
                                    width: '100%',
                                    fontSize: '1rem',
                                    lineHeight: 'normal',
                                }}
                            />
                        </div>
                        <IconButton
                            sx={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '8%',
                                backgroundColor: '#333',
                                color: '#6df',
                                '&:hover': {
                                    backgroundColor: '#6df',
                                    color: '#333',
                                },
                            }}
                            onClick={this.handleSendText}
                        >
                            <KeyboardDoubleArrowUpOutlined sx={{color: '#6df'}}/>
                        </IconButton>
                    </ListItem>
                    <ListItem display="flex" alignItems="center">
                        <Radio
                            checked={this.context.keyboardDataSendMod === 'a'}
                            onChange={() => {
                                this.context.setKeyboardDataSendMod('a');
                            }}
                            value={this.context.keyboardDataSendMod}
                            inputProps={{'aria-label': 'a'}}
                        />
                        <Typography style={{fontSize: '1rem'}}>Past</Typography>
                        <Radio
                            checked={this.context.keyboardDataSendMod === 'b'}
                            onChange={() => {
                                this.context.setKeyboardDataSendMod('b');
                            }}
                            value={this.context.keyboardDataSendMod}
                            inputProps={{'aria-label': 'b'}}
                        />
                        <Typography style={{fontSize: '1rem'}}>Type</Typography>
                        <div style={{flex: 1}}/>
                        <IconButton
                            onClick={() => this.handleSendButton('Enter')}
                            style={{marginLeft: '10px'}}
                        >
                            <SubdirectoryArrowLeftOutlined/>
                        </IconButton>
                        <IconButton
                            onClick={() => this.handleSendButton('Backspace')}
                            style={{marginRight: '10px'}}
                        >
                            <BackspaceOutlined/>
                        </IconButton>
                    </ListItem>
                </List>
                {/*<Divider/>*/}
            </ThemeProvider>
        );
    }
}

KeyboardMenu.contextType = Context;

export default KeyboardMenu;
