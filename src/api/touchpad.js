export const api_touchpad = (xPercent, yPercent) => {
    // 创建一个足够存储两个float32值的缓冲区
    const buffer = new ArrayBuffer(8); // 每个float32占用4字节
    const view = new DataView(buffer);

    // 将x和y值写入缓冲区
    // 第三个参数设置为true表示使用小端序
    view.setFloat32(0, xPercent, true); // 从缓冲区的起始位置写入x
    view.setFloat32(4, yPercent, true); // 从缓冲区的第4字节位置写入y

    // 发送二进制数据
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