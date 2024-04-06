import {createTheme} from "@mui/material/styles";

export const primaryColor = '#6df';
export const primaryColorTrans = 'rgba(102, 204, 255, 0.5)';
export const secondaryColor = '#333';
export const secondaryColorTrans = 'rgba(51, 51, 51, 0.5)';

export const customTheme = createTheme({
    palette: {
        primary: {
            main: primaryColor,
        },
        secondary: {
            main: secondaryColor,
        },
        inherit: {
            main: '#333',
        }
    },
});