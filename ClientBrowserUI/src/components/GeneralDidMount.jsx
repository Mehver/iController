import React, {Component} from 'react';
import {Context} from '../utils/Context';
import {updateColorCSS} from '../utils/Theme';

class GeneralDidMount extends Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        updateColorCSS(this.context.primaryColor, this.context.secondaryColor);
        // 禁用页面滚动
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
    }

    render() {
        return (<></>);
    }
}

GeneralDidMount.contextType = Context;

export default GeneralDidMount;
