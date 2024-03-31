import {Component} from 'react';
import {Context} from '../utils/Context';
import {Drawer, List, ListItem, ListItemButton, ListItemText, Collapse, Box, Divider} from "@mui/material";
import LooksOneOutlinedIcon from '@mui/icons-material/LooksOneOutlined';
import LooksTwoOutlinedIcon from '@mui/icons-material/LooksTwoOutlined';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import MouseIcon from '@mui/icons-material/Mouse';
import VisibilityOffOutlinedIcon from '@mui/icons-material/VisibilityOffOutlined';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronRightOutlinedIcon from '@mui/icons-material/ChevronRightOutlined';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import KeyboardIcon from '@mui/icons-material/Keyboard';
import SpeakerIcon from '@mui/icons-material/Speaker';
import FilterTiltShiftIcon from '@mui/icons-material/FilterTiltShift';
import OpenWithIcon from '@mui/icons-material/OpenWith';
import PinchIcon from '@mui/icons-material/Pinch';
import MouseWheelMenu from './SideBar/MouseWheelMenu';
import KeyboardMenu from './SideBar/KeyboardMenu';
import SoundWheel from './SideBar/SoundWheel';
import SettingMenu from './SideBar/SettingMenu';

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

                            <PinchIcon sx={iconSizeSX}/>
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
                            <OpenWithIcon sx={iconSizeSX}/>
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
                    <Divider/>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleSidebarKeyboardMenu();
                        }}>
                            <KeyboardIcon sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Keyboard"/>
                            <Box sx={boxIconSX}>{this.context.sidebarKeyboardMenu ?
                                <ExpandMoreIcon sx={iconSizeSX}/> :
                                <ChevronRightOutlinedIcon sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse in={this.context.sidebarKeyboardMenu}>
                        <KeyboardMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleSidebarMouseWheelMenu();
                        }}>
                            <FilterTiltShiftIcon sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Mouse Wheel"/>
                            <Box sx={boxIconSX}>{this.context.sidebarMouseWheelMenu ?
                                <ExpandMoreIcon sx={iconSizeSX}/> :
                                <ChevronRightOutlinedIcon sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse in={this.context.sidebarMouseWheelMenu}>
                        <MouseWheelMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleSidebarSoundWheelMenu();
                        }}>
                            <SpeakerIcon sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Sound Wheel"/>
                            <Box sx={boxIconSX}>{this.context.sidebarSoundWheelMenu ?
                                <ExpandMoreIcon sx={iconSizeSX}/> :
                                <ChevronRightOutlinedIcon sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse in={this.context.sidebarSoundWheelMenu}>
                        <SoundWheel/>
                    </Collapse>
                    <Divider/>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleSidebarSettingMenu();
                        }}>
                            <MenuIcon sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Settings"/>
                            <Box sx={boxIconSX}>{this.context.sidebarSettingMenu ?
                                <ExpandMoreIcon sx={iconSizeSX}/> :
                                <ChevronRightOutlinedIcon sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse in={this.context.sidebarSettingMenu}>
                        <SettingMenu/>
                    </Collapse>
                </List>
            </Drawer>
        );
    }
}

SideBar.contextType = Context;

export default SideBar;
