// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

export const api_brightness_get = (): Promise<{ brightness: number }> => {
    return fetch('/api/brightness/get', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            if (data.status === 'error') {
                throw new Error(data.message);
            }
            return data;
        })
        .catch((error) => {
            console.error('Error:', error);
            throw error;
        });
};

export const api_brightness_set = (brightness: string): Promise<void> => {
    return fetch('/api/brightness/set', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: brightness,
    })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            if (data.status === 'error') {
                throw new Error(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            throw error;
        });
};
