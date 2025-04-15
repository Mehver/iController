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
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {
    api_keyboard_buttons,
    api_keyboard_typewriting,
    api_keyboard_pastetext
} from "../../api/keyboard";
import {api_get_system_info} from "../../api/system";
import i18n from '../../utils/i18n';

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
                this.setState({serverIsMac: data.os === 'Darwin'});
            })
            .then(() => {
                if (this.state.serverIsMac) {
                    this.context.setKeyboardDataSendMod('b');
                }
            });
    }

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
        let customTheme = createTheme({
            palette: {
                primary: {
                    main: this.context.primaryColor,
                },
                secondary: {
                    main: this.context.secondaryColor,
                },
            },
        });

        const radioSX = {
            color: this.context.secondaryColor,
            '&.Mui-checked': {
                color: this.context.secondaryColor,
            },
        };
        const radioProps = {
            sx: radioSX,
            color: 'secondary',
        };
        const funcButton_iconSX = {color: this.context.secondaryColor};

        return (
            <ThemeProvider theme={customTheme}>
                <List component="div" disablePadding>
                    <ListItem display="flex" alignItems="center">
                        {/* 使用TextField会有文字大小不匹配的bug */}
                        <div style={{
                            margin: '10px',
                            height: '40px',
                            border: '1px solid ' + this.context.secondaryColor,
                            borderRadius: '4px',
                            backgroundColor: this.context.primaryColor,
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
                                    caretColor: this.context.secondaryColor, // 修改光标颜色
                                    color: this.context.secondaryColor, // 修改文字颜色
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
                                backgroundColor: this.context.secondaryColor,
                                color: this.context.primaryColor,
                                '&:hover': {
                                    backgroundColor: this.context.secondaryColor,
                                    color: this.context.primaryColor,
                                },
                                'focus': {
                                    backgroundColor: this.context.secondaryColor,
                                    color: this.context.primaryColor,
                                },
                            }}
                            onClick={this.handleSendText}
                        >
                            <KeyboardDoubleArrowUpOutlined sx={{color: this.context.primaryColor}}/>
                        </IconButton>
                    </ListItem>
                    <ListItem display="flex" alignItems="center">
                        {this.state.serverIsMac ? (
                            // If it's MacOS, then it only supports ASCII
                            <Typography
                                style={i18n.Sidebar.KeyboardMenu.MacOSOnlyMode.FontSize[this.context.i18n]}
                            >
                                {i18n.Sidebar.KeyboardMenu.MacOSOnlyMode[this.context.i18n]}
                            </Typography>
                        ) : (
                            <>
                                <Radio
                                    {...radioProps}
                                    checked={this.context.keyboardDataSendMod === 'a'}
                                    onChange={() => {
                                        this.context.setKeyboardDataSendMod('a');
                                    }}
                                    value={this.context.keyboardDataSendMod}
                                    inputProps={{'aria-label': 'a'}}
                                />
                                <Typography
                                    style={i18n.Sidebar.KeyboardMenu.Paste.FontSize[this.context.i18n]}
                                >
                                    {i18n.Sidebar.KeyboardMenu.Paste[this.context.i18n]}
                                </Typography>
                                <Radio
                                    {...radioProps}
                                    checked={this.context.keyboardDataSendMod === 'b'}
                                    onChange={() => {
                                        this.context.setKeyboardDataSendMod('b');
                                    }}
                                    value={this.context.keyboardDataSendMod}
                                    inputProps={{'aria-label': 'b'}}
                                />
                                <Typography
                                    style={i18n.Sidebar.KeyboardMenu.Type.FontSize[this.context.i18n]}
                                >
                                    {i18n.Sidebar.KeyboardMenu.Type[this.context.i18n]}
                                </Typography>
                            </>
                        )}
                        <div style={{flex: 1}}/>
                        <IconButton
                            onClick={() => this.handleSendButton('Enter')}
                            style={{marginLeft: '10px'}}
                        >
                            <SubdirectoryArrowLeftOutlined sx={funcButton_iconSX}/>
                        </IconButton>
                        <IconButton
                            onClick={() => this.handleSendButton('Backspace')}
                            style={{marginRight: '10px'}}
                        >
                            <BackspaceOutlined sx={funcButton_iconSX}/>
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
