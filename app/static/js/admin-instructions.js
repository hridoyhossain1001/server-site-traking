(function () {
  function activateTab(tabId, button) {
    document.querySelectorAll(".tab-content").forEach(function (panel) {
      panel.classList.remove("active");
    });
    document.querySelectorAll(".tab-btn").forEach(function (tabButton) {
      tabButton.classList.remove("active");
    });

    var panel = document.getElementById(tabId);
    if (panel) panel.classList.add("active");
    if (button) button.classList.add("active");
  }

  function generatedEventMapping(eventName) {
    var events = {
      page_view: ["PageView", ""],
      session_start: ["PageView", ", {custom_event: 'session_start'}"],
      user_signup: ["CompleteRegistration", ""],
      user_login: ["Login", ""],
      view_item: ["ViewContent", ", {value: 100, currency: 'BDT', content_ids: ['ID-123'], content_type: 'product'}"],
      add_to_cart: ["AddToCart", ", {value: 100, currency: 'BDT', content_ids: ['ID-123']}"],
      begin_checkout: ["InitiateCheckout", ", {value: 500, currency: 'BDT'}"],
      purchase: ["Purchase", ", {value: 1500, currency: 'BDT', content_ids: ['ID-123'], order_id: 'ORD-001'}"],
      lead: ["Lead", ""]
    };
    return events[eventName] || events.page_view;
  }

  function generateEventCode() {
    var selector = document.getElementById("event_selector");
    var output = document.getElementById("generated_code_box");
    var area = document.getElementById("code_result_area");
    if (!selector || !output || !area) return;

    var eventName = selector.value;
    var mapping = generatedEventMapping(eventName);
    var code = "<script>\n  // Event: " + eventName + "\n  capi('track', '" + mapping[0] + "'" + mapping[1] + ");\n</scr" + "ipt>";

    output.innerText = code;
    area.classList.add("is-visible");
  }

  document.addEventListener("click", function (event) {
    var tabButton = event.target.closest("[data-tab-target]");
    if (tabButton) {
      event.preventDefault();
      activateTab(tabButton.getAttribute("data-tab-target"), tabButton);
      return;
    }

    if (event.target.closest("[data-generate-event-code]")) {
      event.preventDefault();
      generateEventCode();
    }
  });
})();
