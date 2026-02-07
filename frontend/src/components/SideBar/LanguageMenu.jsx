import React, {Component} from 'react';
import {Context} from '../../utils/Context';
import {ListItem, Typography, TextField} from "@mui/material";
import {createTheme, ThemeProvider} from "@mui/material/styles";
import i18n from '../../utils/i18n';

class LanguageMenu extends Component {
    static contextType = Context;

    // 处理语言选择变化，更新 Context 后自动刷新页面
    handleLanguageChange = (event) => {
        const newLang = event.target.value;
        this.context.setI18n(newLang);
        // window.location.reload();
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

        return (
            <ThemeProvider theme={customTheme}>
                <ListItem>
                    <Typography style={{fontSize: '1rem'}}>&nbsp;</Typography>
                    <div style={{flex: 1}}/>
                    <TextField
                        select
                        label={i18n.Sidebar.LanguageMenu.Language[this.context.i18n]}
                        variant="outlined"
                        value={this.context.i18n}
                        onChange={this.handleLanguageChange}
                        SelectProps={{native: true}}
                        size="small"
                        fullWidth={true}
                        color="secondary"
                        sx={{
                            input: {
                                color: this.context.secondaryColor,
                                caretColor: this.context.secondaryColor,
                            },
                            '& select': {
                                color: this.context.secondaryColor,
                            },
                            '& svg': {
                                color: this.context.secondaryColor,
                            },
                            '& option': {
                                // On Chrome, use this color for the dropdown options, while the dropdown selector's background is white
                                // On Safari, the dropdown selector use browser's UI, so this color doesn't matter
                                color: '#000',
                            },
                        }}
                        focused={true}
                    >
                        <option value="en">{i18n.Sidebar.LanguageMenu.EN[this.context.i18n]}</option>
                        <option value="zh">{i18n.Sidebar.LanguageMenu.ZH[this.context.i18n]}</option>
                    </TextField>
                </ListItem>
            </ThemeProvider>
        );
    }
}

export default LanguageMenu;
