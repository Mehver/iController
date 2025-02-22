import React, {Component} from 'react';
import debounce from 'lodash/debounce';
import {Slider, List, ListItem, Divider} from "@mui/material";
import {VolumeDown, VolumeUp} from "@mui/icons-material";
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {api_volume_get, api_volume_set} from "../../api/volume";
import {Context} from "../../utils/Context";

class VolumeMenu extends Component {
    state = {
        value: 0,
        lastSuccessfulValue: 0,
    };

    componentDidMount() {
        this._isMounted = true;
        // 延迟获取音量，防止服务器报错
        for (let i = 100; i < 2000; i = (i + 200) * 2) {
            setTimeout(() => {
                this.fetchVolume();
            }, i);
        }
    }

    componentWillUnmount() {
        this._isMounted = false;
        this.debouncedHandleCommit.cancel(); // 取消防抖调用
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

    handleChange = (event, newValue) => {
        // 立即更新UI
        this.setState({value: newValue});
        // 使用消抖函数调用API更新音量
        this.debouncedHandleCommit(newValue);
    };

    debouncedHandleCommit = debounce((newValue) => {
        // noinspection JSVoidFunctionReturnValueUsed, JSUnusedLocalSymbols
        api_volume_set(String(newValue))
            .then(data => {
                if (this._isMounted) {
                    this.setState({lastSuccessfulValue: newValue});
                }
            })
            .catch(error => {
                console.error("Failed to set volume:", error);
            });
    }, 300); // 300ms的防抖时间

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

VolumeMenu.contextType = Context;

export default VolumeMenu;
