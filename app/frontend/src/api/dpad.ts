// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

export const api_dpad = (signal: string): Promise<void> => {
    return fetch('/api/dpad', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: signal,
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
