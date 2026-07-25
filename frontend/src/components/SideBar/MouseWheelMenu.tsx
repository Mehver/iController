// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import React, {Component} from 'react';
import {List, ListItem, Box, IconButton, Divider, Collapse, Slider} from "@mui/material";
import { Add as AddIcon, Remove as RemoveIcon } from '@mui/icons-material';
import {Context} from '../../utils/Context';
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
        let sliderHeight = 150;
        if (window.innerWidth < 280) {
            sliderHeight = 150.0 * window.innerWidth / 280.0;
        }

        const sliderSX = {
            height: sliderHeight,
            '& .MuiSlider-thumb': {
                color: this.context.secondaryColor,
            },
            '& .MuiSlider-track': {
                color: this.context.secondaryColor,
            },
            '& .MuiSlider-rail': {
                color: this.context.secondaryColor,
                opacity: 0.3,
            },
            '& .MuiSlider-valueLabel': {
                backgroundColor: this.context.secondaryColor,
                color: this.context.primaryColor,
            },
            '& .MuiSlider-mark': {
                color: this.context.secondaryColor,
            },
            '& .MuiSlider-markLabel': {
                color: this.context.secondaryColor,
            },
        };

        const marks = [
            {value: -4, label: '-4'},
            {value: 0, label: '0'},
            {value: 4, label: '4'},
        ];

        return (
            <>
                <List component="div" disablePadding style={{width: '100%', display: 'flex', justifyContent: 'center'}}>
                    <ListItem>
                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}
                             style={{backgroundColor: this.context.primaryColor, width: '100%'}}>
                            <Collapse
                                in={
                                    this.context.mouseWheelMenuType === 2 || this.context.mouseWheelMenuType === 0
                                }>
                                <Slider
                                    value={this.state.value}
                                    min={-4}
                                    max={4}
                                    step={1}
                                    orientation="vertical"
                                    valueLabelDisplay="on"
                                    marks={marks}
                                    sx={sliderSX}
                                    onChange={(_e, val) => this.updateValue(val as number)}
                                />
                            </Collapse>
                            <Collapse
                                in={
                                    this.context.mouseWheelMenuType === 2 || this.context.mouseWheelMenuType === 1
                                }>
                                <Box sx={{ display: 'flex', gap: 2 }}>
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
