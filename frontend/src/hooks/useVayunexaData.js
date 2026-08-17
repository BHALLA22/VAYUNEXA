import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getAIPrediction,
  getAutoControl,
} from "../services/api";


export function useVayunexaData(
  deviceId = "VAYU-001"
) {
  const [prediction, setPrediction] =
    useState(null);

  const [control, setControl] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState(null);


  const refresh = useCallback(
    async () => {
      try {
        setError(null);

        const [
          predictionData,
          controlData,
        ] = await Promise.all([
          getAIPrediction(deviceId),
          getAutoControl(deviceId),
        ]);

        setPrediction(
          predictionData
        );

        setControl(
          controlData
        );

      } catch (err) {
        console.error(err);

        setError(
          err.message
        );

      } finally {
        setLoading(false);
      }
    },
    [deviceId]
  );


  useEffect(() => {
    refresh();

    const interval =
      setInterval(
        refresh,
        5000
      );

    return () =>
      clearInterval(interval);

  }, [refresh]);


  return {
    prediction,
    control,
    loading,
    error,
    refresh,
  };
}