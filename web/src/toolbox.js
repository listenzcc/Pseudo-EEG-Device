BACKGROUND_COLOR = "#303030";
REFRESH_INTERVAL = 0.1;
REQUEST_SECONDS = 4.0;
POINTS_PER_SECOND = parseInt(1000 / 40);

INTERVALS = Object.assign({
  id: undefined,
});

/**
 * Keep requesting frames from the data center.
 */
function requesting() {
  console.log("Requesting");

  const seconds = REQUEST_SECONDS;

  /**
   * Request single frame and draw it into the canvas.
   * The draw method is called to draw the frame.
   */
  function freshRequest() {
    const ws = new WebSocket("ws://localhost:23334/?accessToken=123456");

    ws.onopen = function (e) {
      // console.log("Connection established");
      ws.send(seconds * POINTS_PER_SECOND);
    };

    ws.onerror = function (e) {
      console.error("Connection error", e);
    };

    ws.onmessage = function (response) {
      const { data } = response;
      // console.log("Received", data.slice(0, 80));
      draw(data, seconds);
    };
  }

  // freshRequest();

  stopRequesting();
  INTERVALS.id = setInterval(freshRequest, REFRESH_INTERVAL * 1000);
  console.log(
    "Start interval for requesting and drawing the frames",
    INTERVALS.id
  );
}

/**
 * Stop the requesting interval timer
 */
function stopRequesting() {
  if (INTERVALS.id) {
    clearInterval(INTERVALS.id);
    console.log("Stop interval", INTERVALS.id);
    INTERVALS.id = undefined;
  } else {
    console.warn("Invalid INTERVALS.id, so doing nothing");
  }
}

/**
 * Draw the data into the canvas,
 * the frames is plotted into the canvas,
 * using the prepareCanvas.
 *
 * @param {Bytes} rawData , the received bytes from the server.
 * @param {Int} seconds , How many seconds the data contains.
 */
function draw(rawData, seconds) {
  const { frames, channels, latency } = convertFrame(rawData);

  const { max, res, leftFrames, rightFrames } = divideFrames(frames, seconds);
  document.getElementById("span-1").innerHTML =
    max.toFixed(4) +
    " | " +
    res.toFixed(4) +
    " | " +
    d3.mean(latency, (d) => d.latency).toFixed(4);

  drawFrames(leftFrames, rightFrames, seconds, channels);

  /**
   * Draw the left and right frames into the canvas,
   * and the canvas is built by the prepareCanvas function.
   *
   * @param {Array} leftFrames The frame array on the left side of the refreshing line;
   * @param {Array} rightFrames The frame array on the right side of the refreshing line;
   * @param {Int} seconds The seconds of displaying;
   * @param {Int} channels The channels of the frame.
   */
  function drawFrames(leftFrames, rightFrames, seconds, channels) {
    const { width, height, ctx } = prepareCanvas(true);

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

    for (let j = 0; j < channels; ++j) {
      ctx.save();
      ctx.translate(0, scaleOffsetY(j));

      // Left frames
      ctx.strokeStyle = d3.schemePaired[(j * 2 + 1) % 6];
      ctx.beginPath();
      leftFrames.map((e) => {
        const { t, frame } = e;
        ctx.lineTo(scaleX(t % seconds), scaleY(frame[j]));
      });
      ctx.stroke();

      // Right frames
      ctx.strokeStyle = d3.schemePaired[(j * 2) % 6];
      ctx.beginPath();
      rightFrames.map((e) => {
        const { t, frame } = e;
        ctx.lineTo(scaleX(t % seconds), scaleY(frame[j]));
      });
      ctx.stroke();

      ctx.restore();
    }
  }

  /**
   * Divide the frames into left and right frames.
   *
   * @param {Array} frames The frames being divided into left and right sides frames, and the divider is the refreshing line
   * @param {Int} seconds The seconds of the frames.
   * @returns {} {max, res, leftFrames, rightFrames} The res refers the refreshing line.
   */
  function divideFrames(frames, seconds) {
    const max = d3.max(frames, (d) => d.t),
      res = max % seconds,
      gap = seconds * 0.01;

    const leftFrames = frames.filter((d) => d.t % seconds < res),
      rightFrames = frames.filter((d) => d.t % seconds > res + gap);

    leftFrames.sort((d) => d.t);
    rightFrames.sort((d) => d.t);

    return { max, res, leftFrames, rightFrames };
  }

  /**
   * Convert the bytes into the frames array.
   *
   * @param {Bytes} rawData The raw data to be parsed as the JSON object.
   * @returns {} {frames, channels, latency} The latency is the array of the latency of the frames.
   */
  function convertFrame(rawData) {
    const { data, query, query2 } = JSON.parse(rawData);

    const frames = [],
      latency = [];

    // i: The index of the frame package;
    // j: There are 40 frames in the package, each refers a frame.
    for (let i in query) {
      data[i].map((d, j) => {
        frames.push({ t: query[i] + 0.001 * j, frame: d });
        latency.push({ t: query[i], t2: query2[i] });
      });
    }

    latency.map((d) => (d.latency = d.t2 - d.t));

    const channels = frames[0].frame.length;

    return { frames, channels, latency };
  }
}

/**
 * Prepare the canvas,
 * and return the ctx and its size for plotting.
 *
 * @param {boolean} fillRect, the option of whether to fill the canvas with the BACKGROUND_COLOR
 * @returns {} {width, height, ctx}
 */
function prepareCanvas(fillRect = true) {
  const canvas = document.getElementById("canvas-1");
  const ctx = canvas.getContext("2d");

  const { width, height } = canvas;

  if (fillRect) {
    ctx.fillStyle = BACKGROUND_COLOR;
    ctx.fillRect(0, 0, width, height);
  }

  return { width, height, ctx };
}
