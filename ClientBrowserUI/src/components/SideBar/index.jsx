import React, {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    Drawer,
    List,
    ListItem,
    ListItemButton,
    Collapse,
    Box, Typography
} from "@mui/material";
import {
    ChevronRightOutlined,
    ExpandMore,
    Keyboard,
    Speaker,
    FilterTiltShift,
    Tune,
    ColorLensRounded,
    GTranslate,
    Settings
} from '@mui/icons-material';
import LayoutSettingMenu from './LayoutSettingMenu';
import MouseWheelMenu from './MouseWheelMenu';
import KeyboardMenu from './KeyboardMenu';
import VolumeMenu from './VolumeMenu';
import ThemeMenu from './ThemeMenu';
import LanguageMenu from './LanguageMenu';
import SettingMenu from './SettingMenu';
import i18n from '../../utils/i18n';

class SideBar extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        const MenuIndex = {
            AllClose: 0,
            LayoutSettingMenu: 1,
            KeyboardMenu: 2,
            MouseWheelMenu: 3,
            VolumeMenu: 4,
            ThemeMenu: 5,
            LanguageMenu: 6,
            SettingMenu: 7,
        };

        const textStyle = {
            fontSize: '1rem',
            fontWeight: 'bold',
        };

        let drawerWidth = '280px';
        let drawerPaperProps = {
            sx: {
                backgroundColor: this.context.primaryColor,
                color: this.context.secondaryColor,
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
                    backgroundColor: this.context.primaryColor,
                    color: this.context.secondaryColor,
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
                                    if (this.context.openMenuSW === MenuIndex.LayoutSettingMenu) {
                                        this.context.setOpenMenuSW(MenuIndex.AllClose);
                                    } else {
                                        this.context.setOpenMenuSW(MenuIndex.LayoutSettingMenu);
                                    }
                                } else {
                                    this.context.toggleSidebarLayoutSettingMenu();
                                }
                            }
                        }}>
                            <Tune sx={iconSizeSX}/>
                            <Typography style={textStyle}>
                                &nbsp;&nbsp;&nbsp;{i18n.Sidebar.index.LayoutSettings[this.context.i18n]}
                            </Typography>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === MenuIndex.LayoutSettingMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarLayoutSettingMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse
                        in={this.context.autoCollapse ? this.context.openMenuSW === MenuIndex.LayoutSettingMenu : this.context.sidebarLayoutSettingMenu}>
                        <LayoutSettingMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === MenuIndex.KeyboardMenu) {
                                        this.context.setOpenMenuSW(MenuIndex.AllClose);
                                    } else {
                                        this.context.setOpenMenuSW(MenuIndex.KeyboardMenu);
                                    }
                                } else {
                                    this.context.toggleSidebarKeyboardMenu();
                                }
                            }
                        }}>
                            <Keyboard sx={iconSizeSX}/>
                            <Typography style={textStyle}>
                                &nbsp;&nbsp;&nbsp;{i18n.Sidebar.index.Keyboard[this.context.i18n]}
                            </Typography>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === MenuIndex.KeyboardMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarKeyboardMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse
                        in={this.context.autoCollapse ? this.context.openMenuSW === MenuIndex.KeyboardMenu : this.context.sidebarKeyboardMenu}>
                        <KeyboardMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === MenuIndex.MouseWheelMenu) {
                                        this.context.setOpenMenuSW(MenuIndex.AllClose);
                                    } else {
                                        this.context.setOpenMenuSW(MenuIndex.MouseWheelMenu);
                                    }
                                } else {
                                    this.context.toggleSidebarMouseWheelMenu();
                                }
                            }
                        }}>
                            <FilterTiltShift sx={iconSizeSX}/>
                            <Typography style={textStyle}>
                                &nbsp;&nbsp;&nbsp;{i18n.Sidebar.index.MouseWheel[this.context.i18n]}
                            </Typography>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === MenuIndex.MouseWheelMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarMouseWheelMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse
                        in={this.context.autoCollapse ? this.context.openMenuSW === MenuIndex.MouseWheelMenu : this.context.sidebarMouseWheelMenu}>
                        <MouseWheelMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === MenuIndex.VolumeMenu) {
                                        this.context.setOpenMenuSW(MenuIndex.AllClose);
                                    } else {
                                        this.context.setOpenMenuSW(MenuIndex.VolumeMenu);
                                    }
                                } else {
                                    this.context.toggleSidebarVolumeMenu();
                                }
                            }
                        }}>
                            <Speaker sx={iconSizeSX}/>
                            <Typography style={textStyle}>
                                &nbsp;&nbsp;&nbsp;{i18n.Sidebar.index.Volume[this.context.i18n]}
                            </Typography>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === MenuIndex.VolumeMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarVolumeMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse
                        in={this.context.autoCollapse ? this.context.openMenuSW === MenuIndex.VolumeMenu : this.context.sidebarVolumeMenu}>
                        <VolumeMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === MenuIndex.ThemeMenu) {
                                        this.context.setOpenMenuSW(MenuIndex.AllClose);
                                    } else {
                                        this.context.setOpenMenuSW(MenuIndex.ThemeMenu);
                                    }
                                } else {
                                    this.context.toggleSidebarThemeMenu();
                                }
                            }
                        }}>
                            <ColorLensRounded sx={iconSizeSX}/>
                            <Typography style={textStyle}>
                                &nbsp;&nbsp;&nbsp;{i18n.Sidebar.index.ColorScheme[this.context.i18n]}
                            </Typography>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === MenuIndex.ThemeMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarThemeMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse
                        in={this.context.autoCollapse ? this.context.openMenuSW === MenuIndex.ThemeMenu : this.context.sidebarThemeMenu}>
                        <ThemeMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === MenuIndex.LanguageMenu) {
                                        this.context.setOpenMenuSW(MenuIndex.AllClose);
                                    } else {
                                        this.context.setOpenMenuSW(MenuIndex.LanguageMenu);
                                    }
                                } else {
                                    this.context.toggleSidebarLanguageMenu();
                                }
                            }
                        }}>
                            <GTranslate sx={iconSizeSX}/>
                            <Typography style={textStyle}>
                                &nbsp;&nbsp;&nbsp;{i18n.Sidebar.index.Language[this.context.i18n]}
                            </Typography>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === MenuIndex.LanguageMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarLanguageMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse
                        in={this.context.autoCollapse ? this.context.openMenuSW === MenuIndex.LanguageMenu : this.context.sidebarLanguageMenu}>
                        <LanguageMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            {
                                if (this.context.autoCollapse) {
                                    if (this.context.openMenuSW === MenuIndex.SettingMenu) {
                                        this.context.setOpenMenuSW(MenuIndex.AllClose);
                                    } else {
                                        this.context.setOpenMenuSW(MenuIndex.SettingMenu);
                                    }
                                } else {
                                    this.context.toggleSidebarSettingMenu();
                                }
                            }
                        }}>
                            <Settings sx={iconSizeSX}/>
                            <Typography style={textStyle}>
                                &nbsp;&nbsp;&nbsp;{i18n.Sidebar.index.AdvancedSettings[this.context.i18n]}
                            </Typography>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                this.context.openMenuSW === MenuIndex.SettingMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/> :
                                this.context.sidebarSettingMenu ?
                                    <ExpandMore sx={iconSizeSX}/> :
                                    <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <Collapse
                        in={this.context.autoCollapse ? this.context.openMenuSW === MenuIndex.SettingMenu : this.context.sidebarSettingMenu}>
                        <SettingMenu/>
                    </Collapse>
                </List>
            </Drawer>
        );
    }
}

SideBar.contextType = Context;

export default SideBar;
