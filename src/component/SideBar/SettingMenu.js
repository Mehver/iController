import React, {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    List,
    ListItem,
    TextField,
    Radio,
    RadioGroup,
    FormControlLabel,
    FormControl, Typography
} from "@mui/material";
import {ThemeProvider} from '@mui/material/styles';
import {customTheme} from '../../utils/Theme';

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
        return (
            <ThemeProvider theme={customTheme}>
                <List component="div" disablePadding>
                    <ListItem>
                        <Typography style={{fontSize: '1rem'}}>Sidebar Toggle</Typography>
                        <div style={{flex: 1}}/>
                        <FormControl component="fieldset">
                            <RadioGroup
                                row
                                aria-label="sidebar-position"
                                name="row-radio-buttons-group"
                                value={this.state.drawerSide}
                                onChange={this.handleRadioChange}
                            >
                                <FormControlLabel value="l" control={<Radio/>} label="L"/>
                                <FormControlLabel value="r" control={<Radio/>} label="R"/>
                            </RadioGroup>
                        </FormControl>
                    </ListItem>
                    <ListItem>
                    <div style={{flex: 1}}/>
                        <TextField
                            label="Touchpad Sensitivity"
                            variant="outlined"
                            value={tPadSensitivity}
                            onChange={(e) => this.handleTextFieldChange(e, 'tPadSensitivity')}
                            onBlur={() => this.handleBlur('tPadSensitivity')}
                            type="number"
                            inputProps={{step: "0.01", min: "0"}}
                            size="small"
                            fullWidth='true'
                            color="secondary"
                            focused='true'
                        />
                    </ListItem>
                    <ListItem>
                        <div style={{flex: 1}}/>
                        <TextField
                            label="Mouse Wheel Sensitivity"
                            variant="outlined"
                            value={mWheelSensitivity}
                            onChange={(e) => this.handleTextFieldChange(e, 'mWheelSensitivity')}
                            onBlur={() => this.handleBlur('mWheelSensitivity')}
                            type="number"
                            inputProps={{step: "0.01", min: "0"}}
                            size="small"
                            fullWidth='true'
                            color="secondary"
                            focused='true'
                        />
                    </ListItem>
                </List>
            </ThemeProvider>
        );
    }
}

SettingMenu.contextType = Context;

export default SettingMenu;
