// Context.jsx
import React, {createContext, Component} from 'react';
import {setCookie, getCookie} from './CookieIO';
import {defaultPrimaryColor, defaultSecondaryColor} from './Theme';

export const Context = createContext(undefined);

// 定义所有状态项的配置：包括默认值、是否需要 cookie 同步、数据类型、以及是否提供 toggle 方法
const settingsConfig = {
    drawerOpen: {default: false, cookie: null},
    drawerRL: {default: 'l', cookie: 'drawerRL'},
    tPadSensitivity: {default: 1.0, cookie: 'tPadSensitivity', type: 'float'},
    mWheelSensitivity: {default: 1.0, cookie: 'mWheelSensitivity', type: 'float'},
    buttonSW1: {default: false, cookie: 'buttonSW1', type: 'boolean', toggle: true},
    buttonSW4: {default: true, cookie: 'buttonSW4', type: 'boolean', toggle: true},
    button23: {default: 0, cookie: 'button23', type: 'int'},
    autoCollapse: {default: false, cookie: 'autoCollapse', type: 'boolean', toggle: true},
    mouseWheelMenuType: {default: 0, cookie: 'mouseWheelMenuType', type: 'int'},
    sidebarModulesSettingMenu: {default: false, cookie: 'sidebarModulesSettingMenu', type: 'boolean', toggle: true},
    sidebarMouseWheelMenu: {default: false, cookie: 'sidebarMouseWheelMenu', type: 'boolean', toggle: true},
    sidebarKeyboardMenu: {default: false, cookie: 'sidebarKeyboardMenu', type: 'boolean', toggle: true},
    sidebarVolumeMenu: {default: false, cookie: 'sidebarVolumeMenu', type: 'boolean', toggle: true},
    sidebarSettingMenu: {default: false, cookie: 'sidebarSettingMenu', type: 'boolean', toggle: true},
    sidebarThemeMenu: {default: false, cookie: 'sidebarThemeMenu', type: 'boolean', toggle: true},
    primaryColor: {default: defaultPrimaryColor, cookie: 'primaryColor'},
    secondaryColor: {default: defaultSecondaryColor, cookie: 'secondaryColor'},
    openMenuSW: {default: 0, cookie: 'openMenuSW', type: 'int'},
    keyboardDataSendMod: {default: 'a', cookie: 'keyboardDataSendMod'},
};

// 根据配置解析 cookie 值
const parseValue = (value, type, defaultValue) => {
    if (value === null || value === undefined) return defaultValue;
    switch (type) {
        case 'int':
            return parseInt(value, 10) || defaultValue;
        case 'float':
            return parseFloat(value) || defaultValue;
        case 'boolean':
            return value === 'true';
        default:
            return value;
    }
};

export class ContextProvider extends Component {
    constructor(props) {
        super(props);
        const state = {};

        // 遍历配置，为每个状态项初始化值（优先使用 cookie 值，否则使用默认值）
        Object.keys(settingsConfig).forEach(key => {
            const {default: def, type, cookie} = settingsConfig[key];
            const cookieValue = cookie ? getCookie(cookie) : undefined;
            state[key] = parseValue(cookieValue, type, def);
        });

        // 自动生成更新函数
        Object.keys(settingsConfig).forEach(key => {
            const {cookie, toggle} = settingsConfig[key];
            const capitalizedKey = key.charAt(0).toUpperCase() + key.slice(1);

            // 生成 setter：更新状态并同步 cookie（如果配置了 cookie）
            state[`set${capitalizedKey}`] = (value) => {
                this.setState({[key]: value}, () => {
                    if (cookie) {
                        setCookie(cookie, value, 7);
                    }
                });
            };

            // 如果配置了 toggle，则生成 toggle 方法
            if (toggle) {
                state[`toggle${capitalizedKey}`] = () => {
                    this.setState(prevState => {
                        const newValue = !prevState[key];
                        if (cookie) {
                            setCookie(cookie, newValue, 7);
                        }
                        return {[key]: newValue};
                    });
                };
            }
        });

        this.state = state;
    }

    render() {
        return (
            <Context.Provider value={this.state}>
                {this.props.children}
            </Context.Provider>
        );
    }
}
