const baseUrl = 'http://localhost:4200';

export const api = {
  get(url, dataType = 'json') {
    const apiUrl = `${baseUrl}${url}`;

    const promise = fetch(apiUrl, {
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': `application/${dataType}`,
      },
    });

    return promise.then((response) => {
      if (response.status !== 204) {
        return response.json();
      }
      return null;
    });
  },
};
