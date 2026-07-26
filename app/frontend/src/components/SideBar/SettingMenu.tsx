// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import React, {Component} from 'react';
import {Context} from '../../utils/Context';
import {
    List,
    ListItem,
    TextField,
    Radio,
    RadioGroup,
    FormControlLabel,
    FormControl,
    Typography,
    ListItemButton,
    Box
} from "@mui/material";
import {
    CheckBoxOutlineBlankRounded,
    CheckBoxRounded
} from '@mui/icons-material';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import i18n from '../../utils/i18n';
import {AppContextType} from '../../types';

interface SettingMenuState {
    drawerSide: string;
    tPadSensitivity: string;
    mWheelSensitivity: string;
}

class SettingMenu extends Component<object, SettingMenuState> {
    static contextType = Context;
    declare context: AppContextType;

    constructor(props: object) {
        super(props);
        this.state = {
            drawerSide: 'l',
            tPadSensitivity: '',
            mWheelSensitivity: '',
        };
    }

    componentDidMount() {
        this.setState({
            drawerSide: this.context.drawerRL,
            tPadSensitivity: this.context.tPadSensitivity.toString(),
            mWheelSensitivity: this.context.mWheelSensitivity.toString(),
        });
    }

    handleRadioChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        this.setState({drawerSide: event.target.value});
        this.context.setDrawerRL(event.target.value);
    };

    handleTextFieldChange = (event: React.ChangeEvent<HTMLInputElement>, type: string) => {
        this.setState({[type]: event.target.value} as unknown as Pick<SettingMenuState, keyof SettingMenuState>);
    };

    handleBlur = (type: string) => {
        const value = this.state[type as keyof SettingMenuState];
        const numValue = parseFloat(value);
        if (!isNaN(numValue) && numValue > 0) {
            if (type === 'tPadSensitivity') {
                this.context.setTPadSensitivity(numValue);
            } else if (type === 'mWheelSensitivity') {
                this.context.setMWheelSensitivity(numValue);
            }
        } else {
            const ctxValue = this.context[type as keyof AppContextType];
            this.setState({
                [type]: String(ctxValue),
            } as unknown as Pick<SettingMenuState, keyof SettingMenuState>);
        }
    };

    render() {
        const {tPadSensitivity, mWheelSensitivity} = this.state;
        let iconSizeSX: Record<string, string> = {};
        let boxIconSX: Record<string, string> = {};
        if (window.innerWidth < 280) {
            iconSizeSX.fontSize = `${window.innerWidth / 300.0}rem`;
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

        const listItemTextTypoStyle: React.CSSProperties = {fontSize: '1rem'};
        const secondaryColorTag = "secondary";

        const parametersAdjustmentTypoSX = {
            input: {
                color: this.context.secondaryColor,
                caretColor: this.context.secondaryColor,
            }
        };
        const parametersAdjustmentTypoProps = {
            focused: true as const,
            size: "small" as const,
            fullWidth: true as const,
            variant: "outlined" as const,
            type: "number" as const,
            slotProps: { htmlInput: { step: '0.01', min: '0' } } as const,
        };

        const formControlLabelRadioSX = {
            color: this.context.secondaryColor,
            '&.Mui-checked': {
                color: this.context.secondaryColor,
            },
        };

        return (
            <ThemeProvider theme={customTheme}>
                <List component="div" disablePadding>
                    <ListItem>
                        <Typography style={listItemTextTypoStyle}>
                            {i18n.Sidebar.SettingMenu.AutoCollapseSubmenus[this.context.i18n as keyof typeof i18n.Sidebar.SettingMenu.AutoCollapseSubmenus]}
                        </Typography>
                        <div style={{flex: 1}}/>
                        <ListItemButton onClick={() => {
                            this.context.toggleAutoCollapse();
                        }}>
                            <Box sx={boxIconSX}>{this.context.autoCollapse ?
                                <CheckBoxRounded sx={iconSizeSX}/> :
                                <CheckBoxOutlineBlankRounded sx={iconSizeSX}/>
                            }</Box>
                        </ListItemButton>
                    </ListItem>
                    <ListItem>
                        <Typography style={listItemTextTypoStyle}>
                            {i18n.Sidebar.SettingMenu.SidebarToggle[this.context.i18n as keyof typeof i18n.Sidebar.SettingMenu.SidebarToggle]}
                        </Typography>
                        <div style={{flex: 1}}/>
                        <FormControl component="fieldset">
                            <RadioGroup
                                row
                                aria-label="sidebar-position"
                                name="row-radio-buttons-group"
                                value={this.state.drawerSide}
                                onChange={this.handleRadioChange}
                                color={secondaryColorTag}
                            >
                                <FormControlLabel
                                    value="l"
                                    control={<Radio
                                        sx={formControlLabelRadioSX}
                                        color={secondaryColorTag}
                                    />}
                                    label="L"
                                />
                                <FormControlLabel
                                    value="r"
                                    control={<Radio
                                        sx={formControlLabelRadioSX}
                                        color={secondaryColorTag}
                                    />}
                                    label="R"
                                />
                            </RadioGroup>
                        </FormControl>
                    </ListItem>
                    <ListItem>
                        <Typography style={listItemTextTypoStyle}>
                            {i18n.Sidebar.SettingMenu.AdjustmentParameters[this.context.i18n as keyof typeof i18n.Sidebar.SettingMenu.AdjustmentParameters]}
                        </Typography>
                        <div style={{flex: 1}}/>
                    </ListItem>
                    <ListItem>
                        <Typography style={listItemTextTypoStyle}>&nbsp;</Typography>
                        <div style={{flex: 1}}/>
                        <TextField
                            label={i18n.Sidebar.SettingMenu.TPadSensitivity[this.context.i18n as keyof typeof i18n.Sidebar.SettingMenu.TPadSensitivity]}
                            variant={parametersAdjustmentTypoProps.variant}
                            value={tPadSensitivity}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => this.handleTextFieldChange(e, 'tPadSensitivity')}
                            onBlur={() => this.handleBlur('tPadSensitivity')}
                            type={parametersAdjustmentTypoProps.type}
                            slotProps={parametersAdjustmentTypoProps.slotProps}
                            size={parametersAdjustmentTypoProps.size}
                            fullWidth={parametersAdjustmentTypoProps.fullWidth}
                            color={secondaryColorTag}
                            sx={parametersAdjustmentTypoSX}
                            focused={parametersAdjustmentTypoProps.focused}
                        />
                        <Typography style={listItemTextTypoStyle}>&nbsp;</Typography>
                    </ListItem>
                    <ListItem>
                        <Typography style={listItemTextTypoStyle}>&nbsp;</Typography>
                        <div style={{flex: 1}}/>
                        <TextField
                            label={i18n.Sidebar.SettingMenu.MWheelSensitivity[this.context.i18n as keyof typeof i18n.Sidebar.SettingMenu.MWheelSensitivity]}
                            variant={parametersAdjustmentTypoProps.variant}
                            value={mWheelSensitivity}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => this.handleTextFieldChange(e, 'mWheelSensitivity')}
                            onBlur={() => this.handleBlur('mWheelSensitivity')}
                            type={parametersAdjustmentTypoProps.type}
                            slotProps={parametersAdjustmentTypoProps.slotProps}
                            size={parametersAdjustmentTypoProps.size}
                            fullWidth={parametersAdjustmentTypoProps.fullWidth}
                            color={secondaryColorTag}
                            sx={parametersAdjustmentTypoSX}
                            focused={parametersAdjustmentTypoProps.focused}
                        />
                        <Typography style={listItemTextTypoStyle}>&nbsp;</Typography>
                    </ListItem>
                </List>
            </ThemeProvider>
        );
    }
}

export default SettingMenu;
