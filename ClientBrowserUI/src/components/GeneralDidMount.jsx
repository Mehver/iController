import React, {Component} from 'react';
import {Context} from '../utils/Context';
import {
    setPrimaryColor as theme_setPrimaryColor,
    setSecondaryColor as theme_setSecondaryColor
} from '../utils/Theme';

class GeneralDidMount extends Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        theme_setPrimaryColor(this.context.primaryColor);
        theme_setSecondaryColor(this.context.secondaryColor);
        // 禁用页面滚动
        // 主要用于 Touchpad 组件
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
    }

    render() {
        return (<></>);
    }
}

GeneralDidMount.contextType = Context;

export default GeneralDidMount;
