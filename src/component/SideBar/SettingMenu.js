import React, { Component } from 'react';
import { Context } from '../../utils/Context';
import { ListItem, TextField } from "@mui/material";

class SettingMenu extends Component {
    // 初始化局部状态以存储临时输入值
    state = {
        tPadSensitivity: '',
        mWheelSensitivity: '',
    };

    componentDidMount() {
        // 组件挂载时，使用context中的值初始化局部状态
        this.setState({
            tPadSensitivity: this.context.tPadSensitivity.toString(),
            mWheelSensitivity: this.context.mWheelSensitivity.toString(),
        });
    }

    // 处理输入值的变化，但不立即更新context
    handleChange = (event, type) => {
        this.setState({ [type]: event.target.value });
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
        const { tPadSensitivity, mWheelSensitivity } = this.state;
        return (
            <>
                <ListItem>
                    <TextField
                        label="Touchpad Sensitivity"
                        variant="outlined"
                        value={tPadSensitivity}
                        onChange={(e) => this.handleChange(e, 'tPadSensitivity')}
                        onBlur={() => this.handleBlur('tPadSensitivity')}
                        type="number"
                        inputProps={{ step: "0.01", min: "0" }}
                    />
                </ListItem>
                <ListItem>
                    <TextField
                        label="Mouse Wheel Sensitivity"
                        variant="outlined"
                        value={mWheelSensitivity}
                        onChange={(e) => this.handleChange(e, 'mWheelSensitivity')}
                        onBlur={() => this.handleBlur('mWheelSensitivity')}
                        type="number"
                        inputProps={{ step: "0.01", min: "0" }}
                    />
                </ListItem>
            </>
        );
    }
}

SettingMenu.contextType = Context;

export default SettingMenu;
