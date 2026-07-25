// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

export const api_touchpad = (xPercent: string, yPercent: string): void => {
    const buffer = new ArrayBuffer(8);
    const view = new DataView(buffer);

    view.setFloat32(0, parseFloat(xPercent), true);
    view.setFloat32(4, parseFloat(yPercent), true);

    fetch('/api/touchpad', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/octet-stream',
        },
        body: buffer,
    })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch((error) => {
            console.error('Error:', error);
        });
}

export const api_touchpad_reposition = (): void => {
    fetch('/api/touchpad/reposition', {
        method: 'POST',
    })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch((error) => {
            console.error('Error:', error);
        });
}
