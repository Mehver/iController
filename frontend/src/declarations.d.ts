declare module 'react-color' {
  import React from 'react';

  interface HSLColor {
    a?: number;
    h: number;
    l: number;
    s: number;
  }

  interface RGBColor {
    a?: number;
    b: number;
    g: number;
    r: number;
  }

  interface ColorResult {
    hex: string;
    hsl: HSLColor;
    rgb: RGBColor;
  }

  interface ColorPickerProps {
    color?: string;
    onChange?: (color: ColorResult, event?: React.ChangeEvent) => void;
    onChangeComplete?: (color: ColorResult, event?: React.ChangeEvent) => void;
  }

  export const HuePicker: React.ComponentType<ColorPickerProps>;

  interface TwitterPickerProps extends ColorPickerProps {
    colors?: string[];
    onSwatchHover?: (color: ColorResult, event?: React.MouseEvent) => void;
    triangle?: 'hide' | 'top-left' | 'top-right';
    width?: string;
  }

  export const TwitterPicker: React.ComponentType<TwitterPickerProps>;
}
