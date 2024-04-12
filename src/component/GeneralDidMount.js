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
    }

    render() {
        return (<></>);
    }
}

GeneralDidMount.contextType = Context;

export default GeneralDidMount;
