const assert = require("assert");
const { calcTravelTax } = require("./app.js");
const r = calcTravelTax(11000, 0.2, 3.0, "included");
assert.strictEqual(r.twdTaxFree, 2000);
assert(r.eligible.includes("符合"));
console.log("TRAVEL_TAX_TESTS_PASSED");