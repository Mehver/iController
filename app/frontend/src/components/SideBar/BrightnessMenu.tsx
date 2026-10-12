// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import React, {Component} from 'react';
import debounce from 'lodash/debounce';
import {Slider, List, ListItem, Divider} from "@mui/material";
import {BrightnessLow, BrightnessHigh} from "@mui/icons-material";
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {api_brightness_get, api_brightness_set} from "../../api/brightness";
import {Context} from "../../utils/Context";
import {AppContextType} from '../../types';

interface BrightnessMenuState {
    value: number;
}

class BrightnessMenu extends Component<object, BrightnessMenuState> {
    static contextType = Context;
    declare context: AppContextType;

    private _isMounted: boolean = false;

    state: BrightnessMenuState = {value: 0};

    componentDidMount() {
        this._isMounted = true;
        this.fetchBrightness();
    }

    componentWillUnmount() {
        this._isMounted = false;
        this.debouncedHandleCommit.cancel();
    }

    fetchBrightness = () => {
        api_brightness_get()
            .then(data => {
                if (this._isMounted) {
                    this.setState({value: data.brightness});
                }
            })
            .catch(error => {
                console.error("Failed to fetch brightness:", error);
            });
    };

    handleChange = (_event: Event, newValue: number | number[]) => {
        const value = Array.isArray(newValue) ? newValue[0] : newValue;
        this.setState({value});
        this.debouncedHandleCommit(value);
    };

    debouncedHandleCommit = debounce((newValue: number) => {
        api_brightness_set(String(newValue))
            .catch(error => {
                console.error("Failed to set brightness:", error);
            });
    }, 300);

    render() {
        const customTheme = createTheme({
            palette: {
                primary: {main: this.context.primaryColor},
                secondary: {main: this.context.secondaryColor},
            },
        });

        return (
            <ThemeProvider theme={customTheme}>
                <List component="div" disablePadding>
                    <ListItem sx={{display: 'flex', alignItems: 'center'}}>
                        <BrightnessLow/>
                        <Slider
                            value={this.state.value}
                            color="secondary"
                            min={0}
                            max={100}
                            onChange={this.handleChange}
                        />
                        <BrightnessHigh/>
                    </ListItem>
                </List>
                <Divider/>
            </ThemeProvider>
        );
    }
}

export default BrightnessMenu;
