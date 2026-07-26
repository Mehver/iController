// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import {Component} from 'react';
import {Context} from '../../utils/Context';
import {AppContextType} from '../../types';
import DPad from "./DPad";
import MouseButtons from "./MouseButtons";
import Touchpad from "./Touchpad";

class Screen extends Component {
    static contextType = Context;
    declare context: AppContextType;

    render() {
        return (
            <>
                <Touchpad/>
                <DPad/>
                <MouseButtons/>
            </>
        );
    }
}

export default Screen;
