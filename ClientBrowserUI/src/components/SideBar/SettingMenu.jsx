import React, {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    List,
    ListItem,
    TextField,
    Radio,
    RadioGroup,
    FormControlLabel,
    FormControl,
    Typography,
    ListItemButton,
    Box
} from "@mui/material";
import {
    CheckBoxOutlineBlankRounded,
    CheckBoxRounded
} from '@mui/icons-material';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import i18n from '../../utils/i18n';

class SettingMenu extends Component {
    constructor(props) {
        super(props);
        this.state = {
            drawerSide: 'l', // 初始边栏位置为右边
            tPadSensitivity: '',
            mWheelSensitivity: '',
        };
    }

    componentDidMount() {
        // 组件挂载时，使用context中的值初始化局部状态
        this.setState({
            drawerSide: this.context.drawerRL,
            tPadSensitivity: this.context.tPadSensitivity.toString(),
            mWheelSensitivity: this.context.mWheelSensitivity.toString(),
        });
    }

    handleRadioChange = (event) => {
        this.setState({drawerSide: event.target.value});
        this.context.setDrawerRL(event.target.value);
    };

    // 处理输入值的变化，但不立即更新context
    handleTextFieldChange = (event, type) => {
        this.setState({[type]: event.target.value});
    };


    // 当输入框失去焦点时，根据类型更新context
    handleBlur = (type) => {
        const value = this.state[type];
        const numValue = parseFloat(value);
        if (!isNaN(numValue) && numValue > 0) {
            if (type === 'tPadSensitivity') {
                this.context.setTPadSensitivity(numValue);
            } else if (type === 'mWheelSensitivity') {
                this.context.setMWheelSensitivity(numValue);
            }
        } else {
            // 如果输入非法，重置为context的当前值
            this.setState({
                [type]: this.context[type].toString(),
            });
        }
    };

    render() {
        const {tPadSensitivity, mWheelSensitivity} = this.state;
        let iconSizeSX = {};
        let boxIconSX = {};
        if (window.innerWidth < 280) {
            iconSizeSX.fontSize = `${window.innerWidth / 300.0}rem`;
            boxIconSX.marginRight = '-50px';
        }

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
                <List component="div" disablePadding>
                    <ListItem>
                        <Typography style={{fontSize: '1rem'}}>{i18n.Sidebar.SettingMenu.AutoCollapseSubmenus[this.context.i18n]}</Typography>
                        <div style={{flex: 1}}/>
                        <ListItemButton onClick={() => {
                            this.context.toggleAutoCollapse();
                        }}>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                <CheckBoxRounded sx={iconSizeSX}/> :
                                <CheckBoxOutlineBlankRounded sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <Typography style={{fontSize: '1rem'}}>{i18n.Sidebar.SettingMenu.SidebarToggle[this.context.i18n]}</Typography>
                        <div style={{flex: 1}}/>
                        <FormControl component="fieldset">
                            <RadioGroup
                                row
                                aria-label="sidebar-position"
                                name="row-radio-buttons-group"
                                value={this.state.drawerSide}
                                onChange={this.handleRadioChange}
                                color="secondary"
                            >
                                <FormControlLabel
                                    value="l"
                                    control={<Radio
                                        sx={{
                                            color: this.context.secondaryColor,
                                            '&.Mui-checked': {
                                                color: this.context.secondaryColor,
                                            },
                                        }}
                                        color="secondary"
                                    />}
                                    label="L"
                                />
                                <FormControlLabel
                                    value="r"
                                    control={<Radio
                                        sx={{
                                            color: this.context.secondaryColor,
                                            '&.Mui-checked': {
                                                color: this.context.secondaryColor,
                                            },
                                        }}
                                        color="secondary"
                                    />}
                                    label="R"
                                />
                            </RadioGroup>
                        </FormControl>
                    </ListItem>
                    <ListItem>
                        <Typography style={{fontSize: '1rem'}}>{i18n.Sidebar.SettingMenu.AdjustmentParameters[this.context.i18n]}</Typography>
                        <div style={{flex: 1}}/>
                    </ListItem>
                    <ListItem>
                        <Typography style={{fontSize: '1rem'}}>&nbsp;</Typography>
                        <div style={{flex: 1}}/>
                        <TextField
                            label={i18n.Sidebar.SettingMenu.TPadSensitivity[this.context.i18n]}
                            variant="outlined"
                            value={tPadSensitivity}
                            onChange={(e) => this.handleTextFieldChange(e, 'tPadSensitivity')}
                            onBlur={() => this.handleBlur('tPadSensitivity')}
                            type="number"
                            inputProps={{step: "0.01", min: "0"}}
                            size="small"
                            fullWidth='true'
                            color="secondary"
                            sx={{
                                input: {
                                    color: this.context.secondaryColor,
                                    caretColor: this.context.secondaryColor,
                                }
                            }}
                            focused='true'
                        />
                        <Typography style={{fontSize: '1rem'}}>&nbsp;</Typography>
                    </ListItem>
                    <ListItem>
                        <Typography style={{fontSize: '1rem'}}>&nbsp;</Typography>
                        <div style={{flex: 1}}/>
                        <TextField
                            label={i18n.Sidebar.SettingMenu.MWheelSensitivity[this.context.i18n]}
                            variant="outlined"
                            value={mWheelSensitivity}
                            onChange={(e) => this.handleTextFieldChange(e, 'mWheelSensitivity')}
                            onBlur={() => this.handleBlur('mWheelSensitivity')}
                            type="number"
                            inputProps={{step: "0.01", min: "0"}}
                            size="small"
                            fullWidth='true'
                            color="secondary"
                            sx={{
                                input: {
                                    color: this.context.secondaryColor,
                                    caretColor: this.context.secondaryColor,
                                }
                            }}
                            focused='true'
                        />
                        <Typography style={{fontSize: '1rem'}}>&nbsp;</Typography>
                    </ListItem>
                </List>
            </ThemeProvider>
        );
    }
}

SettingMenu.contextType = Context;

export default SettingMenu;
