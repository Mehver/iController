import React from 'react';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import {Context} from '../utils/Context';

class TopBar extends React.Component {
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
            // 增加透明的伪元素以扩大触发区域
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

TopBar.contextType = Context;

export default TopBar;
