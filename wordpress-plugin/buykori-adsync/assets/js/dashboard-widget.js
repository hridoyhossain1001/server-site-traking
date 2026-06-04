(function () {
  'use strict';

  var root = document.querySelector('.cgw-wrap');
  var content = document.getElementById('cgw-content');

  if (!root || !content) {
    return;
  }

  function escapeText(value) {
    var div = document.createElement('div');
    div.textContent = value == null ? '' : String(value);
    return div.innerHTML;
  }

  function numberValue(value) {
    var number = Number(value);
    return Number.isFinite(number) ? number : 0;
  }

  function money(value) {
    return 'BDT ' + numberValue(value).toLocaleString();
  }

  function showError(message) {
    content.innerHTML = '<div class="cgw-loading cgw-loading-error">' + escapeText(message) + '</div>';
  }

  function stat(className, value, label, valueClass) {
    return '<div class="cgw-stat ' + className + '"><div class="num ' + (valueClass || '') + '">' + value + '</div><div class="label">' + label + '</div></div>';
  }

  function render(data) {
    var html = '';
    html += '<div class="cgw-conn ' + (data.server_online ? 'online' : 'offline') + '">';
    html += '<span class="dot"></span>';
    html += data.server_online ? 'Server Connected' : 'Server Offline';
    html += '</div>';

    if (numberValue(data.pending_orders) > 0) {
      html += '<div class="cgw-risk">';
      html += '<div class="cgw-risk-head">';
      html += '<div><div class="cgw-risk-title">Pending revenue at risk</div>';
      html += '<div class="cgw-risk-value">' + money(data.pending_value) + '</div></div>';
      html += '<div class="cgw-risk-count">' + numberValue(data.pending_orders) + ' COD</div>';
      html += '</div>';
      html += '<div class="cgw-risk-meta">These orders are held until verification, so fake or cancelled COD orders do not train Meta/TikTok.';
      if (numberValue(data.pending_oldest_age_hours) > 0) {
        html += '<br>Oldest pending order: ' + numberValue(data.pending_oldest_age_hours) + 'h';
      }
      html += '</div></div>';
    }

    html += '<div class="cgw-stats">';
    html += stat('info', numberValue(data.total_today), "Today's Events");
    html += stat('success', numberValue(data.success_rate) + '%', 'Success Rate');
    html += stat('warning', numberValue(data.pending_orders), 'Pending COD');
    html += stat('success', numberValue(data.verified_purchases), 'Verified Purchases');
    html += stat('error', numberValue(data.cancelled_or_expired), 'Cancelled / Expired');
    html += stat('warning', money(data.pending_value), 'Revenue At Risk', 'num-small');
    html += stat('', numberValue(data.total_month), 'This Month');
    html += '</div>';

    if (numberValue(data.pending_oldest_age_hours) >= 24) {
      html += '<div class="cgw-alert">Oldest COD order is ' + numberValue(data.pending_oldest_age_hours) + 'h pending. Confirm or cancel it so ad platforms learn from verified purchases only.</div>';
    }

    if (data.top_events && data.top_events.length > 0) {
      html += '<div class="cgw-events"><strong class="cgw-events-title">Top Events (Today)</strong>';
      data.top_events.forEach(function (eventItem) {
        html += '<div class="cgw-event-row"><span class="cgw-event-name">' + escapeText(eventItem.name) + '</span><span class="cgw-event-count">' + numberValue(eventItem.count) + '</span></div>';
      });
      html += '</div>';
    }

    content.innerHTML = html;
  }

  function load() {
    var formData = new FormData();
    formData.append('action', 'buykorigw_widget_data');
    formData.append('nonce', root.getAttribute('data-cgw-nonce') || '');

    fetch(window.ajaxurl || '/wp-admin/admin-ajax.php', { method: 'POST', body: formData })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('HTTP ' + response.status);
        }
        return response.json();
      })
      .then(function (response) {
        if (!response.success) {
          showError(response.data || 'Error loading data');
          return;
        }
        render(response.data);
      })
      .catch(function () {
        showError('Network error');
      });
  }

  load();
})();
