import {Component} from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {ButtonContext} from '../context/ButtonContext';

const customTheme = createTheme({
    palette: {
        primary: {
            main: '#6df',
        },
    },
});

class MouseDPadButtons extends Component {
    constructor(props) {
        super(props);
    }

    // 发送按钮信号的函数，传递信号为纯文本
    sendButtonSignal = (buttonType) => {
        // 使用简短编码表示不同的按钮
        const signal =
            buttonType === 'Left' ? 'L' :
                buttonType === 'Middle' ? 'M' :
                    buttonType === 'Right' ? 'R' :
                        buttonType === 'DUp' ? 'W' :
                            buttonType === 'DLeft' ? 'A' :
                                buttonType === 'DDown' ? 'S' :
                                    buttonType === 'DRight' ? 'D' : '';

        fetch('/button_signal', {
            method: 'POST',
            headers: {
                'Content-Type': 'text/plain',
            },
            body: signal,
        })
            .then(response => response.json())
            .then(data => console.log('Success:', data))
            .catch((error) => {
                console.error('Error:', error);
            });
    };

    render() {
        let buttonWidth = window.innerWidth / 4;
        let buttonHeight = window.innerHeight / 5;
        return (
            <ThemeProvider theme={customTheme}>
                <Box sx={{
                    display: 'flex',
                    justifyContent: 'space-between', // 使按钮间有等距间隙
                    p: 1, // 设置内边距
                    marginBottom: '50px',
                    bottom: 0,
                    position: 'fixed',
                    width: '100%',
                    backgroundColor: 'transparent',
                }}>
                    {this.context.button23 !== 2 ? (
                        <>
                            <Button color="primary" variant="outlined" onClick={() => this.sendButtonSignal('Left')}
                                    sx={{width: '100%', mx: '2%'}}>L</Button>
                            {this.context.button23 === 0 ? (
                                <Button color="primary" variant="outlined"
                                        onClick={() => this.sendButtonSignal('Middle')}
                                        sx={{width: '100%', mx: '2%'}}>M</Button> // 中间按钮左右各留出一些空间
                            ) : null}
                            <Button color="primary" variant="outlined" onClick={() => this.sendButtonSignal('Right')}
                                    sx={{width: '100%', mx: '2%'}}>R</Button>
                        </>
                    ) : null}
                </Box>
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '100%',
                        backgroundColor: 'transparent',
                    }}
                >
                    {this.context.buttonSW4 ? (
                        <>
                            <Box>
                                <Button color="primary" variant="outlined" onClick={() => this.sendButtonSignal('DUp')}
                                        sx={{mb: 2, width: buttonWidth, height: buttonHeight}}>↑</Button>
                            </Box>
                            <Box
                                sx={{
                                    display: 'flex',
                                    flexDirection: 'row',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                }}
                            >
                                <Button color="primary" variant="outlined"
                                        onClick={() => this.sendButtonSignal('DLeft')}
                                        sx={{width: buttonWidth, height: buttonHeight}}>←</Button>
                                <Button color="primary" variant="outlined"
                                        onClick={() => this.sendButtonSignal('DDown')}
                                        sx={{mx: 2, width: buttonWidth, height: buttonHeight}}>↓</Button>
                                <Button color="primary" variant="outlined"
                                        onClick={() => this.sendButtonSignal('DRight')}
                                        sx={{width: buttonWidth, height: buttonHeight}}>→</Button>
                            </Box>
                            <Box>
                            </Box>
                        </>
                    ) : null}
                </Box>
            </ThemeProvider>
        );
    }

}

MouseDPadButtons.contextType = ButtonContext;

export default MouseDPadButtons;
