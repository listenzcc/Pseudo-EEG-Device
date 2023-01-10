BACKGROUND_COLOR = "#303030";
REFRESH_INTERVAL = 0.1;
REQUEST_SECONDS = 4.0;

function requesting() {
  console.log("Requesting");

  const seconds = REQUEST_SECONDS;

  function freshRequest() {
    const ws = new WebSocket("ws://localhost:23334/?accessToken=123456");

    ws.onopen = function (e) {
      console.log("Connection established");
      ws.send(seconds * 25);
    };

    ws.onerror = function (e) {
      console.log("Connection error", e);
    };

    ws.onmessage = function (response) {
      const { data } = response;
      console.log("Received", data.slice(0, 80));
      console.log(draw(data, seconds));
    };
  }

  freshRequest();

  setInterval(freshRequest, REFRESH_INTERVAL * 1000);
}

function draw(rawData, seconds) {
  const { data, query } = JSON.parse(rawData);

  const timeStampArray = [],
    dataArray = [];

  for (let i in query) {
    data[i].map((d, j) => {
      timeStampArray.push(query[i] + 0.001 * j);
      dataArray.push(d);
    });
  }
  const resArray = timeStampArray.map((d) => d % seconds);

  const channels = dataArray[0].length;

  function findDivider() {
    const max = d3.max(timeStampArray);
    const res = max % seconds;
    document.getElementById("span-1").innerHTML =
      max.toFixed(4) + " | " + res.toFixed(4);
    return { max, res };
  }

  {
    const { max, res } = findDivider();

    const gap = seconds * 0.01;
    const rightTimeStampArray = timeStampArray.filter(
      (t) => t % seconds > res + gap
    );
    const rightDataArray = dataArray.filter(
      (_, i) => timeStampArray[i] % seconds > res + gap
    );
    const rightArray = rightTimeStampArray.map((t, i) => {
      return { t, d: rightDataArray[i] };
    });
    rightArray.sort((a, b) => (a.t % seconds) - (b.t % seconds));

    const { width, height, ctx } = initCanvas(true);

    const scaleOffsetY = d3
        .scaleLinear()
        .domain([-1, channels])
        .range([0, height]),
      scaleY = d3
        .scaleLinear()
        .domain([0, -2000])
        .range([0, height / channels])
        .nice(),
      scaleX = d3.scaleLinear().domain([0, seconds]).range([0, width]).nice();

    // ctx.fillStyle = background_color;
    // ctx.fillRect(0, 0, scaleX(res), height);
    // ctx.fillStyle = background_color + "05";
    // ctx.fillRect(scaleX(res), 0, scaleX(seconds), height);

    for (let j = 0; j < channels; ++j) {
      ctx.save();
      ctx.translate(0, scaleOffsetY(j));

      //
      ctx.strokeStyle = d3.schemePaired[(j * 2 + 1) % 6]; // "blue";
      ctx.beginPath();
      timeStampArray.map((t, i) => {
        if (t > max - res)
          ctx.lineTo(scaleX(t % seconds), scaleY(dataArray[i][j]));
      });
      ctx.stroke();

      //
      ctx.strokeStyle = d3.schemePaired[(j * 2) % 6]; // "blue";
      ctx.beginPath();
      // timeStampArray.map((t, i) => {
      //   if (t % seconds > res + seconds * 0.01)
      //     ctx.lineTo(scaleX(t % seconds), scaleY(dataArray[i][j]));
      // });

      // rightTimeStampArray.map((t, i) => {
      //   ctx.lineTo(scaleX(t % seconds), scaleY(rightDataArray[i][j]));
      // });

      rightArray.map((e) => {
        const { t, d } = e;
        ctx.lineTo(scaleX(t % seconds), scaleY(d[j]));
      });

      ctx.stroke();

      ctx.restore();
    }
  }

  return { ds: dataArray, qs: timeStampArray };
}

function initCanvas(fillRect = true) {
  const canvas = document.getElementById("canvas-1");
  const ctx = canvas.getContext("2d");

  const { width, height } = canvas;

  if (fillRect) {
    ctx.fillStyle = BACKGROUND_COLOR;
    ctx.fillRect(0, 0, width, height);
  }

  return { width, height, ctx };
}
