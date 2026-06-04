(function () {
  function showToast(message) {
    var toast = document.getElementById("bk-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "bk-toast";
      toast.className = "bk-toast";
      document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.classList.add("is-visible");
    clearTimeout(toast._tid);
    toast._tid = setTimeout(function () {
      toast.classList.remove("is-visible");
    }, 1800);
  }

  function copyText(id) {
    var target = document.getElementById(id);
    if (!target) return;

    var value = target.dataset.secret || target.innerText || target.value || "";
    navigator.clipboard.writeText(value.trim()).then(function () {
      showToast("Copied!");
    });
  }

  function revealSecret(id) {
    var el = document.getElementById(id);
    if (!el) return;

    if (el.dataset.hidden === "1") {
      el.innerText = el.dataset.secret || "";
      el.dataset.hidden = "0";
    } else {
      el.innerText = el.dataset.masked || "";
      el.dataset.hidden = "1";
    }
  }

  function localizeDatetimes() {
    document.querySelectorAll(".local-datetime").forEach(function (el) {
      var utcStr = el.getAttribute("data-utc");
      if (!utcStr) return;

      try {
        if (!utcStr.endsWith("Z") && !utcStr.includes("+")) {
          utcStr += "Z";
        }
        var date = new Date(utcStr);
        if (isNaN(date.getTime())) return;

        var format = el.getAttribute("data-format");
        if (format === "time") {
          el.textContent = date.toLocaleTimeString(undefined, {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: false
          });
        } else if (format === "date") {
          el.textContent = date.toLocaleDateString(undefined, {
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
          });
        } else {
          var dateStr = date.toLocaleDateString(undefined, {
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
          });
          var timeStr = date.toLocaleTimeString(undefined, {
            hour: "2-digit",
            minute: "2-digit",
            hour12: false
          });
          el.textContent = dateStr + " " + timeStr;
        }
      } catch (error) {
        console.error(error);
      }
    });
  }

  function hydrateProgressBars() {
    document.querySelectorAll("[data-progress-width]").forEach(function (el) {
      var pct = Number(el.getAttribute("data-progress-width") || 0);
      if (!Number.isFinite(pct)) pct = 0;
      pct = Math.max(0, Math.min(100, pct));
      el.style.width = pct + "%";
    });
  }

  function attachDeclarativeHandlers() {
    document.addEventListener("click", function (event) {
      var copyButton = event.target.closest("[data-copy-target]");
      if (copyButton) {
        event.preventDefault();
        copyText(copyButton.getAttribute("data-copy-target"));
      }

      var revealButton = event.target.closest("[data-reveal-target]");
      if (revealButton) {
        event.preventDefault();
        revealSecret(revealButton.getAttribute("data-reveal-target"));
      }

      var reloadButton = event.target.closest("[data-reload-page]");
      if (reloadButton) {
        event.preventDefault();
        window.location.reload();
      }

      var toastButton = event.target.closest("[data-toast-message]");
      if (toastButton) {
        event.preventDefault();
        showToast(toastButton.getAttribute("data-toast-message") || "Saved.");
      }
    });

    document.addEventListener("submit", function (event) {
      var form = event.target;
      if (!form || !form.matches("form[data-confirm]")) return;

      var message = form.getAttribute("data-confirm");
      if (message && !window.confirm(message)) {
        event.preventDefault();
      }
    });
  }

  window.showToast = showToast;
  window.copyText = copyText;
  window.revealSecret = revealSecret;

  document.addEventListener("DOMContentLoaded", function () {
    localizeDatetimes();
    hydrateProgressBars();
  });
  attachDeclarativeHandlers();
})();
