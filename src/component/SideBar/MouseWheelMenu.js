import React, { Component } from 'react';
import { Knob } from 'primereact/knob';
import { List, ListItem, Box, Divider, IconButton } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import { Context } from '../../utils/Context';
import { api_mousewheel } from "../../api/mousewheel";

class MouseWheelMenu extends Component {
    constructor(props) {
        super(props);
        this.state = { value: 0 };
    }

    updateValue = (newValue) => {
        this.setState({ value: newValue }); // 更新状态
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
                <List component="div" disablePadding style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
                    <ListItem>
                        <Box display="flex" flexDirection="column" alignItems="center" gap={2}
                            style={{ backgroundColor: '#6df', width: '100%' }}>
                            <Knob value={this.state.value} size={knobSize} min={-4} max={4} step={1}
                                onChange={(e) => this.updateValue(e.value)}
                                textColor="#333"
                                valueColor="#333"
                                rangeColor="rgba(51, 51, 51, 0.5)"
                                strokeWidth={10}
                                valueTemplate="{value}"
                            />
                            <Box display="flex" gap={2}>
                                <IconButton size="large" onClick={() => {
                                    const newValue = Math.max(this.state.value - 1, -4);
                                    this.updateValue(newValue);
                                }} disabled={this.state.value === -4}>
                                    <RemoveIcon fontSize="inherit" sx={{ color: '#333' }} />
                                </IconButton>
                                <IconButton size="large" onClick={() => {
                                    const newValue = Math.min(this.state.value + 1, 4);
                                    this.updateValue(newValue);
                                }} disabled={this.state.value === 4}>
                                    <AddIcon fontSize="inherit" sx={{ color: '#333' }} />
                                </IconButton>
                            </Box>
                        </Box>
                    </ListItem>
                </List>
                {/*<Divider />*/}
            </>
        );
    }
}

MouseWheelMenu.contextType = Context;

export default MouseWheelMenu;
