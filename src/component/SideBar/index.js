import {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemText,
    Collapse,
    Box
} from "@mui/material";
import {
    ChevronRightOutlined,
    ExpandMore,
    Keyboard,
    Speaker,
    FilterTiltShift,
    Tune,
    Settings
} from '@mui/icons-material';
import {primaryColor, secondaryColor} from '../../utils/Theme';
import ModulesSettingMenu from './ModulesSettingMenu';
import MouseWheelMenu from './MouseWheelMenu';
import KeyboardMenu from './KeyboardMenu';
import VolumeMenu from './VolumeMenu';
import SettingMenu from './SettingMenu';

class SideBar extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        let drawerWidth = '280px';
        let drawerPaperProps = {
            sx: {
                backgroundColor: primaryColor,
                color: secondaryColor,
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
                    backgroundColor: primaryColor,
                    color: secondaryColor,
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
                anchor={this.context.drawerRL === 'r' ? 'right' : 'left'}
                open={this.context.drawerOpen}
                onClose={() => this.context.setDrawerOpen(false)}
                PaperProps={drawerPaperProps}
            >
                <List sx={listSX}>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.sidebarModulesSettingMenu === 1) {
                                        this.context.setOpenMenuSW(0);
                                    } else {
                                        this.context.setOpenMenuSW(1);
                                    }
                                } else {
                                    this.context.toggleSidebarModulesSettingMenu();
                                }
                            }
                        }}>
                            <Tune sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Modules Settings"/>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === 1 ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarModulesSettingMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse in={this.context.autoCollapse ? this.context.openMenuSW === 1 : this.context.sidebarModulesSettingMenu}>
                        <ModulesSettingMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === 2) {
                                        this.context.setOpenMenuSW(0);
                                    } else {
                                        this.context.setOpenMenuSW(2);
                                    }
                                } else {
                                    this.context.toggleSidebarKeyboardMenu();
                                }
                            }
                        }}>
                            <Keyboard sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Keyboard"/>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === 2 ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarKeyboardMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse in={this.context.autoCollapse ? this.context.openMenuSW === 2 : this.context.sidebarKeyboardMenu}>
                        <KeyboardMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === 3) {
                                        this.context.setOpenMenuSW(0);
                                    } else {
                                        this.context.setOpenMenuSW(3);
                                    }
                                } else {
                                    this.context.toggleSidebarMouseWheelMenu();
                                }
                            }
                        }}>
                            <FilterTiltShift sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Mouse Wheel"/>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === 3 ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarMouseWheelMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse in={this.context.autoCollapse ? this.context.openMenuSW === 3 : this.context.sidebarMouseWheelMenu}>
                        <MouseWheelMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === 4) {
                                        this.context.setOpenMenuSW(0);
                                    } else {
                                        this.context.setOpenMenuSW(4);
                                    }
                                } else {
                                    this.context.toggleSidebarVolumeMenu();
                                }
                            }
                        }}>
                            <Speaker sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Volume"/>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === 4 ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarVolumeMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse in={this.context.autoCollapse ? this.context.openMenuSW === 4 : this.context.sidebarVolumeMenu}>
                        <VolumeMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === 5) {
                                        this.context.setOpenMenuSW(0);
                                    } else {
                                        this.context.setOpenMenuSW(5);
                                    }
                                } else {
                                    this.context.toggleSidebarSettingMenu();
                                }
                            }
                        }}>
                            <Settings sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Advanced Settings"/>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === 5?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarSettingMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse in={this.context.autoCollapse ? this.context.openMenuSW === 5 : this.context.sidebarSettingMenu}>
                        <SettingMenu/>
                    </Collapse>
                </List>
            </Drawer>
        );
    }
}

SideBar.contextType = Context;

export default SideBar;
