"use client";

import { useEffect, useRef, useState } from "react";

type PollingState<T> = {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
};

export function usePolling<T>(
  fetcher: () => Promise<T>,
  intervalMs: number,
): PollingState<T> {
  const [state, setState] = useState<PollingState<T>>({
    data: null,
    error: null,
    isLoading: true,
  });
  const fetcherRef = useRef(fetcher);

  useEffect(() => {
    fetcherRef.current = fetcher;
  }, [fetcher]);

  useEffect(() => {
    let isActive = true;

    async function tick() {
      try {
        const data = await fetcherRef.current();
        if (isActive) {
          setState({ data, error: null, isLoading: false });
        }
      } catch (error) {
        if (isActive) {
          setState({
            data: null,
            error: error instanceof Error ? error : new Error("Polling failed"),
            isLoading: false,
          });
        }
      }
    }

    void tick();
    const timer = window.setInterval(() => void tick(), intervalMs);

    return () => {
      isActive = false;
      window.clearInterval(timer);
    };
  }, [intervalMs]);

  return state;
}
