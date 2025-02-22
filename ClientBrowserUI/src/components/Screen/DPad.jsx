import {Component} from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import {Collapse} from "@mui/material";
import {
    KeyboardArrowDownOutlined,
    KeyboardArrowUpOutlined,
    KeyboardArrowLeftOutlined,
    KeyboardArrowRightOutlined
} from '@mui/icons-material';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {convertHexToRGBA} from '../../utils/Theme';
import {Context} from '../../utils/Context';
import {api_dpad} from '../../api/dpad';

class DPad extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        // 计算正方形的边长
        let dPadButtonSize = Math.min(window.innerWidth, window.innerHeight) / 4.2;
        let buttonSX = {
            width: dPadButtonSize,
            height: dPadButtonSize,
            borderRadius: '18%',
            // 使用 !important 否则按下时边框不会变粗
            borderWidth: '5px !important',
            borderColor: convertHexToRGBA(this.context.primaryColor) + ' !important',
        };
        let iconSX = {
            fontSize: dPadButtonSize * 0.4,
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
                <Box sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '100%',
                    backgroundColor: 'transparent',
                    position: 'absolute',
                    bottom: (window.innerHeight) / 2.3 - 50,
                }}>
                    <Collapse in={this.context.buttonSW4}>
                        <Box>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_dpad('DUp')}
                                sx={{...buttonSX, mb: 2}}
                            >
                                <KeyboardArrowUpOutlined
                                    color="primary"
                                    sx={iconSX}
                                />
                            </Button>
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
                                sx={buttonSX}
                            >
                                <KeyboardArrowLeftOutlined
                                    color="primary"
                                    sx={iconSX}
                                />
                            </Button>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_dpad('DDown')}
                                sx={{...buttonSX, mx: 2}}
                            >
                                <KeyboardArrowDownOutlined
                                    color="primary"
                                    sx={iconSX}
                                />
                            </Button>
                            <Button
                                color="primary"
                                variant="outlined"
                                onClick={() => api_dpad('DRight')}
                                sx={buttonSX}
                            >
                                <KeyboardArrowRightOutlined
                                    color="primary"
                                    sx={iconSX}
                                />
                            </Button>
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
