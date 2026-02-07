import {Component} from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {convertHexToRGBA} from '../../utils/Theme';
import {Context} from '../../utils/Context';
import {api_mousebutton} from '../../api/mousebutton';
import {Typography} from "@mui/material";

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
            // 如果屏幕宽度小于 500px，则设置为 100%, 否则设置为 500px
            width: window.innerWidth < 500 ? '100%' : '500px',
            backgroundColor: 'transparent',
        };
        const buttonSX = {
            width: '100%',
            // 使用 !important 否则按下时边框不会变粗
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

MouseButtons.contextType = Context;

export default MouseButtons;
