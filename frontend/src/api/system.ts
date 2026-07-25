// SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
// SPDX-License-Identifier: BSD-3-Clause

export const api_get_system_info = (): Promise<{ os: string }> => {
    return fetch('/api/system/info', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            return data;
        })
        .catch((error) => {
            console.error('Error:', error);
            throw error;
        });
}
