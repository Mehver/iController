// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

export const api_touchpad = (xPercent: string, yPercent: string): Promise<void> => {
    const buffer = new ArrayBuffer(8);
    const view = new DataView(buffer);

    view.setFloat32(0, parseFloat(xPercent), true);
    view.setFloat32(4, parseFloat(yPercent), true);

    return fetch('/api/touchpad', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/octet-stream',
        },
        body: buffer,
    })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => console.log('Success:', data))
        .catch((error) => {
            console.error('Error:', error);
            throw error;
        });
};

export const api_touchpad_reposition = (): Promise<void> => {
    return fetch('/api/touchpad/reposition', {
        method: 'POST',
    })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => console.log('Success:', data))
        .catch((error) => {
            console.error('Error:', error);
            throw error;
        });
};
