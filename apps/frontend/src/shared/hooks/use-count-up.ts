import * as React from "react";

export const useCountUp = (target: number, duration = 700) => {
  const [value, setValue] = React.useState(0);
  const previousTarget = React.useRef(0);

  React.useEffect(() => {
    const from = previousTarget.current;
    const to = target;
    previousTarget.current = to;

    if (from === to) {
      setValue(to);
      return;
    }

    const start = performance.now();
    let frame: number;

    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(from + (to - from) * eased));
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      }
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);

  return value;
};
