import {Component} from 'react';
import {Context} from '../../utils/Context';
import {List, ListItemButton, ListItemText} from "@mui/material";

class KeyboardMenu extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <List component="div" disablePadding>
                <ListItemButton sx={{pl: 4}}>
                    <ListItemText primary="KeyboardMenu"/>
                </ListItemButton>
            </List>
        );
    }
}

KeyboardMenu.contextType = Context;

export default KeyboardMenu;
