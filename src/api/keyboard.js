export const api_keyboard_buttons = (signal) => {
    fetch('/api/keyboard/buttons', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: signal,
    })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch((error) => {
            console.error('Error:', error);
        });
};

export const api_keyboard_typewriting = (text) => {
    fetch('/api/keyboard/typewriting', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: text,
    })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch((error) => {
            console.error('Error:', error);
        });
};

export const api_keyboard_pastetext = (text) => {
    fetch('/api/keyboard/pastetext', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: text,
    })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch((error) => {
            console.error('Error:', error);
        });
};