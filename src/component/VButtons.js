import {Component} from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import {Collapse} from "@mui/material";
import {ThemeProvider} from '@mui/material/styles';
import {customTheme} from '../utils/Theme';
import {Context} from '../utils/Context';
import {api_button} from '../api/button';

class VButtons extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        let dPadButtonWidth = window.innerWidth / 4;
        let dPadButtonHeight = window.innerHeight / 5;
        const mouseLMRBoxSX = {
            display: 'flex',
            justifyContent: 'space-between', // 使按钮间有等距间隙
            p: 1, // 设置内边距
            marginBottom: '50px',
            bottom: 0,
            position: 'fixed',
            width: '100%',
            backgroundColor: 'transparent',
        };
        const buttonSX = {
            width: '100%',
            mx: '2%'
        };
        return (
            <ThemeProvider theme={customTheme}>
                <Box sx={mouseLMRBoxSX}>
                    {this.context.button23 !== 2 ? (
                        <>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_button('Left')}
                                sx={buttonSX}
                            >L</Button>
                            {this.context.button23 === 0 ? (
                                <Button
                                    color="primary"
                                    variant="outlined"
                                    onClick={() => api_button('Middle')}
                                    sx={buttonSX}
                                >M</Button>
                            ) : null}
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_button('Right')}
                                sx={buttonSX}
                            >R</Button>
                        </>
                    ) : null}
                </Box>
                <Box sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '100%',
                    backgroundColor: 'transparent',
                }}>
                    <Collapse in={this.context.buttonSW4}>
                        <Box>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_button('DUp')}
                                sx={{mb: 2, width: dPadButtonWidth, height: dPadButtonHeight}}
                            >↑</Button>
                        </Box>
                        <Box
                            sx={{
                                display: 'flex',
                                flexDirection: 'row',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_button('DLeft')}
                                sx={{width: dPadButtonWidth, height: dPadButtonHeight}}
                            >←</Button>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_button('DDown')}
                                sx={{mx: 2, width: dPadButtonWidth, height: dPadButtonHeight}}
                            >↓</Button>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_button('DRight')}
                                sx={{width: dPadButtonWidth, height: dPadButtonHeight}}
                            >→</Button>
                        </Box>
                        <Box>
                        </Box>
                    </Collapse>
                </Box>
            </ThemeProvider>
        );
    }

}

VButtons.contextType = Context;

export default VButtons;
