#!/usr/bin/env python3
"""Animate only solutions produced by the scheduling model."""

import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import proj_scheduling as scheduling


PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Water Bucket Schedule</title>
  <style>
    :root {
      color-scheme: light;
      font-family: ui-rounded, "Trebuchet MS", system-ui, sans-serif;
      color: #34445b;
      background: #fff8eb;
    }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; }
    main { width: min(1080px, calc(100% - 32px)); margin: 18px auto; }
    .card {
      overflow: hidden;
      border: 1px solid #f0e5d4;
      border-radius: 24px;
      background: #fffdf8;
      box-shadow: 0 16px 50px #65513b12;
    }
    .status { padding: 18px 16px 4px; text-align: center; }
    #time { color: #e7835d; font-size: .92rem; font-weight: 800; }
    #action { min-height: 28px; margin-top: 7px; font-weight: 750; }
    .stage { overflow-x: auto; scrollbar-color: #d2c6b5 #fffdf8; }
    canvas { display: block; height: 420px; }
    .controls {
      display: flex; flex-wrap: wrap; align-items: center; justify-content: center;
      gap: 10px; padding: 14px 18px 20px;
    }
    button {
      border: 0; border-radius: 13px; padding: 10px 16px;
      color: #34445b; background: #f1e8d9; cursor: pointer;
      font: inherit; font-weight: 700; transition: transform .15s, background .15s;
    }
    button:hover { transform: translateY(-2px); background: #e9dcc9; }
    button.primary { color: white; background: #57afd0; }
    button.primary:hover { background: #3899be; }
    label { margin-left: 12px; color: #718096; font-size: .9rem; }
    input { width: 120px; accent-color: #57afd0; vertical-align: middle; }
    footer { padding: 0 14px 20px; color: #8992a0; text-align: center; font-size: .84rem; }
  </style>
</head>
<body>
  <main>
    <section class="card" aria-label="Water bucket schedule animation">
      <div class="status">
        <div id="time" aria-live="polite"></div>
        <div id="action"></div>
      </div>
      <div class="stage"><canvas id="scene" aria-label="Animated water buckets"></canvas></div>
      <div class="controls">
        <button class="primary" id="play">▶ Play</button>
        <button id="pause">Ⅱ Pause</button>
        <button id="step">↷ Step</button>
        <button id="replay">↺ Replay</button>
        <label for="speed">Speed</label>
        <input id="speed" type="range" min="0.5" max="3" step="0.1" value="1">
        <button id="stop">Stop server</button>
      </div>
      <footer>Use Step to watch one scheduled time unit at a time.</footer>
    </section>
  </main>
  <script>
    const solution = __SCHEDULE_JSON__;
    const canvas = document.getElementById("scene");
    const context = canvas.getContext("2d");
    const timeLabel = document.getElementById("time");
    const actionLabel = document.getElementById("action");
    const stage = canvas.parentElement;
    let tick = 0;
    let progress = 0;
    let playing = false;
    let lastFrame = 0;
    let frameHandle = null;

    function operationLabel(operation) {
      if (operation.type === "FILL") return `Fill bucket ${operation.target + 1}`;
      if (operation.type === "EMPTY") return `Empty bucket ${operation.source + 1}`;
      return `Pour ${operation.source + 1} → ${operation.target + 1}`;
    }

    function resizeCanvas() {
      const count = solution.capacities.length;
      const width = Math.max(stage.clientWidth, count * 150 + 70);
      const ratio = window.devicePixelRatio || 1;
      canvas.style.width = `${width}px`;
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(420 * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      draw();
    }

    function draw() {
      const width = canvas.clientWidth;
      const height = 420;
      context.clearRect(0, 0, width, height);
      const count = solution.capacities.length;
      const gap = 34;
      const baseWidth = Math.min(112, (width - 60 - (count - 1) * gap) / count);
      const maxCapacity = Math.max(...solution.capacities);
      const scales = solution.capacities.map(capacity =>
        0.72 + 0.28 * Math.sqrt(capacity / maxCapacity)
      );
      const bucketWidths = scales.map(scale => baseWidth * scale);
      const contentsWidth = bucketWidths.reduce((total, bucketWidth) => total + bucketWidth, 0)
        + (count - 1) * gap;
      const left = (width - contentsWidth) / 2;
      const bottom = 350;
      const current = solution.amounts[tick];
      const following = solution.amounts[Math.min(tick + 1, solution.makespan)];
      const displayed = current.map((amount, index) =>
        amount + (following[index] - amount) * progress
      );
      let nextX = left;
      const buckets = solution.capacities.map((capacity, index) => {
        const bucket = {
          x: nextX,
          top: bottom - 240 * scales[index],
          bottom,
          width: bucketWidths[index],
        };
        nextX += bucket.width + gap;
        return bucket;
      });

      if (tick < solution.makespan) {
        actionLabel.hidden = false;
        timeLabel.textContent = `Time unit ${tick + 1} of ${solution.makespan}`;
        actionLabel.textContent = solution.operations[tick].map(operationLabel).join("   ·   ");
      } else {
        timeLabel.textContent = `Finished in ${solution.makespan} time unit${solution.makespan === 1 ? "" : "s"}`;
        actionLabel.hidden = true;
      }

      solution.capacities.forEach((capacity, index) => {
        drawBucket(
          buckets[index],
          capacity,
          displayed[index],
          solution.goal[index],
          index
        );
      });
      if (tick < solution.makespan) {
        drawOperations(buckets);
      }
    }

    function drawBucket(bucket, capacity, amount, goal, index) {
      const ctx = context;
      const { x, top, bottom, width } = bucket;
      const height = bottom - top;
      const waterTop = bottom - Math.max(0, Math.min(1, amount / capacity)) * height;
      ctx.textAlign = "center";
      ctx.fillStyle = "#34445b";
      ctx.font = "700 14px system-ui, sans-serif";
      ctx.fillText(`Bucket ${index + 1}`, x + width / 2, top - 54);
      ctx.fillStyle = "#718096";
      ctx.font = "12px system-ui, sans-serif";
      ctx.fillText(`${amount.toFixed(1)} / ${capacity} L`, x + width / 2, top - 34);
      ctx.fillText(goal < 0 ? "any amount" : `goal ${goal} L`, x + width / 2, top - 16);

      if (amount > 0) {
        ctx.save();
        ctx.beginPath();
        ctx.rect(x + 4, top + 3, width - 8, height - 7);
        ctx.clip();
        ctx.beginPath();
        ctx.moveTo(x + 4, bottom - 4);
        ctx.lineTo(x + 4, waterTop);
        for (let offset = 0; offset <= width - 8; offset += 8) {
          ctx.lineTo(
            x + 4 + offset,
            waterTop + Math.sin(offset / 13 + tick + progress * 5) * 2.5
          );
        }
        ctx.lineTo(x + width - 4, bottom - 4);
        ctx.closePath();
        ctx.fillStyle = "#75d0ed";
        ctx.fill();
        ctx.restore();
      }

      ctx.strokeStyle = "#c58c57";
      ctx.lineWidth = 5;
      ctx.lineJoin = "round";
      ctx.strokeRect(x, top, width, height);
      ctx.strokeStyle = "#f0c997";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(x + 8, top + 2);
      ctx.lineTo(x + width - 8, top + 2);
      ctx.stroke();
    }

    function drawOperations(buckets) {
      const ctx = context;
      for (const operation of solution.operations[tick]) {
        const source = buckets[operation.source];
        const target = buckets[operation.target];
        const sourceX = source.x + source.width / 2;
        const targetX = target.x + target.width / 2;
        ctx.lineWidth = 4;
        ctx.strokeStyle = "#36a9d4";
        ctx.fillStyle = "#68c9ed";
        if (operation.type === "FILL") {
          const x = targetX;
          const top = target.top;
          ctx.beginPath();
          ctx.moveTo(x, top - 48);
          ctx.lineTo(x, top - 34);
          ctx.lineTo(x - 14, top - 34);
          ctx.lineTo(x - 14, top - 21);
          ctx.stroke();
          ctx.beginPath();
          ctx.arc(x - 14, top - 15, 4, 0, Math.PI * 2);
          ctx.fill();
        } else if (operation.type === "EMPTY") {
          const x = sourceX;
          const bottom = source.bottom;
          ctx.beginPath();
          ctx.moveTo(x, bottom + 4);
          ctx.lineTo(x, bottom + 22);
          ctx.stroke();
          ctx.beginPath();
          ctx.arc(x, bottom + 27, 5, 0, Math.PI * 2);
          ctx.fill();
        } else {
          const sourceLevel = solution.amounts[tick][operation.source] /
            solution.capacities[operation.source];
          const targetLevel = solution.amounts[tick + 1][operation.target] /
            solution.capacities[operation.target];
          const startY = source.bottom - sourceLevel * (source.bottom - source.top);
          const endY = target.bottom - targetLevel * (target.bottom - target.top);
          ctx.beginPath();
          ctx.moveTo(sourceX, startY);
          ctx.quadraticCurveTo((sourceX + targetX) / 2, Math.min(startY, endY) - 26, targetX, endY);
          ctx.stroke();
          const dropX = sourceX + (targetX - sourceX) * progress;
          const dropY = startY + (endY - startY) * progress - 10;
          ctx.beginPath();
          ctx.arc(dropX, dropY, 6, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }

    function pause() {
      playing = false;
      if (frameHandle !== null) cancelAnimationFrame(frameHandle);
      frameHandle = null;
      draw();
    }

    function animate(timestamp) {
      if (!playing) return;
      if (lastFrame === 0) lastFrame = timestamp;
      const elapsed = timestamp - lastFrame;
      lastFrame = timestamp;
      progress += elapsed * Number(document.getElementById("speed").value) / 900;
      if (progress >= 1) {
        tick += 1;
        progress = 0;
      }
      draw();
      if (tick >= solution.makespan) {
        pause();
        return;
      }
      frameHandle = requestAnimationFrame(animate);
    }

    document.getElementById("play").addEventListener("click", () => {
      if (playing || solution.makespan === 0) return;
      if (tick >= solution.makespan) {
        tick = 0;
        progress = 0;
      }
      playing = true;
      lastFrame = 0;
      frameHandle = requestAnimationFrame(animate);
    });
    document.getElementById("pause").addEventListener("click", pause);
    document.getElementById("step").addEventListener("click", () => {
      pause();
      if (tick < solution.makespan) {
        tick += 1;
        progress = 0;
        draw();
      }
    });
    document.getElementById("replay").addEventListener("click", () => {
      pause();
      tick = 0;
      progress = 0;
      draw();
    });
    document.getElementById("stop").addEventListener("click", () => {
      pause();
      actionLabel.textContent = "Animation server stopped. You can close this tab.";
      fetch("/shutdown", { method: "POST" }).catch(() => {});
    });
    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();
  </script>
</body>
</html>"""


def read_schedule(result, bucket_count):
    """Return the solved water levels and active operations for each time unit."""
    makespan = int(result["makespan"])
    amounts = [
        [int(result["amount"][bucket][step]) for bucket in range(bucket_count)]
        for step in range(makespan + 1)
    ]
    operation_names = {1: "FILL", 2: "EMPTY", 3: "POUR"}
    operations = []
    for step in range(makespan):
        tick_operations = []
        for slot, op in enumerate(result["op"][step]):
            op = int(op)
            if op == 0:
                continue
            tick_operations.append(
                {
                    "type": operation_names[op],
                    "source": int(result["source"][step][slot]) - 1,
                    "target": int(result["target"][step][slot]) - 1,
                }
            )
        operations.append(tick_operations)
    return amounts, operations


def serve_animation(capacities, goal, amounts, operations):
    schedule = {
        "capacities": capacities,
        "goal": goal,
        "amounts": amounts,
        "operations": operations,
        "makespan": len(operations),
    }
    page = PAGE.replace(
        "__SCHEDULE_JSON__",
        json.dumps(schedule).replace("<", "\\u003c").replace(">", "\\u003e"),
    )

    class AnimationHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/":
                self.send_error(404)
                return
            body = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != "/shutdown":
                self.send_error(404)
                return
            self.send_response(204)
            self.end_headers()
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    server = ThreadingHTTPServer(("127.0.0.1", 0), AnimationHandler)
    address = f"http://127.0.0.1:{server.server_port}/"
    print(f"Opening schedule animation at {address}", flush=True)
    if not webbrowser.open(address):
        print("Open the URL above in your browser to view the animation.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv=None):
    args = scheduling.parse_args(argv)
    capacities, initial, goal, max_steps = scheduling.load_instance(args)
    result, bucket_count = scheduling.build_and_solve(
        capacities, initial, goal, max_steps, args.solver
    )
    if result.solution is None:
        print(
            scheduling.format_solution(
                result, capacities, initial, goal, bucket_count, max_steps
            ),
            end="",
        )
        raise SystemExit(1)

    amounts, operations = read_schedule(result, bucket_count)
    serve_animation(capacities, goal, amounts, operations)


if __name__ == "__main__":
    main()
