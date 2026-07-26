// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

export const api_mousewheel = (wheel: number): Promise<void> => {
    return fetch('/api/mousewheel', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: wheel.toString(),
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
