// 发送按钮信号的函数，传递信号为纯文本
export const api_button = (buttonType) => {
    // 使用简短编码表示不同的按钮
    const signal =
        buttonType === 'Left' ? 'L' :
        buttonType === 'Middle' ? 'M' :
        buttonType === 'Right' ? 'R' :
        buttonType === 'DUp' ? 'W' :
        buttonType === 'DLeft' ? 'A' :
        buttonType === 'DDown' ? 'S' :
        buttonType === 'DRight' ? 'D' :
    '';

    fetch('/api/button', {
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