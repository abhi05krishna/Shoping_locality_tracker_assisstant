(() => {
  const chartAnchor = "#price-trend";

  function scrollToOpenedChart() {
    if (window.location.hash !== chartAnchor) return;

    const chart = document.querySelector(chartAnchor);
    if (chart) chart.scrollIntoView({ block: "start", behavior: "auto" });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      window.requestAnimationFrame(scrollToOpenedChart);
    }, { once: true });
  } else {
    window.requestAnimationFrame(scrollToOpenedChart);
  }
})();
