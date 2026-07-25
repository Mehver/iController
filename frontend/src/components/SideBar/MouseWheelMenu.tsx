// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import React, {Component} from 'react';
import {Knob, KnobChangeEvent} from 'primereact/knob';
import {List, ListItem, Box, IconButton, Divider, Collapse} from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import {Context} from '../../utils/Context';
import {convertHexToRGBA} from '../../utils/Theme';
import {api_mousewheel} from "../../api/mousewheel";
import {AppContextType} from '../../types';

interface MouseWheelMenuState {
    value: number;
}

class MouseWheelMenu extends Component<object, MouseWheelMenuState> {
    static contextType = Context;
    declare context: AppContextType;

    private timer: ReturnType<typeof setTimeout> | null = null;

    constructor(props: object) {
        super(props);
        this.state = {value: 0};
    }

    updateValue = (newValue: number) => {
        this.setState({value: newValue});
        if (newValue !== 0) {
            api_mousewheel(newValue * this.context.mWheelSensitivity);
        }
    };

    componentDidMount() {
        this.resetTimer();
    }

    componentDidUpdate(_prevProps: Readonly<object>, prevState: Readonly<MouseWheelMenuState>) {
        if (prevState.value !== this.state.value) {
            this.resetTimer();
        }
    }

    componentWillUnmount() {
        if (this.timer) clearTimeout(this.timer);
    }

    resetTimer = () => {
        if (this.timer) clearTimeout(this.timer);
        this.timer = setTimeout(() => this.updateValue(0), 500);
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
                             style={{backgroundColor: this.context.primaryColor, width: '100%'}}>
                            <Collapse
                                in={
                                    this.context.mouseWheelMenuType === 2 || this.context.mouseWheelMenuType === 0
                                }>
                                <Knob value={this.state.value} size={knobSize} min={-4} max={4} step={1}
                                      onChange={(e: KnobChangeEvent) => this.updateValue(e.value)}
                                      textColor={this.context.secondaryColor}
                                      valueColor={this.context.secondaryColor}
                                      rangeColor={convertHexToRGBA(this.context.secondaryColor, 0.5) || undefined}
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
                                        <RemoveIcon fontSize="inherit" sx={{color: this.context.secondaryColor}}/>
                                    </IconButton>
                                    <IconButton size="large" onClick={() => {
                                        const newValue = Math.min(this.state.value + 1, 4);
                                        this.updateValue(newValue);
                                    }} disabled={this.state.value === 4}>
                                        <AddIcon fontSize="inherit" sx={{color: this.context.secondaryColor}}/>
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

export default MouseWheelMenu;
