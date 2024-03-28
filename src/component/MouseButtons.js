import {Component} from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import {ThemeProvider} from '@mui/material/styles';
import {customTheme} from '../utils/Theme';
import {Context} from '../utils/Context';
import {api_mousebutton} from '../api/mousebutton';

class MouseButtons extends Component {
    constructor(props) {
        super(props);
    }

    render() {
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
                                onClick={() => api_mousebutton('Left')}
                                sx={buttonSX}
                            >L</Button>
                            {this.context.button23 === 0 ? (
                                <Button
                                    color="primary"
                                    variant="outlined"
                                    onClick={() => api_mousebutton('Middle')}
                                    sx={buttonSX}
                                >M</Button>
                            ) : null}
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_mousebutton('Right')}
                                sx={buttonSX}
                            >R</Button>
                        </>
                    ) : null}
                </Box>
            </ThemeProvider>
        );
    }

}

MouseButtons.contextType = Context;

export default MouseButtons;
