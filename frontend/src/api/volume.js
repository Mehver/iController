export const api_volume_get = () => {
    // 返回 fetch 调用的 Promise
    return fetch('/api/volume/get', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })
        .then(response => {
            if (!response.ok) {
                // 如果响应状态码不是 2xx, 抛出错误
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            // 将数据作为 Promise 的解析值返回
            return data;
        })
        .catch((error) => {
            console.error('Error:', error);
            // 还可以选择在这里抛出错误，让外部调用者处理
            throw error;
        });
}

export const api_volume_set = (volume) => {
    fetch('/api/volume/set', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain',
        },
        body: volume,
    })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch((error) => {
            console.error('Error:', error);
        });
}