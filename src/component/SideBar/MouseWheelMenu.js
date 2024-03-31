import React, {Component, useState, useEffect} from 'react';
import {Knob} from 'primereact/knob';
import {List, ListItem, Box, Divider} from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import {Context} from '../../utils/Context';
import IconButton from "@mui/material/IconButton";
import {api_mousewheel} from "../../api/mousewheel";

// 旋钮组件
function KnobComponent() {
    const [value, setValue] = useState(0);

    // 改变组件状态的同时调用API发送值
    const updateValue = (newValue) => {
        setValue(newValue); // 更新状态
        if (newValue !== 0) {
            api_mousewheel(newValue); // 调用API发送值
        }
    };

    // 旋钮回中逻辑
    useEffect(() => {
        const timer = setTimeout(() => updateValue(0), 500); // 0.5秒后自动回中
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
                        onClick={() => {
                            const newValue = Math.max(value - 1, -4);
                            updateValue(newValue);
                        }}
                        disabled={value === -4}
                        fontSize="inherit"
                    />
                </IconButton>
                <IconButton size="large">
                    <AddIcon
                        onClick={() => {
                            const newValue = Math.min(value + 1, 4);
                            updateValue(newValue);
                        }} disabled={value === 4}
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
            <>
                <List component="div" disablePadding style={{width: '100%', display: 'flex', justifyContent: 'center'}}>
                    <ListItem>
                        <KnobComponent/>
                    </ListItem>
                </List>
                <Divider/>
            </>
        );
    }
}

MouseWheelMenu.contextType = Context;

export default MouseWheelMenu;
