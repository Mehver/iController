import React from 'react';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import {Context} from '../utils/Context';

class TopBar extends React.Component {
    render() {
        return (
            <>
                <div id="topBar" style={{
                    position: 'absolute',
                    top: '-5px',
                    width: '100%',
                    height: '35px',
                    backgroundColor: '#6df',
                }}>
                    <p style={{
                        fontSize: '20px',
                        fontWeight: 'bold',
                        color: '#333',
                        float: 'left',
                        position: 'relative',
                        top: '-14px',
                        left: '8px'
                    }}>
                        iController
                    </p>
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
                            color: '#333',
                            // 增加透明的伪元素以扩大触发区域
                            '&:after': {
                                content: '""',
                                position: 'absolute',
                                top: '-30px',
                                right: '-30px',
                                bottom: '-30px',
                                left: '-30px',
                            },
                        }}
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
