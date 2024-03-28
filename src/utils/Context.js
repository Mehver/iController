// Context.js
import React, {createContext, Component} from 'react';
import {setCookie, getCookie} from '../storage/CookieIO';

// 创建Context
export const Context = createContext();

// 创建Provider组件
export class ButtonProvider extends Component {
    state = {
        buttonSW1: getCookie('buttonSW1') === 'false',
        button23: parseInt(getCookie('button23'), 10) || 0,
        buttonSW4: getCookie('buttonSW4') === 'true',
        sidebarMouseWheelMenu: getCookie('sidebarMouseWheelMenu') === 'false',
        sidebarSoundWheelMenu: getCookie('sidebarMouseWheelMenu') === 'false',
        sidebarSettingMenu: getCookie('sidebarMouseWheelMenu') === 'false',
        sidebarKeyboardMenu: getCookie('sidebarMouseWheelMenu') === 'false',
        drawerOpen: false,
        setDrawerOpen: (value) => {
            this.setState({drawerOpen: value});
        },
        toggleSidebarMouseWheelMenu: () => {
            this.setState(prevState => {
                const newValue = !prevState.sidebarMouseWheelMenu;
                setCookie('sidebarMouseWheelMenu', newValue, 7); // 保存7天
                return {sidebarMouseWheelMenu: newValue};
            });
        },
        toggleSidebarKeyboardMenu: () => {
            this.setState(prevState => {
                const newValue = !prevState.sidebarKeyboardMenu;
                setCookie('sidebarKeyboardMenu', newValue, 7); // 保存7天
                return {sidebarKeyboardMenu: newValue};
            });
        },
        toggleSidebarSoundWheelMenu: () => {
            this.setState(prevState => {
                const newValue = !prevState.sidebarSoundWheelMenu;
                setCookie('sidebarSoundWheelMenu', newValue, 7); // 保存7天
                return {sidebarSoundWheelMenu: newValue};
            });
        },
        toggleSidebarSettingMenu: () => {
            this.setState(prevState => {
                const newValue = !prevState.sidebarSettingMenu;
                setCookie('sidebarSettingMenu', newValue, 7); // 保存7天
                return {sidebarSettingMenu: newValue};
            });
        },
        toggleButtonSW1: () => {
            this.setState(prevState => {
                const newValue = !prevState.buttonSW1;
                setCookie('buttonSW1', newValue, 7); // 保存7天
                return {buttonSW1: newValue};
            });
        },
        setButton23: (value) => {
            this.setState(
                {button23: value}, () =>
                    setCookie('button23', value, 7));
        },
        toggleButtonSW4: () => {
            this.setState(prevState => {
                const newValue = !prevState.buttonSW4;
                setCookie('buttonSW4', newValue, 7); // 保存7天
                return {buttonSW4: newValue};
            });
        },
    };

    componentDidMount() {
        // 从cookie初始化状态
        const buttonSW1 = getCookie('buttonSW1');
        const button23 = getCookie('button23');
        const buttonSW4 = getCookie('buttonSW4');
        const sidebarMouseWheelMenu = getCookie('sidebarMouseWheelMenu');
        const sidebarSettingMenu = getCookie('sidebarSettingMenu');
        const sidebarSoundWheelMenu = getCookie('sidebarSoundWheelMenu');
        const sidebarKeyboardMenu = getCookie('sidebarKeyboardMenu');
        this.setState({
            buttonSW1: buttonSW1 ? buttonSW1 === 'true' : this.state.buttonSW1,
            button23: button23 ? parseInt(button23, 10) : this.state.button23,
            buttonSW4: buttonSW4 ? buttonSW4 === 'true' : this.state.buttonSW4,
            sidebarMouseWheelMenu: sidebarMouseWheelMenu ? sidebarMouseWheelMenu === 'true' : this.state.sidebarMouseWheelMenu,
            sidebarSettingMenu: sidebarSettingMenu ? sidebarSettingMenu === 'true' : this.state.sidebarSettingMenu,
            sidebarSoundWheelMenu: sidebarSoundWheelMenu ? sidebarSoundWheelMenu === 'true' : this.state.sidebarSoundWheelMenu,
            sidebarKeyboardMenu: sidebarKeyboardMenu ? sidebarKeyboardMenu === 'true' : this.state.sidebarKeyboardMenu,
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
