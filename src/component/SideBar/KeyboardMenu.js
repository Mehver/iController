import {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    List,
    IconButton,
    ListItem,
    Radio,
    Typography,
    Divider
} from "@mui/material";
import {
    KeyboardDoubleArrowUpOutlined,
    BackspaceOutlined,
    SubdirectoryArrowLeftOutlined
} from '@mui/icons-material';
import {ThemeProvider} from '@mui/material/styles';
import {
    customTheme,
    primaryColor,
    secondaryColor
} from '../../utils/Theme';
import {
    api_keyboard_buttons,
    api_keyboard_typewriting,
    api_keyboard_pastetext
} from "../../api/keyboard";
import {api_get_system_info} from "../../api/system";

class KeyboardMenu extends Component {
    constructor(props) {
        super(props);
        this.state = {
            inputText: '',
            serverIsMac: true,
        };
    }

    componentDidMount() {
        api_get_system_info()
            .then(data => {
                this.setState({serverIsMac: data.volume === 'Darwin'});
            })
            .then(() => {
                if (this.state.serverIsMac) {
                    this.context.setKeyboardDataSendMod('b');
                }
            });
    }

    handleRadioChange = (event) => {
        this.context.setKeyboardDataSendMod(event.target.value);
    };

    // 输入框实时更新
    handleInputChange = (event) => {
        this.setState({inputText: event.target.value});
    };

    // 发送文本消息
    handleSendText = (event) => {
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
        event.target.blur();
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
                            border: '1px solid ' + secondaryColor,
                            borderRadius: '4px',
                            backgroundColor: primaryColor,
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
                                    caretColor: secondaryColor, // 修改光标颜色
                                    color: secondaryColor, // 修改文字颜色
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
                                backgroundColor: secondaryColor,
                                color: primaryColor,
                                '&:hover': {
                                    backgroundColor: secondaryColor,
                                    color: primaryColor,
                                },
                                'focus': {
                                    backgroundColor: secondaryColor,
                                    color: primaryColor,
                                },
                            }}
                            onClick={this.handleSendText}
                        >
                            <KeyboardDoubleArrowUpOutlined sx={{color: primaryColor}}/>
                        </IconButton>
                    </ListItem>
                    <ListItem display="flex" alignItems="center">
                        {this.state.serverIsMac ? (
                            <Typography style={{fontSize: '1rem'}}>*MacOS ASCII Only</Typography>
                        ) : (
                            // <RadioGroup
                            //     row
                            //     value={this.context.keyboardDataSendMod}
                            //     onChange={this.handleRadioChange}
                            // >
                            //     <FormControlLabel
                            //         value="a"
                            //         control={
                            //             <Radio
                            //                 sx={{
                            //                     color: secondaryColor,
                            //                     '&.Mui-checked': {
                            //                         color: secondaryColor,
                            //                     },
                            //                 }}
                            //                 color="secondary"
                            //             />
                            //         }
                            //         label="Paste"
                            //     />
                            //     <FormControlLabel
                            //         value="b"
                            //         control={
                            //             <Radio
                            //                 sx={{
                            //                     color: secondaryColor,
                            //                     '&.Mui-checked': {
                            //                         color: secondaryColor,
                            //                     },
                            //                 }}
                            //                 color="secondary"
                            //             />
                            //         }
                            //         label="Type"
                            //     />
                            // </RadioGroup>
                            <>
                                <Radio
                                    checked={this.context.keyboardDataSendMod === 'a'}
                                    onChange={() => {
                                        this.context.setKeyboardDataSendMod('a');
                                    }}
                                    value={this.context.keyboardDataSendMod}
                                    inputProps={{'aria-label': 'a'}}
                                    sx={{
                                        color: secondaryColor,
                                        '&.Mui-checked': {
                                            color: secondaryColor,
                                        },
                                    }}
                                    color='secondary'
                                />
                                <Typography style={{fontSize: '1rem'}}>Paste</Typography>
                                <Radio
                                    checked={this.context.keyboardDataSendMod === 'b'}
                                    onChange={() => {
                                        this.context.setKeyboardDataSendMod('b');
                                    }}
                                    value={this.context.keyboardDataSendMod}
                                    inputProps={{'aria-label': 'b'}}
                                    sx={{
                                        color: secondaryColor,
                                        '&.Mui-checked': {
                                            color: secondaryColor,
                                        },
                                    }}
                                    color='secondary'
                                />
                                <Typography style={{fontSize: '1rem'}}>Type</Typography>
                            </>
                        )}
                        <div style={{flex: 1}}/>
                        <IconButton
                            onClick={() => this.handleSendButton('Enter')}
                            style={{marginLeft: '10px'}}
                        >
                            <SubdirectoryArrowLeftOutlined sx={{color: secondaryColor}}/>
                        </IconButton>
                        <IconButton
                            onClick={() => this.handleSendButton('Backspace')}
                            style={{marginRight: '10px'}}
                        >
                            <BackspaceOutlined sx={{color: secondaryColor}}/>
                        </IconButton>
                    </ListItem>
                </List>
                <Divider/>
            </ThemeProvider>
        );
    }
}

KeyboardMenu.contextType = Context;

export default KeyboardMenu;
