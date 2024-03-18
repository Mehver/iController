import {Component} from 'react';
import GamepadIcon from '@mui/icons-material/Gamepad';
import MouseIcon from '@mui/icons-material/Mouse';
import TouchAppIcon from '@mui/icons-material/TouchApp';
// import {ThemeProvider} from '@mui/material/styles';
// import {customTheme} from '../utils/Theme';
import {Context} from '../utils/Context';
import {Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText} from "@mui/material";
import {EyeOutlined, EyeFilled, EyeInvisibleOutlined} from '@ant-design/icons';

class SideBar extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        let drawerWidth = 240;
        return (
            // <ThemeProvider theme={customTheme}>
            <Drawer
                anchor="left"
                open={this.context.drawerOpen}
                onClose={() => this.context.setDrawerOpen(false)}
                PaperProps={{
                    sx: {
                        backgroundColor: '#6df',
                        color: '#333',
                        width: drawerWidth,
                    },
                }}
            >

                <List
                    sx={{
                        width: drawerWidth,
                        padding: 0,
                    }}
                >
                    <ListItem>
                        <ListItemButton
                            onClick={() => {
                                this.context.toggleButtonSW1();
                            }}
                        >
                            <ListItemIcon>
                                <TouchAppIcon/>
                            </ListItemIcon>
                            <ListItemText primary="Touchpad"/>
                            {this.context.buttonSW1 ? <EyeOutlined/> : <EyeInvisibleOutlined/>}
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <ListItemButton
                            onClick={() => {
                                this.context.setButton23((this.context.button23 + 1) % 3);
                            }}
                        >
                            <ListItemIcon>
                                <MouseIcon/>
                            </ListItemIcon>
                            <ListItemText primary="Mouse Buttons"/>
                            {this.context.button23 === 0 ?
                                <EyeOutlined/> :
                                this.context.button23 === 1 ? <EyeFilled/> :
                                    <EyeInvisibleOutlined/>}
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <ListItemButton
                            onClick={() => {
                                this.context.toggleButtonSW4();
                            }}
                        >
                            <ListItemIcon>
                                <GamepadIcon/>
                            </ListItemIcon>
                            <ListItemText primary="D-Pad Buttons"/>
                            {this.context.buttonSW4 ? <EyeOutlined/> : <EyeInvisibleOutlined/>}
                        </ListItemButton>
                    </ListItem>

                </List>
            </Drawer>
            // </ThemeProvider>
        );
    }
}

SideBar.contextType = Context;

export default SideBar;
