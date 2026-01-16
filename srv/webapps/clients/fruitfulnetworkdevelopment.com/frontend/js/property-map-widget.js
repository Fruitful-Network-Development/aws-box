(() => {
  const DEFAULT_DATASET_ID = "3_2_3_17_77_19_10_1_1";

  const getNestedPropertyGeometry = (payload) =>
    payload?.mss_profile?.msn_profile?.fnd_profile?.property?.geometry || null;

  const createSvgElement = (tag, attrs = {}) => {
    const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.entries(attrs).forEach(([key, value]) => {
      el.setAttribute(key, value);
    });
    return el;
  };

  const renderPolygon = (container, coordinates) => {
    const points = coordinates[0];
    if (!Array.isArray(points) || points.length < 3) {
      throw new Error("Polygon coordinates are missing or invalid.");
    }

    const lons = points.map((point) => point[0]);
    const lats = points.map((point) => point[1]);
    const minLon = Math.min(...lons);
    const maxLon = Math.max(...lons);
    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);

    const width = maxLon - minLon || 1;
    const height = maxLat - minLat || 1;
    const paddingRatio = 0.08;
    const paddedWidth = width * (1 + paddingRatio * 2);
    const paddedHeight = height * (1 + paddingRatio * 2);
    const paddedMinLon = minLon - width * paddingRatio;
    const paddedMinLat = minLat - height * paddingRatio;

    const viewBox = [0, 0, paddedWidth, paddedHeight].join(" ");
    const svg = createSvgElement("svg", {
      class: "map-widget__svg",
      viewBox,
      preserveAspectRatio: "xMidYMid meet",
      role: "img",
      "aria-label": "Property boundary",
    });

    const polygonPoints = points
      .map(([lon, lat]) => {
        const x = lon - paddedMinLon;
        const y = paddedHeight - (lat - paddedMinLat);
        return `${x},${y}`;
      })
      .join(" ");

    const polygon = createSvgElement("polygon", {
      points: polygonPoints,
      class: "map-widget__polygon",
    });

    svg.appendChild(polygon);
    container.appendChild(svg);
  };

  const renderMessage = (container, message) => {
    container.innerHTML = `<p class="map-widget__message">${message}</p>`;
  };

  const initializeWidget = async () => {
    const container = document.getElementById("map-widget");
    if (!container) {
      return;
    }

    const datasetId = container.dataset.datasetId || DEFAULT_DATASET_ID;

    try {
      const response = await fetch(`/api/datasets/${datasetId}`);
      if (!response.ok) {
        throw new Error(`Dataset request failed (${response.status}).`);
      }

      const payload = await response.json();
      const geometry = getNestedPropertyGeometry(payload);

      if (!geometry || geometry.type !== "Polygon" || !geometry.coordinates) {
        throw new Error("Property polygon geometry was not found.");
      }

      renderPolygon(container, geometry.coordinates);
    } catch (error) {
      renderMessage(container, "Property boundary data is unavailable.");
      console.error("Map widget error:", error);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeWidget);
  } else {
    initializeWidget();
  }
})();
