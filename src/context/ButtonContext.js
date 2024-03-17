// ButtonContext.js
import React, {createContext, Component} from 'react';

// 创建Context
export const ButtonContext = createContext();

// 创建Provider组件
export class ButtonProvider extends Component {
    state = {
        buttonSW1: true,
        button23: 0,
        buttonSW4: false,
        toggleButtonSW1: () => {
            this.setState(prevState => ({buttonSW1: !prevState.buttonSW1}));
        },
        setButton23: (value) => {
            this.setState({button23: value});
        },
        toggleButtonSW4: () => {
            this.setState(prevState => ({buttonSW4: !prevState.buttonSW4}));
        },
    };

    render() {
        return (
            <ButtonContext.Provider value={this.state}>
                {this.props.children}
            </ButtonContext.Provider>
        );
    }
}
