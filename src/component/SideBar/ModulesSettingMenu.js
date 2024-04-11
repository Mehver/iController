import React, {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    List,
    ListItem,
    ListItemButton,
    Box, ListItemText
} from "@mui/material";
import {
    LooksOneOutlined,
    LooksTwoOutlined,
    Mouse,
    OpenWith,
    Pinch,
    VisibilityOffOutlined,
    VisibilityOutlined
} from '@mui/icons-material';
import {ThemeProvider} from '@mui/material/styles';
import {
    customTheme
} from '../../utils/Theme';

class ModuleSettingMenu extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        let iconSizeSX = {};
        let boxIconSX = {};
        if (window.innerWidth < 280) {
            const fontSize = window.innerWidth / 300.0;
            iconSizeSX.fontSize = `${fontSize}rem`;
            boxIconSX.marginRight = '-50px';
        }
        return (
            <ThemeProvider theme={customTheme}>
                <List component="div" disablePadding>

                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleButtonSW1();
                        }}>

                            <Pinch sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Touchpad"/>
                            <Box sx={boxIconSX}>{this.context.buttonSW1 ?
                                <VisibilityOutlined sx={iconSizeSX}/> :
                                <VisibilityOffOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleButtonSW4();
                        }}>
                            <OpenWith sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;D-Pad"/>
                            <Box sx={boxIconSX}>{this.context.buttonSW4 ?
                                <VisibilityOutlined sx={iconSizeSX}/> :
                                <VisibilityOffOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.setButton23((this.context.button23 + 1) % 3);
                        }}>
                            <Mouse sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Mouse Buttons"/>
                            <Box sx={boxIconSX}>{this.context.button23 === 0 ?
                                <LooksOneOutlined sx={iconSizeSX}/> :
                                this.context.button23 === 1 ?
                                    <LooksTwoOutlined sx={iconSizeSX}/> :
                                    <VisibilityOffOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                </List>
            </ThemeProvider>
        );
    }
}

ModuleSettingMenu.contextType = Context;

export default ModuleSettingMenu;
