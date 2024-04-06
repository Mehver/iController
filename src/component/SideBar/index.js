import {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemText,
    Collapse,
    Box,
    Divider
} from "@mui/material";
import {
    LooksOneOutlined,
    LooksTwoOutlined,
    VisibilityOutlined,
    Mouse,
    VisibilityOffOutlined,
    Menu,
    ChevronRightOutlined,
    ExpandMore,
    Keyboard,
    Speaker,
    FilterTiltShift,
    OpenWith,
    Pinch,
    FormatAlignLeftOutlined,
    FormatAlignRightOutlined,
    ViewCarousel
} from '@mui/icons-material';
import {ThemeProvider} from '@mui/material/styles';
import {customTheme} from '../../utils/Theme';
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
                anchor={this.context.drawerRL === 'r' ? 'right' : 'left'}
                open={this.context.drawerOpen}
                onClose={() => this.context.setDrawerOpen(false)}
                PaperProps={drawerPaperProps}
            >
                <List sx={listSX}>
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
                    <Divider/>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            // this.context.toggleSidebarKeyboardMenu();
                            {if (this.context.openMenuSW === 1) {
                                this.context.setOpenMenuSW(0);
                            } else {
                                this.context.setOpenMenuSW(1);
                            }}
                        }}>
                            <Keyboard sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Keyboard"/>
                            {/*<Box sx={boxIconSX}>{this.context.sidebarKeyboardMenu ?*/}
                            {/*    <ExpandMore sx={iconSizeSX}/> :*/}
                            {/*    <ChevronRightOutlined sx={iconSizeSX}/>*/}
                            {/*}</Box>*/}
                            <Box sx={boxIconSX}>{this.context.openMenuSW === 1 ?
                                <ExpandMore sx={iconSizeSX}/> :
                                <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    {/*<Collapse in={this.context.sidebarKeyboardMenu}>*/}
                    <Collapse in={this.context.openMenuSW === 1}>
                        <KeyboardMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            // this.context.toggleSidebarMouseWheelMenu();
                            {if (this.context.openMenuSW === 2) {
                                this.context.setOpenMenuSW(0);
                            } else {
                                this.context.setOpenMenuSW(2);
                            }}
                        }}>
                            <FilterTiltShift sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Mouse Wheel"/>
                            {/*<Box sx={boxIconSX}>{this.context.sidebarMouseWheelMenu ?*/}
                            {/*    <ExpandMore sx={iconSizeSX}/> :*/}
                            {/*    <ChevronRightOutlined sx={iconSizeSX}/>*/}
                            {/*}</Box>*/}
                            <Box sx={boxIconSX}>{this.context.openMenuSW === 2 ?
                                <ExpandMore sx={iconSizeSX}/> :
                                <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    {/*<Collapse in={this.context.sidebarMouseWheelMenu}>*/}
                    <Collapse in={this.context.openMenuSW === 2}>
                        <MouseWheelMenu/>
                    </Collapse>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            // this.context.toggleSidebarVolumeMenu();
                            {if (this.context.openMenuSW === 3) {
                                this.context.setOpenMenuSW(0);
                            } else {
                                this.context.setOpenMenuSW(3);
                            }}
                        }}>
                            <Speaker sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Volume"/>
                            {/*<Box sx={boxIconSX}>{this.context.sidebarVolumeMenu ?*/}
                            {/*    <ExpandMore sx={iconSizeSX}/> :*/}
                            {/*    <ChevronRightOutlined sx={iconSizeSX}/>*/}
                            {/*}</Box>*/}
                            <Box sx={boxIconSX}>{this.context.openMenuSW === 3 ?
                                <ExpandMore sx={iconSizeSX}/> :
                                <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    {/*<Collapse in={this.context.sidebarVolumeMenu}>*/}
                    <Collapse in={this.context.openMenuSW === 3}>
                        <VolumeMenu/>
                    </Collapse>
                    {/*<Divider/>*/}
                    <ListItem>
                        <ListItemButton onClick={() => {
                            // this.context.toggleSidebarSettingMenu();
                            {if (this.context.openMenuSW === 4) {
                                this.context.setOpenMenuSW(0);
                            } else {
                                this.context.setOpenMenuSW(4);
                            }}
                        }}>
                            <Menu sx={iconSizeSX}/>
                            <ListItemText primary="&nbsp;&nbsp;&nbsp;Settings"/>
                            {/*<Box sx={boxIconSX}>{this.context.sidebarSettingMenu ?*/}
                            {/*    <ExpandMore sx={iconSizeSX}/> :*/}
                            {/*    <ChevronRightOutlined sx={iconSizeSX}/>*/}
                            {/*}</Box>*/}
                            <Box sx={boxIconSX}>{this.context.openMenuSW === 4 ?
                                <ExpandMore sx={iconSizeSX}/> :
                                <ChevronRightOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    {/*<Collapse in={this.context.sidebarSettingMenu}>*/}
                    <Collapse in={this.context.openMenuSW === 4}>
                        <ThemeProvider theme={customTheme}>
                            <List component="div" disablePadding>
                                <ListItem>
                                    <ListItemButton onClick={() => {
                                        this.context.setDrawerRL(this.context.drawerRL === 'r' ? 'l' : 'r');
                                    }}>
                                        <ViewCarousel sx={iconSizeSX}/>
                                        <ListItemText primary="&nbsp;&nbsp;&nbsp;Sidebar Toggle"/>
                                        <Box sx={boxIconSX}>
                                            {this.context.drawerRL === 'r' ?
                                                <FormatAlignRightOutlined sx={iconSizeSX}/> :
                                                <FormatAlignLeftOutlined sx={iconSizeSX}/>
                                            }
                                        </Box>
                                    </ListItemButton>
                                </ListItem>
                                {/*<Divider/>*/}
                                <SettingMenu/>
                            </List>
                        </ThemeProvider>
                    </Collapse>
                </List>
            </Drawer>
        );
    }
}

SideBar.contextType = Context;

export default SideBar;
