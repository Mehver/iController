// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

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
import {AppContextType} from '../../types';

interface KeyboardMenuState {
    inputText: string;
    serverIsMac: boolean;
}

class KeyboardMenu extends Component<object, KeyboardMenuState> {
    static contextType = Context;
    declare context: AppContextType;

    constructor(props: object) {
        super(props);
        this.state = {
            inputText: '',
            serverIsMac: true,
        };
    }

    componentDidMount() {
        api_get_system_info()
            .then(data => {
                const isMac = data.os === 'Darwin';
                this.setState({serverIsMac: isMac});
                if (isMac) {
                    this.context.setKeyboardDataSendMod('b');
                }
            });
    }

    handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        this.setState({inputText: event.target.value});
    };

    handleSendText = (event: React.MouseEvent | React.TouchEvent) => {
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
        (event.target as HTMLElement).blur();
    };

    handleSendButton = (signal: string) => {
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
            color: 'secondary' as const,
        };
        const funcButton_iconSX = {color: this.context.secondaryColor};

        return (
            <ThemeProvider theme={customTheme}>
                <List component="div" disablePadding>
                    <ListItem sx={{ display: 'flex', alignItems: 'center' }}>
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
                                    border: 'none',
                                    outline: 'none',
                                    caretColor: this.context.secondaryColor,
                                    color: this.context.secondaryColor,
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
                                '&:focus': {
                                    backgroundColor: this.context.secondaryColor,
                                    color: this.context.primaryColor,
                                },
                            }}
                            onClick={this.handleSendText}
                        >
                            <KeyboardDoubleArrowUpOutlined sx={{color: this.context.primaryColor}}/>
                        </IconButton>
                    </ListItem>
                    <ListItem sx={{ display: 'flex', alignItems: 'center' }}>
                        {this.state.serverIsMac ? (
                            <Typography
                                style={i18n.Sidebar.KeyboardMenu.MacOSOnlyMode.FontSize[this.context.i18n as keyof typeof i18n.Sidebar.KeyboardMenu.MacOSOnlyMode.FontSize] as React.CSSProperties}
                            >
                                {i18n.Sidebar.KeyboardMenu.MacOSOnlyMode[this.context.i18n as 'en' | 'zh']}
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
                                    slotProps={{ input: { 'aria-label': 'a' } }}
                                />
                                <Typography
                                    style={i18n.Sidebar.KeyboardMenu.Paste.FontSize[this.context.i18n as keyof typeof i18n.Sidebar.KeyboardMenu.Paste.FontSize] as React.CSSProperties}
                                >
                                    {i18n.Sidebar.KeyboardMenu.Paste[this.context.i18n as 'en' | 'zh']}
                                </Typography>
                                <Radio
                                    {...radioProps}
                                    checked={this.context.keyboardDataSendMod === 'b'}
                                    onChange={() => {
                                        this.context.setKeyboardDataSendMod('b');
                                    }}
                                    value={this.context.keyboardDataSendMod}
                                    slotProps={{ input: { 'aria-label': 'b' } }}
                                />
                                <Typography
                                    style={i18n.Sidebar.KeyboardMenu.Type.FontSize[this.context.i18n as keyof typeof i18n.Sidebar.KeyboardMenu.Type.FontSize] as React.CSSProperties}
                                >
                                    {i18n.Sidebar.KeyboardMenu.Type[this.context.i18n as 'en' | 'zh']}
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

export default KeyboardMenu;
