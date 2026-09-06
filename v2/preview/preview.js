(function () {
  document.querySelectorAll(".chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      chip.classList.toggle("is-on");
    });
  });

  var cook = document.getElementById("cook");
  var openBtn = document.getElementById("open-cook");
  var closeBtn = document.getElementById("close-cook");
  if (cook && openBtn) {
    openBtn.addEventListener("click", function () {
      cook.hidden = false;
    });
  }
  if (cook && closeBtn) {
    closeBtn.addEventListener("click", function () {
      cook.hidden = true;
    });
  }

  var input = document.getElementById("anchor");
  if (!input) return;

  function roundShown(n, unit) {
    if (unit === "зубчик") return (Math.round(n * 2) / 2).toString();
    if (n >= 200) return String(Math.round(n / 10) * 10);
    if (n >= 50) return String(Math.round(n / 5) * 5);
    return String(Math.round(n));
  }

  function render() {
    var ratio = Number(input.value) / 500;
    document.querySelectorAll(".amt[data-base]").forEach(function (el) {
      var base = Number(el.getAttribute("data-base"));
      var mode = el.getAttribute("data-mode");
      var unit = el.getAttribute("data-unit") || "г";
      var factor = mode === "gentle" ? Math.pow(ratio, 0.7) : ratio;
      var n = base * factor;
      el.textContent = roundShown(n, unit) + " " + unit;
    });
  }

  input.addEventListener("input", render);
  document.querySelectorAll("[data-delta]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = Number(input.value) + Number(btn.getAttribute("data-delta"));
      input.value = String(Math.max(50, next));
      render();
    });
  });
})();
