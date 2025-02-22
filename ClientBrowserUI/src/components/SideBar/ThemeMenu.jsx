import React, {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    List,
    ListItem,
    Typography,
    Divider
} from "@mui/material";
import {
    HuePicker,
    TwitterPicker
} from 'react-color';
import {defaultPrimaryColor,defaultSecondaryColor,updateColorCSS} from '../../utils/Theme';

class ThemeMenu extends Component {
    constructor(props) {
        super(props);
    }

    handlePrimaryColorChange = (color) => {
        this.context.setPrimaryColor(color.hex);
        updateColorCSS(color.hex, this.context.secondaryColor);
    }

    handleSecondaryColorChange = (color) => {
        this.context.setSecondaryColor(color.hex);
        updateColorCSS(this.context.primaryColor, color.hex);
    }

    render() {
        return (
            <>
                <List
                    component="div"
                    disablePadding
                >
                    <ListItem>
                        <Typography style={{fontSize: '1rem'}}>Primary Color</Typography>
                        <div style={{flex: 1}}/>
                    </ListItem>
                    <ListItem>
                        <HuePicker
                            color="primary"
                            onChangeComplete={(color) => {
                                this.handlePrimaryColorChange(color);
                            }}
                        />
                    </ListItem>
                    <ListItem>
                        <TwitterPicker
                            color="primary"
                            colors={[
                                defaultPrimaryColor,
                                defaultSecondaryColor,
                                '#FFFFFF',
                                '#000000',
                                '#ABB8C3',
                                '#0693E3',
                                '#FCB900',
                                '#9900EF',
                                '#7BDCB5',
                                '#F78DA7',
                                '#00D084',
                                '#EB144C',
                            ]}
                            onSwatchHover={(color) => {
                                this.handlePrimaryColorChange(color);
                            }}
                        />
                    </ListItem>
                    <ListItem>
                        <Typography style={{fontSize: '1rem'}}>Secondary Color</Typography>
                        <div style={{flex: 1}}/>
                    </ListItem>
                    <ListItem>
                        <HuePicker
                            color={this.context.secondaryColor}
                            onChangeComplete={(color) => {
                                this.handleSecondaryColorChange(color);
                            }}
                        />
                    </ListItem>
                    <ListItem>
                        <TwitterPicker
                            color={this.context.secondaryColor}
                            colors={[
                                defaultSecondaryColor,
                                defaultPrimaryColor,
                                '#000000',
                                '#FFFFFF',
                                '#0693E3',
                                '#ABB8C3',
                                '#9900EF',
                                '#FCB900',
                                '#F78DA7',
                                '#7BDCB5',
                                '#EB144C',
                                '#00D084',
                            ]}
                            onSwatchHover={(color) => {
                                this.handleSecondaryColorChange(color);
                            }}
                        />
                    </ListItem>
                </List>
                <Divider/>
            </>
        );
    }
}

ThemeMenu.contextType = Context;

export default ThemeMenu;
