import {Component} from 'react';
import GamepadIcon from '@mui/icons-material/Gamepad';
import MouseIcon from '@mui/icons-material/Mouse';
import TouchAppIcon from '@mui/icons-material/TouchApp';
import {Context} from '../utils/Context';
import {Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Switch} from "@mui/material";
import LooksOneOutlinedIcon from '@mui/icons-material/LooksOneOutlined';
import LooksTwoOutlinedIcon from '@mui/icons-material/LooksTwoOutlined';
import VisibilityOffOutlinedIcon from '@mui/icons-material/VisibilityOffOutlined';

class SideBar extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        let drawerWidth = 280;
        const drawerPaperProps = {
            sx: {
                backgroundColor: '#6df',
                color: '#333',
                width: drawerWidth,
            },
        };
        return (
            <Drawer
                anchor="left"
                open={this.context.drawerOpen}
                onClose={() => this.context.setDrawerOpen(false)}
                PaperProps={drawerPaperProps}
            >
                <List sx={{
                    width: drawerWidth,
                    padding: 0,
                }}>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleButtonSW1();
                        }}>
                            <ListItemIcon>
                                <TouchAppIcon/>
                            </ListItemIcon>
                            <ListItemText primary="Touchpad"/>
                            <Switch checked={this.context.buttonSW1} color="primary"/>
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.setButton23((this.context.button23 + 1) % 3);
                        }}>
                            <ListItemIcon>
                                <MouseIcon/>
                            </ListItemIcon>
                            <ListItemText primary="Mouse Buttons"/>
                            {this.context.button23 === 0 ?
                                <LooksOneOutlinedIcon/> :
                                this.context.button23 === 1 ? <LooksTwoOutlinedIcon/> :
                                    <VisibilityOffOutlinedIcon/>}
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <ListItemButton onClick={() => {
                            this.context.toggleButtonSW4();
                        }}>
                            <ListItemIcon>
                                <GamepadIcon/>
                            </ListItemIcon>
                            <ListItemText primary="D-Pad"/>
                            <Switch checked={this.context.buttonSW4} color="primary"/>
                        </ListItemButton>
                    </ListItem>

                </List>
            </Drawer>
        );
    }
}

SideBar.contextType = Context;

export default SideBar;
