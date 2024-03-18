// Context.js
import React, {createContext, Component} from 'react';
import {setCookie, getCookie} from './CookieIO';

// 创建Context
export const Context = createContext();

// 创建Provider组件
export class ButtonProvider extends Component {
    state = {
        buttonSW1: getCookie('buttonSW1') === 'false',
        button23: parseInt(getCookie('button23'), 10) || 0,
        buttonSW4: getCookie('buttonSW4') === 'true',
        drawerOpen: false,
        setDrawerOpen: (value) => {
            this.setState({drawerOpen: value});
        },
        toggleButtonSW1: () => {
            // this.setState(prevState => ({buttonSW1: !prevState.buttonSW1}));
            this.setState(prevState => {
                const newValue = !prevState.buttonSW1;
                setCookie('buttonSW1', newValue, 7); // 保存7天
                return {buttonSW1: newValue};
            });
        },
        setButton23: (value) => {
            // this.setState({button23: value});
            this.setState({button23: value}, () => setCookie('button23', value, 7));
        },
        toggleButtonSW4: () => {
            // this.setState(prevState => ({buttonSW4: !prevState.buttonSW4}));
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
        this.setState({
            buttonSW1: buttonSW1 ? buttonSW1 === 'true' : this.state.buttonSW1,
            button23: button23 ? parseInt(button23, 10) : this.state.button23,
            buttonSW4: buttonSW4 ? buttonSW4 === 'true' : this.state.buttonSW4,
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
