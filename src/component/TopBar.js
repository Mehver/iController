import React from 'react';

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
                </div>
            </>
        )
    }
}

export default TopBar;