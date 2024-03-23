import {Component} from 'react';
import GamepadIcon from '@mui/icons-material/Gamepad';
import MouseIcon from '@mui/icons-material/Mouse';
import TouchAppIcon from '@mui/icons-material/TouchApp';
import {Context} from '../utils/Context';
import {Drawer, List, ListItem, ListItemButton, ListItemText, Switch, Box} from "@mui/material";
import {styled} from '@mui/material/styles';
import LooksOneOutlinedIcon from '@mui/icons-material/LooksOneOutlined';
import LooksTwoOutlinedIcon from '@mui/icons-material/LooksTwoOutlined';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import VisibilityOffOutlinedIcon from '@mui/icons-material/VisibilityOffOutlined';

class SideBar extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        let drawerWidth = '280px';
        let drawerPaperProps = {
            sx: {
                backgroundColor: '#6df',
                color: '#333',
                width: drawerWidth,
            },
        };
        let listSX = {
            width: drawerWidth,
            padding: 0,
        };
        let iconSizeSX = {};
        let boxIconSX = {};
        if (window.innerWidth < 280) {
            const fontSize = window.innerWidth / 300.0;
            drawerWidth = '80%';
            listSX = {
                width: drawerWidth,
                padding: 0,
                '& .MuiSwitch-sizeSmall': {
                    transform: 'scale(0.8)',
                },
            };
            drawerPaperProps = {
                sx: {
                    backgroundColor: '#6df',
                    color: '#333',
                    width: drawerWidth,
                    // 调整字体和图标大小
                    '& .MuiListItemIcon-root': {
                        fontSize: `${fontSize}rem`,
                    },
                    '& .MuiListItemText-primary': {
                        fontSize: `${fontSize}rem`,
                    },
                },
            };
            iconSizeSX.fontSize = `${fontSize}rem`;
            boxIconSX.marginRight = '-50px';
        }
        return (
            <Drawer
                anchor="left"
                open={this.context.drawerOpen}
                onClose={() => this.context.setDrawerOpen(false)}
                PaperProps={drawerPaperProps}
            >
                <List sx={listSX}>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleButtonSW1();
                        }}>

                            <TouchAppIcon sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Touchpad"/>
                            <Box sx={boxIconSX}>{this.context.buttonSW1 ?
                                <VisibilityOutlinedIcon sx={iconSizeSX}/> :
                                <VisibilityOffOutlinedIcon sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleButtonSW4();
                        }}>
                            <GamepadIcon sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;D-Pad"/>
                            <Box sx={boxIconSX}>{this.context.buttonSW4 ?
                                <VisibilityOutlinedIcon sx={iconSizeSX}/> :
                                <VisibilityOffOutlinedIcon sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.setButton23((this.context.button23 + 1) % 3);
                        }}>
                            <MouseIcon sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Mouse Buttons"/>
                            <Box sx={boxIconSX}>{this.context.button23 === 0 ?
                                <LooksOneOutlinedIcon sx={iconSizeSX}/> :
                                this.context.button23 === 1 ?
                                    <LooksTwoOutlinedIcon sx={iconSizeSX}/> :
                                    <VisibilityOffOutlinedIcon sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                </List>
            </Drawer>
        );
    }
}

SideBar.contextType = Context;

export default SideBar;
