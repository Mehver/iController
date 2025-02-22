import {Component} from 'react';
import {Context} from '../../utils/Context';
import DPad from "./DPad";
import MouseButtons from "./MouseButtons";
import Touchpad from "./Touchpad";

class Screen extends Component {
    constructor(props) {
        super(props);
    }

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

Screen.contextType = Context;

export default Screen;
