import React, {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    List,
    ListItem,
    ListItemButton,
    Box,
    ListItemText,
    Divider,
    SvgIcon
} from "@mui/material";
import {
    LooksOneOutlined,
    LooksTwoOutlined,
    Looks3Outlined,
    Mouse,
    OpenWith,
    Pinch,
    VisibilityOffOutlined,
    VisibilityOutlined
} from '@mui/icons-material';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import i18n from '../../utils/i18n';

class LayoutSettingMenu extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        let iconSizeSX = {
            marginRight: '20px',
        };
        let boxIconSX = {};
        if (window.innerWidth < 280) {
            const fontSize = window.innerWidth / 300.0;
            iconSizeSX.fontSize = `${fontSize}rem`;
            boxIconSX.marginRight = '-50px';
        }

        let customTheme = createTheme({
            palette: {
                primary: {
                    main: this.context.primaryColor,
                },
                secondary: {
                    main: this.context.secondaryColor,
                },
            },
        });

        return (
            <ThemeProvider theme={customTheme}>
                <List component="div" disablePadding>

                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleButtonSW1();
                        }}>

                            <Pinch sx={iconSizeSX}/>
                            <ListItemText primary={i18n.Sidebar.LayoutSettingMenu.Touchpad[this.context.i18n]}/>
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
                            <ListItemText primary={i18n.Sidebar.LayoutSettingMenu.DPad[this.context.i18n]}/>
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
                            <ListItemText primary={i18n.Sidebar.LayoutSettingMenu.MouseButtons[this.context.i18n]}/>
                            <Box sx={boxIconSX}>{this.context.button23 === 0 ?
                                <LooksOneOutlined sx={iconSizeSX}/> :
                                this.context.button23 === 1 ?
                                    <LooksTwoOutlined sx={iconSizeSX}/> :
                                    <VisibilityOffOutlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.setMouseWheelMenuType((this.context.mouseWheelMenuType + 1) % 3);
                        }}>
                            <SvgIcon sx={iconSizeSX} style={{color: 'transparent'}}/>
                            <ListItemText primary={i18n.Sidebar.LayoutSettingMenu.MouseWheel[this.context.i18n]}/>
                            <Box sx={boxIconSX}>{this.context.mouseWheelMenuType === 0 ?
                                <LooksOneOutlined sx={iconSizeSX}/> :
                                this.context.mouseWheelMenuType === 1 ?
                                    <LooksTwoOutlined sx={iconSizeSX}/> :
                                    <Looks3Outlined sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                </List>
                <Divider/>
            </ThemeProvider>
        );
    }
}

LayoutSettingMenu.contextType = Context;

export default LayoutSettingMenu;
