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

class VolumeMenu extends Component<{drawerOpen: boolean; expanded: boolean}, VolumeMenuState> {
    static contextType = Context;
    declare context: AppContextType;

    private _isMounted: boolean = false;
    private _requestId = 0;
    private _editVersion = 0;
    private _lastWrite: Promise<void> = Promise.resolve();

    state: VolumeMenuState = {
        value: 0,
        lastSuccessfulValue: 0,
    };

    componentDidMount() {
        this._isMounted = true;
        if (this.props.drawerOpen) void this.fetchVolume();
    }

    componentDidUpdate(previous: {drawerOpen: boolean; expanded: boolean}) {
        if (!this.props.drawerOpen) {
            if (previous.drawerOpen) this.invalidateRead();
            return;
        }
        // One refresh for a render that both opens the drawer and changes the Collapse.
        if (!previous.drawerOpen || previous.expanded !== this.props.expanded) void this.fetchVolume();
    }

    private invalidateRead() {
        this._requestId++;
        this.debouncedHandleCommit.cancel();
    }

    componentWillUnmount() {
        this._isMounted = false;
        this.invalidateRead();
    }

    fetchVolume = async () => {
        if (!this._isMounted || !this.props.drawerOpen) return;
        this.invalidateRead(); // A closed/opened drawer must not send an old draft.
        const requestId = this._requestId, editVersion = this._editVersion;
        await this._lastWrite; // Includes every already-sent write, even overlapping POSTs.
        if (!this._isMounted || !this.props.drawerOpen || requestId !== this._requestId || editVersion !== this._editVersion) return;
        return api_volume_get()
            .then(data => {
                if (this._isMounted && this.props.drawerOpen && requestId === this._requestId && editVersion === this._editVersion) {
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
        if (!this._isMounted || !this.props.drawerOpen) return;
        this._editVersion++;
        const val = Array.isArray(newValue) ? newValue[0] : newValue;
        this.setState({value: val});
        this.debouncedHandleCommit(val);
    };

    debouncedHandleCommit = debounce((newValue: number) => {
        const requestId = this._requestId, editVersion = this._editVersion;
        const write = api_volume_set(String(newValue))
            .then(_data => {
                if (this._isMounted && this.props.drawerOpen && requestId === this._requestId && editVersion === this._editVersion) {
                    this.setState({lastSuccessfulValue: newValue});
                }
            })
            .catch(error => {
                console.error("Failed to set volume:", error);
            });
        this._lastWrite = Promise.all([this._lastWrite, write]).then(() => undefined);
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
                    <ListItem sx={{ display: 'flex', alignItems: 'center' }}>
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
