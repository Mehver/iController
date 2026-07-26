// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

import React from 'react';
import { IconButton } from '@mui/material';
import { Menu as MenuIcon } from '@mui/icons-material';
import {Context} from '../utils/Context';
import {AppContextType} from '../types';

class TopBar extends React.Component {
    static contextType = Context;
    declare context: AppContextType;

    render() {
        let nameFrontSize = '20px';
        let nameFrontTop = '-14px';
        if (window.innerWidth < 280) {
            nameFrontSize = `${(window.innerWidth / 280.0) * 20.0}px`;
            nameFrontTop = `${(window.innerWidth / 280.0) * -11.0}px`;
            if (window.innerWidth < 240) {
                nameFrontTop = `${(window.innerWidth / 280.0) * -7.0}px`;
            }
        }
        const iconButtonSX = {
            position: 'absolute',
            top: 0,
            right: 0,
            marginRight: '10px',
            marginTop: '10px',
            width: '20px',
            height: '20px',
            color: this.context.secondaryColor,
            '&:after': {
                content: '""',
                position: 'absolute',
                top: '-30px',
                right: '-30px',
                bottom: '-30px',
                left: '-30px',
            },
        };
        return (
            <>
                <div id="topBar" style={{
                    position: 'absolute',
                    top: '-5px',
                    width: '100%',
                    height: '35px',
                    backgroundColor: this.context.primaryColor,
                }}>
                    <p style={{
                        fontSize: nameFrontSize,
                        fontWeight: 'bold',
                        color: this.context.secondaryColor,
                        float: 'left',
                        position: 'relative',
                        top: nameFrontTop,
                        left: '8px'
                    }}>
                        iController
                    </p>
                    <IconButton
                        edge="start"
                        aria-label="menu"
                        sx={iconButtonSX}
                        onClick={() => {
                            this.context.setDrawerOpen(true);
                        }}
                    >
                        <MenuIcon/>
                    </IconButton>
                </div>
            </>
        )
    }
}

export default TopBar;
