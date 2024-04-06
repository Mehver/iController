// Context.js
import React, {createContext, Component} from 'react';
import {setCookie, getCookie} from '../storage/CookieIO';

// 创建Context
export const Context = createContext(undefined);

// 创建Provider组件
export class ContextProvider extends Component {
    state = {
        ///////////////////////////////////////////////////////////////////////////////////
        drawerOpen: false,
        setDrawerOpen: (value) => {
            this.setState({drawerOpen: value});
        },
        ///////////////////////////////////////////////////////////////////////////////////
        // drawerRL 是用 char 类型保存的可切换状态值, 'l' 表示左侧，'r' 表示右侧
        drawerRL: getCookie('drawerRL') || 'l',
        setDrawerRL: (value) => {
            this.setState(
                {drawerRL: value}, () => {
                    setCookie('drawerRL', value, 7);
                    return {drawerRL: value};
                }
            );
        },
        ///////////////////////////////////////////////////////////////////////////////////
        // tPadSensitivity 是用 float 类型保存的可切换状态值, 是灵敏度系数，默认为 1.0，必须大于 0
        tPadSensitivity: parseFloat(getCookie('tPadSensitivity')) || 1.0,
        setTPadSensitivity: (value) => {
            this.setState(
                {tPadSensitivity: value}, () => {
                    setCookie('tPadSensitivity', value, 7);
                    return {tPadSensitivity: value};
                }
            );
        },
        ///////////////////////////////////////////////////////////////////////////////////
        mWheelSensitivity: parseFloat(getCookie('mWheelSensitivity')) || 1.0,
        setMWheelSensitivity: (value) => {
            this.setState(
                {mWheelSensitivity: value}, () => {
                    setCookie('mWheelSensitivity', value, 7);
                    return {mWheelSensitivity: value};
                }
            );
        },
        ///////////////////////////////////////////////////////////////////////////////////
        buttonSW1: getCookie('buttonSW1') === 'false',
        toggleButtonSW1: () => {
            this.setState(prevState => {
                const newValue = !prevState.buttonSW1;
                setCookie('buttonSW1', newValue, 7);
                return {buttonSW1: newValue};
            });
        },
        buttonSW4: getCookie('buttonSW4') === 'true',
        toggleButtonSW4: () => {
            this.setState(prevState => {
                const newValue = !prevState.buttonSW4;
                setCookie('buttonSW4', newValue, 7);
                return {buttonSW4: newValue};
            });
        },
        button23: parseInt(getCookie('button23'), 10) || 0,
        setButton23: (value) => {
            this.setState(
                {button23: value}, () =>
                    setCookie('button23', value, 7));
        },
        ///////////////////////////////////////////////////////////////////////////////////
        // sidebarMouseWheelMenu: getCookie('sidebarMouseWheelMenu') === 'false',
        // toggleSidebarMouseWheelMenu: () => {
        //     this.setState(prevState => {
        //         const newValue = !prevState.sidebarMouseWheelMenu;
        //         setCookie('sidebarMouseWheelMenu', newValue, 7);
        //         return {sidebarMouseWheelMenu: newValue};
        //     });
        // },
        ///////////////////////////////////////////////////////////////////////////////////
        // sidebarKeyboardMenu: getCookie('sidebarKeyboardMenu') === 'false',
        // toggleSidebarKeyboardMenu: () => {
        //     this.setState(prevState => {
        //         const newValue = !prevState.sidebarKeyboardMenu;
        //         setCookie('sidebarKeyboardMenu', newValue, 7);
        //         return {sidebarKeyboardMenu: newValue};
        //     });
        // },
        ///////////////////////////////////////////////////////////////////////////////////
        // sidebarVolumeMenu: getCookie('sidebarVolumeMenu') === 'false',
        // toggleSidebarVolumeMenu: () => {
        //     this.setState(prevState => {
        //         const newValue = !prevState.sidebarVolumeMenu;
        //         setCookie('sidebarVolumeMenu', newValue, 7);
        //         return {sidebarVolumeMenu: newValue};
        //     });
        // },
        ///////////////////////////////////////////////////////////////////////////////////
        // openMenuSW 是用 int 类型保存的可切换状态值，0 表示关闭，1 表示打开键盘菜单，2 表示打开鼠标滚轮菜单，3 表示打开音量菜单...
        openMenuSW: parseInt(getCookie('openMenuSW'), 10) || 0,
        setOpenMenuSW: (value) => {
            this.setState(
                {openMenuSW: value}, () =>
                    setCookie('openMenuSW', value, 7));
        },
        ///////////////////////////////////////////////////////////////////////////////////
        sidebarSettingMenu: getCookie('sidebarSettingMenu') === 'false',
        toggleSidebarSettingMenu: () => {
            this.setState(prevState => {
                const newValue = !prevState.sidebarSettingMenu;
                setCookie('sidebarSettingMenu', newValue, 7);
                return {sidebarSettingMenu: newValue};
            });
        },
        ///////////////////////////////////////////////////////////////////////////////////
        // keyboardDataSendMod 是用 char 类型保存的可切换状态值
        keyboardDataSendMod: getCookie('keyboardDataSendMod') || 'a',
        setKeyboardDataSendMod: (value) => {
            this.setState(
                {keyboardDataSendMod: value}, () => {
                    setCookie('keyboardDataSendMod', value, 7);
                    return {keyboardDataSendMod: value};
                }
            );
        },
        ///////////////////////////////////////////////////////////////////////////////////
    };

    componentDidMount() {
        // 从cookie初始化状态
        const buttonSW1 = getCookie('buttonSW1');
        const button23 = getCookie('button23');
        const buttonSW4 = getCookie('buttonSW4');
        const drawerRL = getCookie('drawerRL');
        const tPadSensitivity = getCookie('tPadSensitivity');
        const mWheelSensitivity = getCookie('mWheelSensitivity');
        // const sidebarMouseWheelMenu = getCookie('sidebarMouseWheelMenu');
        // const sidebarSettingMenu = getCookie('sidebarSettingMenu');
        // const sidebarVolumeMenu = getCookie('sidebarVolumeMenu');
        const openMenuSW = getCookie('openMenuSW');
        const sidebarKeyboardMenu = getCookie('sidebarKeyboardMenu');
        const keyboardDataSendMod = getCookie('keyboardDataSendMod');
        this.setState({
            buttonSW1: buttonSW1 ? buttonSW1 === 'true' : this.state.buttonSW1,
            button23: button23 ? parseInt(button23, 10) : this.state.button23,
            buttonSW4: buttonSW4 ? buttonSW4 === 'true' : this.state.buttonSW4,
            drawerRL: drawerRL || this.state.drawerRL,
            tPadSensitivity: tPadSensitivity ? parseFloat(tPadSensitivity) : this.state.tPadSensitivity,
            mWheelSensitivity: mWheelSensitivity ? parseFloat(mWheelSensitivity) : this.state.mWheelSensitivity,
            // sidebarMouseWheelMenu: sidebarMouseWheelMenu ? sidebarMouseWheelMenu === 'true' : this.state.sidebarMouseWheelMenu,
            // sidebarSettingMenu: sidebarSettingMenu ? sidebarSettingMenu === 'true' : this.state.sidebarSettingMenu,
            // sidebarVolumeMenu: sidebarVolumeMenu ? sidebarVolumeMenu === 'true' : this.state.sidebarVolumeMenu,
            openMenuSW: openMenuSW ? parseInt(openMenuSW, 10) : this.state.openMenuSW,
            sidebarKeyboardMenu: sidebarKeyboardMenu ? sidebarKeyboardMenu === 'true' : this.state.sidebarKeyboardMenu,
            keyboardDataSendMod: keyboardDataSendMod || this.state.keyboardDataSendMod,
        });
    }

    render() {
        return (
            <Context.Provider value={this.state}>
                {this.props.children}
            </Context.Provider>
        );
    }
}
