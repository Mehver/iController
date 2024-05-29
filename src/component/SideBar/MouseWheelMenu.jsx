import React, {Component} from 'react';
import {Knob} from 'primereact/knob';
import {List, ListItem, Box, IconButton, Divider, Collapse} from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import {Context} from '../../utils/Context';
import {primaryColor, secondaryColor, secondaryColorTrans} from '../../utils/Theme';
import {api_mousewheel} from "../../api/mousewheel";
import ModulesSettingMenu from "./ModulesSettingMenu";

class MouseWheelMenu extends Component {
    constructor(props) {
        super(props);
        this.state = {value: 0};
    }

    updateValue = (newValue) => {
        this.setState({value: newValue}); // 更新状态
        if (newValue !== 0) {
            api_mousewheel(newValue * this.context.mWheelSensitivity);
        }
    };

    componentDidMount() {
        this.resetTimer();
    }

    // noinspection JSCheckFunctionSignatures
    componentDidUpdate(prevProps, prevState) {
        if (prevState.value !== this.state.value) {
            this.resetTimer();
        }
    }

    componentWillUnmount() {
        clearTimeout(this.timer);
    }

    resetTimer = () => {
        clearTimeout(this.timer);
        this.timer = setTimeout(() => this.updateValue(0), 500); // 0.5秒后自动回中
    };

    render() {
        let knobSize = 150;
        if (window.innerWidth < 280) {
            knobSize = 150.0 * window.innerWidth / 280.0;
        }

        return (
            <>
                <List component="div" disablePadding style={{width: '100%', display: 'flex', justifyContent: 'center'}}>
                    <ListItem>
                        <Box display="flex" flexDirection="column" alignItems="center" gap={2}
                             style={{backgroundColor: primaryColor, width: '100%'}}>
                            <Collapse
                                in={
                                    this.context.mouseWheelMenuType === 2 || this.context.mouseWheelMenuType === 0
                                }>
                                <Knob value={this.state.value} size={knobSize} min={-4} max={4} step={1}
                                      onChange={(e) => this.updateValue(e.value)}
                                      textColor={secondaryColor}
                                      valueColor={secondaryColor}
                                      rangeColor={secondaryColorTrans}
                                      strokeWidth={10}
                                      valueTemplate="{value}"
                                />
                            </Collapse>
                            <Collapse
                                in={
                                    this.context.mouseWheelMenuType === 2 || this.context.mouseWheelMenuType === 1
                                }>
                                <Box display="flex" gap={2}>
                                    <IconButton size="large" onClick={() => {
                                        const newValue = Math.max(this.state.value - 1, -4);
                                        this.updateValue(newValue);
                                    }} disabled={this.state.value === -4}>
                                        <RemoveIcon fontSize="inherit" sx={{color: secondaryColor}}/>
                                    </IconButton>
                                    <IconButton size="large" onClick={() => {
                                        const newValue = Math.min(this.state.value + 1, 4);
                                        this.updateValue(newValue);
                                    }} disabled={this.state.value === 4}>
                                        <AddIcon fontSize="inherit" sx={{color: secondaryColor}}/>
                                    </IconButton>
                                </Box>
                            </Collapse>
                        </Box>
                    </ListItem>
                </List>
                <Divider/>
            </>
        );
    }
}

MouseWheelMenu.contextType = Context;

export default MouseWheelMenu;
