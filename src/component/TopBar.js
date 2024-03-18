import React from 'react';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import { Context } from '../utils/Context';

class TopBar extends React.Component {
    render() {
        const topBarCss = {
            position: 'absolute',
            top: '-5px',
            width: '100%',
            height: '35px',
            backgroundColor: '#6df',
        };
        const titleCss = {
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#333',
            float: 'left',
            position: 'relative',
            top: '-14px',
            left: '8px'
        };
        return (
            <>
                <div id="topBar" style={topBarCss}>
                    <p style={titleCss}>iController</p>
                    <IconButton
                        edge="start"
                        aria-label="menu"
                        sx={{
                            position: 'absolute',
                            top: 0,
                            right: 0,
                            marginRight: '10px',
                            marginTop: '10px',
                            width: '20px',
                            height: '20px',
                            color: '#333'
                        }}
                        onClick={() => {
                            this.context.setDrawerOpen(true);
                        }}
                    >
                        <MenuIcon />
                    </IconButton>
                </div>
            </>
        )
    }
}

TopBar.contextType = Context;

export default TopBar;
