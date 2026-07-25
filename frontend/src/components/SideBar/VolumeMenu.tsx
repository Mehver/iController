// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import React, {Component} from 'react';
import debounce from 'lodash/debounce';
import {Slider, List, ListItem, Divider} from "@mui/material";
import {VolumeDown, VolumeUp} from "@mui/icons-material";
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {api_volume_get, api_volume_set} from "../../api/volume";
import {Context} from "../../utils/Context";
import {AppContextType} from '../../types';

interface VolumeMenuState {
    value: number;
    lastSuccessfulValue: number;
}

class VolumeMenu extends Component<object, VolumeMenuState> {
    static contextType = Context;
    declare context: AppContextType;

    private _isMounted: boolean = false;
    private debouncedHandleCommit: ReturnType<typeof debounce>;

    state: VolumeMenuState = {
        value: 0,
        lastSuccessfulValue: 0,
    };

    componentDidMount() {
        this._isMounted = true;
        for (let i = 100; i < 2000; i = (i + 200) * 2) {
            setTimeout(() => {
                this.fetchVolume();
            }, i);
        }
    }

    componentWillUnmount() {
        this._isMounted = false;
        this.debouncedHandleCommit.cancel();
    }

    fetchVolume = () => {
        api_volume_get()
            .then(data => {
                if (this._isMounted) {
                    this.setState({
                        value: data.volume,
                        lastSuccessfulValue: data.volume,
                    });
                }
            })
            .catch(error => {
                console.error("Failed to fetch volume:", error);
            });
    };

    handleChange = (_event: Event, newValue: number | number[]) => {
        const val = Array.isArray(newValue) ? newValue[0] : newValue;
        this.setState({value: val});
        this.debouncedHandleCommit(val);
    };

    debouncedHandleCommit = debounce((newValue: number) => {
        api_volume_set(String(newValue))
            .then(_data => {
                if (this._isMounted) {
                    this.setState({lastSuccessfulValue: newValue});
                }
            })
            .catch(error => {
                console.error("Failed to set volume:", error);
            });
    }, 300);

    render() {
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
                    <ListItem display="flex" alignItems="center">
                        <VolumeDown/>
                        <Slider
                            value={this.state.value}
                            color="secondary"
                            onChange={this.handleChange}
                        />
                        <VolumeUp/>
                    </ListItem>
                </List>
                <Divider/>
            </ThemeProvider>
        );
    }
}

export default VolumeMenu;
