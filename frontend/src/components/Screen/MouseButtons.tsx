// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import {Component} from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {convertHexToRGBA} from '../../utils/Theme';
import {Context} from '../../utils/Context';
import {api_mousebutton} from '../../api/mousebutton';
import {Typography} from "@mui/material";
import {AppContextType} from '../../types';

class MouseButtons extends Component {
    static contextType = Context;
    declare context: AppContextType;

    render() {
        const mouseLMRBoxSX = {
            display: 'flex',
            justifyContent: 'space-between',
            p: 1,
            marginBottom: '50px',
            bottom: 0,
            position: 'fixed',
            width: window.innerWidth < 500 ? '100%' : '500px',
            backgroundColor: 'transparent',
        };
        const buttonSX = {
            width: '100%',
            borderWidth: '5px !important',
            borderColor: convertHexToRGBA(this.context.primaryColor) + ' !important',
        };

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
                <Box sx={mouseLMRBoxSX}>
                    {this.context.button23 !== 2 ? (
                        <>
                            <Typography style={{fontSize: '1rem'}}>&nbsp;&nbsp;&nbsp;&nbsp;</Typography>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={(event) => {
                                    api_mousebutton('Left');
                                    event.currentTarget.blur();
                                }}
                                sx={buttonSX}
                            >L</Button>
                            {this.context.button23 === 0 ? (
                                <>
                                    <Typography style={{fontSize: '1rem'}}>&nbsp;&nbsp;</Typography>
                                    <Button
                                        color="primary"
                                        variant="outlined"
                                        onClick={(event) => {
                                            api_mousebutton('Middle');
                                            event.currentTarget.blur();
                                        }}
                                        sx={buttonSX}
                                    >M</Button>
                                    <Typography style={{fontSize: '1rem'}}>&nbsp;&nbsp;</Typography>
                                </>
                            ) : <Typography style={{fontSize: '1rem'}}>&nbsp;&nbsp;</Typography>}
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={(event) => {
                                    api_mousebutton('Right');
                                    event.currentTarget.blur();
                                }}
                                sx={buttonSX}
                            >R</Button>
                            <Typography style={{fontSize: '1rem'}}>&nbsp;&nbsp;&nbsp;&nbsp;</Typography>
                        </>
                    ) : null}
                </Box>
            </ThemeProvider>
        );
    }

}

export default MouseButtons;
