// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

export const api_volume_get = (): Promise<{ volume: number }> => {
    return fetch('/api/volume/get', {
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

export const api_volume_set = (volume: string): Promise<void> => {
    return fetch('/api/volume/set', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: volume,
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
