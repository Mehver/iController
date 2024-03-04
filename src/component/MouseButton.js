import React, {Component} from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import {createTheme, ThemeProvider} from '@mui/material/styles';

const customTheme = createTheme({
    palette: {
        primary: {
            main: '#6df',
        },
    },
});

class MouseButton extends Component {
    constructor(props) {
        super(props);
        this.state = {
            buttonSW2: true, // 控制所有按钮的显示与隐藏
            buttonSW3: true, // 控制中键的显示与隐藏
        };
    }

    // 发送按钮信号的函数，传递信号为纯文本
    sendButtonSignal = (buttonType) => {
        // 使用简短编码表示不同的按钮
        const signal = buttonType === 'left' ? 'L' : buttonType === 'middle' ? 'M' : 'R';

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

    componentDidMount() {
        document.getElementById("button-sw2").addEventListener("click", () => {
            this.setState(prevState => ({
                buttonSW2: !prevState.buttonSW2,
            }));
        });
        document.getElementById("button-sw3").addEventListener("click", () => {
            this.setState(prevState => ({
                buttonSW3: !prevState.buttonSW3,
            }));
        });
    };

    render() {
        return (
            <ThemeProvider theme={customTheme}>
                <Box sx={{
                    display: 'flex',
                    justifyContent: 'space-between', // 使按钮间有等距间隙
                    p: 1,
                    marginBottom: '50px', // 向上移动10px
                    bottom: 0,
                    position: 'fixed',
                    width: '100%', // 确保Box填满宽度
                    backgroundColor: 'transparent',
                }}>
                    {this.state.buttonSW2 ? (
                        <>
                            <Button color="primary" variant="outlined" onClick={() => this.sendButtonSignal('left')}
                                    sx={{width: '100%', mx: '2%'}}>L</Button>
                            {this.state.buttonSW3 ? (
                                <Button color="primary" variant="outlined"
                                        onClick={() => this.sendButtonSignal('middle')}
                                        sx={{width: '100%', mx: '2%'}}>M</Button> // 中间按钮左右各留出一些空间
                            ) : null}
                            <Button color="primary" variant="outlined" onClick={() => this.sendButtonSignal('right')}
                                    sx={{width: '100%', mx: '2%'}}>R</Button>
                        </>
                    ) : null}
                </Box>
            </ThemeProvider>
        );
    }

}

export default MouseButton;
