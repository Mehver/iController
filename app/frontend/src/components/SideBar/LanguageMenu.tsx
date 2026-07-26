// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import React, {Component} from 'react';
import {Context} from '../../utils/Context';
import {ListItem, Typography, TextField} from "@mui/material";
import {createTheme, ThemeProvider} from "@mui/material/styles";
import i18n from '../../utils/i18n';
import {AppContextType} from '../../types';

class LanguageMenu extends Component {
    static contextType = Context;
    declare context: AppContextType;

    handleLanguageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newLang = event.target.value;
        this.context.setI18n(newLang);
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
                        label={i18n.Sidebar.LanguageMenu.Language[this.context.i18n as keyof typeof i18n.Sidebar.LanguageMenu.Language]}
                        variant="outlined"
                        value={this.context.i18n}
                        onChange={this.handleLanguageChange}
                        slotProps={{ select: { native: true } }}
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
                                color: '#000',
                            },
                        }}
                        focused={true}
                    >
                        <option value="en">{i18n.Sidebar.LanguageMenu.EN[this.context.i18n as keyof typeof i18n.Sidebar.LanguageMenu.EN]}</option>
                        <option value="zh">{i18n.Sidebar.LanguageMenu.ZH[this.context.i18n as keyof typeof i18n.Sidebar.LanguageMenu.ZH]}</option>
                    </TextField>
                </ListItem>
            </ThemeProvider>
        );
    }
}

export default LanguageMenu;
