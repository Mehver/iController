// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import React, {Component} from 'react';
import {Context} from '../utils/Context';
import {updateColorCSS} from '../utils/Theme';
import {AppContextType} from '../types';

class GeneralDidMount extends Component {
    static contextType = Context;
    declare context: AppContextType;

    componentDidMount() {
        updateColorCSS(this.context.primaryColor, this.context.secondaryColor);
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
    }

    render() {
        return (<></>);
    }
}

export default GeneralDidMount;
