import {Component} from 'react';
import {Context} from '../../utils/Context';
import {List, ListItemButton, ListItemText} from "@mui/material";

class SoundWheel extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <List component="div" disablePadding>
                <ListItemButton sx={{pl: 4}}>
                    <ListItemText primary="SoundWheelMenu"/>
                </ListItemButton>
            </List>
        );
    }
}

SoundWheel.contextType = Context;

export default SoundWheel;
