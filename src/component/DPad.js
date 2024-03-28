import {Component} from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import {Collapse} from "@mui/material";
import {ThemeProvider} from '@mui/material/styles';
import {customTheme} from '../utils/Theme';
import {Context} from '../utils/Context';
import {api_dpad} from '../api/dpad';

class DPad extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        let dPadButtonWidth = window.innerWidth / 4;
        let dPadButtonHeight = window.innerHeight / 5;
        return (
            <ThemeProvider theme={customTheme}>
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
                                onClick={() => api_dpad('DUp')}
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
                                onClick={() => api_dpad('DLeft')}
                                sx={{width: dPadButtonWidth, height: dPadButtonHeight}}
                            >←</Button>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_dpad('DDown')}
                                sx={{mx: 2, width: dPadButtonWidth, height: dPadButtonHeight}}
                            >↓</Button>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_dpad('DRight')}
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

DPad.contextType = Context;

export default DPad;
