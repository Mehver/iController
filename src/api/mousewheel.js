export const api_mousewheel = (wheel) => {
    // wheel 为-4到4的整数，表示滚轮向滚动的格数
    fetch('/api/mousewheel', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: wheel.toString(),
    })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch((error) => {
            console.error('Error:', error);
        });
};