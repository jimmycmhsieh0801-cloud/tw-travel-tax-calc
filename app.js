function calcTravelTax(amount, fxRate, rewardPct = 3.0, taxMode = "included") {
  const amt = Math.max(0, Number(amount) || 0);
  const fx = Math.max(0, Number(fxRate) || 0.215);
  const rw = Math.max(0, Number(rewardPct) || 0);
  const taxFreeForeign = taxMode === "included" ? amt / 1.1 : amt;
  const twdTaxFree = Math.round(taxFreeForeign * fx);
  const netFactor = 1 + 0.015 - rw / 100;
  const twdNet = Math.round(twdTaxFree * netFactor);
  const eligible = taxFreeForeign >= 5000 ? "符合日本 ≥5,000 免稅門檻" : `還差 ${Math.ceil(5000 - taxFreeForeign)} 日圓達免稅`;
  return { twdTaxFree, twdNet, eligible };
}
if (typeof document !== "undefined") {
  const ids = ["foreignAmt", "fxRate", "cardReward", "taxMode"];
  function render() {
    const [a, f, r, m] = ids.map(id => document.getElementById(id).value);
    const res = calcTravelTax(a, f, r, m);
    document.getElementById("twdTaxFreeEl").textContent = `NT$ ${res.twdTaxFree.toLocaleString()}`;
    document.getElementById("twdNetEl").textContent = `NT$ ${res.twdNet.toLocaleString()}`;
    document.getElementById("taxVerdictEl").textContent = res.eligible;
  }
  ids.forEach(id => document.getElementById(id).addEventListener("input", render));
  render();
}
if (typeof module !== "undefined" && module.exports) module.exports = { calcTravelTax };