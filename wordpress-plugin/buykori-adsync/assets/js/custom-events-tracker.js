(function () {
  'use strict';

  function getDataNode() {
    return document.getElementById('buykorigw-custom-events-data');
  }

  function parseEvents(node) {
    if (!node) {
      return [];
    }
    try {
      var parsed = JSON.parse(node.getAttribute('data-events') || '[]');
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      return [];
    }
  }

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : '';
  }

  function getQueryParam(name) {
    try {
      return new URLSearchParams(window.location.search).get(name) || '';
    } catch (error) {
      return '';
    }
  }

  function getGA4ClientId() {
    var ga = getCookie('_ga');
    if (!ga) {
      return '';
    }
    var parts = ga.split('.');
    return parts.length >= 4 ? parts[parts.length - 2] + '.' + parts[parts.length - 1] : '';
  }

  function getGA4SessionId() {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i += 1) {
      var cookie = cookies[i].trim();
      if (cookie.indexOf('_ga_') === 0) {
        var value = cookie.split('=')[1] || '';
        var parts = value.split('.');
        if (parts.length >= 3) {
          return parts[2];
        }
      }
    }
    return '';
  }

  function getFieldValue(selectors) {
    for (var i = 0; i < selectors.length; i += 1) {
      var field = document.querySelector(selectors[i]);
      if (field && field.value && String(field.value).trim()) {
        return String(field.value).trim();
      }
    }
    return '';
  }

  function appendCustomerData(formData) {
    var fields = {
      em: ['#billing_email', 'input[name="billing_email"]', 'input[type="email"]'],
      ph: ['#billing_phone', 'input[name="billing_phone"]', 'input[type="tel"]'],
      fn: ['#billing_first_name', 'input[name="billing_first_name"]'],
      ln: ['#billing_last_name', 'input[name="billing_last_name"]'],
      ct: ['#billing_city', 'input[name="billing_city"]'],
      st: ['#billing_state', 'select[name="billing_state"], input[name="billing_state"]'],
      zp: ['#billing_postcode', 'input[name="billing_postcode"]'],
      country: ['#billing_country', 'select[name="billing_country"], input[name="billing_country"]']
    };

    Object.keys(fields).forEach(function (key) {
      var value = getFieldValue(fields[key]);
      if (value) {
        formData.append(key, value);
      }
    });
  }

  function elementMatches(element, selector) {
    if (!selector || !element) {
      return false;
    }
    try {
      return Boolean(element.matches(selector) || element.closest(selector));
    } catch (error) {
      return false;
    }
  }

  function sendCustom(eventConfig) {
    var cfg = readTrackerConfig();
    if (!cfg.ajax_url) {
      return;
    }

    var eventId = 'wp_' + eventConfig.name + '_' + Math.floor(Date.now() / 1000) + '_' + Math.floor(Math.random() * 9000 + 1000);
    var data = {};
    if (eventConfig.value) {
      data.value = eventConfig.value;
    }
    if (eventConfig.currency) {
      data.currency = eventConfig.currency;
    }
    if (eventConfig.custom_param) {
      data.custom_param = eventConfig.custom_param;
    }

    var ga4ClientId = getGA4ClientId();
    var ga4SessionId = getGA4SessionId();
    if (ga4ClientId) {
      data._ga = ga4ClientId;
    }
    if (ga4SessionId) {
      data.ga_session_id = ga4SessionId;
    }

    var formData = new FormData();
    formData.append('action', 'buykorigw_track_event');
    formData.append('nonce', cfg.nonce);
    formData.append('event_name', eventConfig.name);
    formData.append('event_id', eventId);
    formData.append('event_data', JSON.stringify(data));
    formData.append('page_url', window.location.href);
    formData.append('fbp', getCookie('_fbp') || '');
    formData.append('fbc', getCookie('_fbc') || '');
    formData.append('ttp', getCookie('_ttp') || '');
    formData.append('ttclid', getQueryParam('ttclid') || getCookie('_ttclid') || '');
    appendCustomerData(formData);

    if (cfg.enable_hybrid) {
      if (window.fbq && cfg.fb_pixel_id) {
        window.fbq('trackCustom', eventConfig.name, data, { eventID: eventId });
      }
      if (window.ttq && cfg.tt_pixel_id) {
        window.ttq.track(eventConfig.name, data, { event_id: eventId });
      }
    }

    if (navigator.sendBeacon) {
      navigator.sendBeacon(cfg.ajax_url, formData);
    } else {
      fetch(cfg.ajax_url, { method: 'POST', body: formData, keepalive: true });
    }
  }

  function readTrackerConfig() {
    var node = document.getElementById('buykorigw-tracker-config');
    if (node) {
      try {
        return JSON.parse(node.getAttribute('data-config') || '{}');
      } catch (error) {}
    }
    return window.buykorigw_config || {};
  }

  function bindEvents(events) {
    events.forEach(function (eventConfig) {
      if (eventConfig.trigger === 'click' && eventConfig.selector) {
        document.addEventListener('click', function (event) {
          if (elementMatches(event.target, eventConfig.selector)) {
            sendCustom(eventConfig);
          }
        });
      } else if (eventConfig.trigger === 'url' && eventConfig.url_pattern) {
        if (window.location.href.indexOf(eventConfig.url_pattern) !== -1) {
          sendCustom(eventConfig);
        }
      } else if (eventConfig.trigger === 'form' && eventConfig.selector) {
        document.addEventListener('submit', function (event) {
          if (elementMatches(event.target, eventConfig.selector)) {
            sendCustom(eventConfig);
          }
        });
      } else if (eventConfig.trigger === 'timer' && eventConfig.selector) {
        var seconds = parseInt(eventConfig.selector, 10);
        if (seconds > 0) {
          window.setTimeout(function () {
            sendCustom(eventConfig);
          }, seconds * 1000);
        }
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindEvents(parseEvents(getDataNode()));
  });
})();
