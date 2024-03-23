import React, {Component, useState, useEffect} from 'react';
import {Knob} from 'primereact/knob';
import {List, ListItem, Button, Box} from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import {Context} from '../../utils/Context';
import IconButton from "@mui/material/IconButton";

// 旋钮组件
function ReactiveDemo() {
    const [value, setValue] = useState(0);

    // 旋钮回中逻辑
    useEffect(() => {
        const timer = setTimeout(() => setValue(0), 700); // 0.7秒后自动回中
        return () => clearTimeout(timer);
    }, [value]);

    let knobSize = 150;
    if (window.innerWidth < 280) {
        knobSize = 150.0 * window.innerWidth / 280.0;
    }

    return (
        <Box display="flex" flexDirection="column" alignItems="center" gap={2}
             style={{backgroundColor: '#6df', width: '100%'}}>
            <Knob value={value} size={knobSize} min={-4} max={4} step={1}
                  textColor="#333"
                  valueColor="#6df"
                  rangeColor="#333"
                  strokeWidth={10}
                  valueTemplate="{value}"
            />
            <Box display="flex" gap={2}>
                <IconButton size="large">
                    <RemoveIcon
                        onClick={() => setValue(prevValue => Math.max(prevValue - 1, -4))}
                        disabled={value === -4}
                        fontSize="inherit"
                    />
                </IconButton>
                <IconButton size="large">
                    <AddIcon
                        onClick={() => setValue(prevValue => Math.min(prevValue + 1, 4))}
                        disabled={value === 4}
                        fontSize="inherit"
                    />
                </IconButton>
            </Box>
        </Box>
    );
}

// 菜单组件
class MouseWheelMenu extends Component {
    render() {
        return (
            <List component="div" disablePadding style={{width: '100%', display: 'flex', justifyContent: 'center'}}>
                <ListItem>
                    <ReactiveDemo/>
                </ListItem>
            </List>
        );
    }
}

MouseWheelMenu.contextType = Context;

export default MouseWheelMenu;
