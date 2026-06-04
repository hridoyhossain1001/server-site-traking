(function () {
  'use strict';

  var root = document.querySelector('.buykorigw-wrap');
  var config = root ? root.dataset : {};
  var ajaxUrl = config.buykorigwAjaxUrl || window.ajaxurl || '/wp-admin/admin-ajax.php';
  var storageKey = 'buykorigw_active_tab';

  function text(key, fallback) {
    if (key === 'disconnectConfirm' && config.buykorigwDisconnectMessage) {
      return config.buykorigwDisconnectMessage;
    }
    return fallback;
  }

  function setStatus(status, type, message) {
    if (!status) {
      return;
    }
    status.className = 'buykorigw-status' + (type ? ' ' + type : '');
    status.textContent = message;
    status.style.display = 'block';
  }

  function resetStatus(status) {
    if (!status) {
      return;
    }
    status.className = 'buykorigw-status';
    status.textContent = '';
    status.style.display = 'none';
  }

  function restoreButton(button, label) {
    if (!button) {
      return;
    }
    button.disabled = false;
    button.textContent = label;
  }

  function postAdminAjax(action, fields) {
    var formData = new FormData();
    formData.append('action', action);
    formData.append('nonce', config.buykorigwNonce || '');

    Object.keys(fields || {}).forEach(function (key) {
      formData.append(key, fields[key]);
    });

    return fetch(ajaxUrl, {
      method: 'POST',
      body: formData
    }).then(function (response) {
      if (!response.ok) {
        throw new Error('HTTP ' + response.status);
      }
      return response.json();
    });
  }

  function bindTabs() {
    var tabs = document.querySelectorAll('.buykorigw-nav-tab');
    var panels = document.querySelectorAll('.buykorigw-tab-content');

    function switchTab(tabName) {
      tabs.forEach(function (tab) {
        tab.classList.remove('active');
      });
      panels.forEach(function (panel) {
        panel.classList.remove('active');
      });

      var activeTab = document.querySelector('.buykorigw-nav-tab[data-tab="' + tabName + '"]');
      var activePanel = document.getElementById('tab-' + tabName);
      if (activeTab) {
        activeTab.classList.add('active');
      }
      if (activePanel) {
        activePanel.classList.add('active');
      }

      try {
        window.localStorage.setItem(storageKey, tabName);
      } catch (error) {}
    }

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        switchTab(tab.getAttribute('data-tab'));
      });
    });

    try {
      var saved = window.localStorage.getItem(storageKey);
      if (saved && document.getElementById('tab-' + saved)) {
        switchTab(saved);
      }
    } catch (error) {}
  }

  function bindDisconnectConfirm() {
    document.querySelectorAll('[data-buykorigw-disconnect-confirm]').forEach(function (link) {
      link.addEventListener('click', function (event) {
        if (!window.confirm(text('disconnectConfirm', 'Disconnect this WordPress site from Buykori AdSync?'))) {
          event.preventDefault();
        }
      });
    });
  }

  function bindHealthCheck() {
    var button = document.getElementById('buykorigw-test-btn');
    if (!button) {
      return;
    }

    button.addEventListener('click', function () {
      var status = document.getElementById('buykorigw-test-status');
      var apiKeyField = document.getElementById('buykorigw_api_key');
      var gatewayUrlField = document.getElementById('buykorigw_gateway_url');
      var apiKey = apiKeyField ? apiKeyField.value.trim() : '';
      var gatewayUrl = gatewayUrlField ? gatewayUrlField.value.trim() : '';

      button.disabled = true;
      button.textContent = text('healthTesting', 'Testing...');
      resetStatus(status);

      if (!apiKey || !gatewayUrl) {
        setStatus(status, 'error', text('apiKeyRequired', 'Please connect your Buykori account first.'));
        restoreButton(button, text('healthDefault', 'Run Health Check'));
        return;
      }

      postAdminAjax('buykorigw_test_connection', {
        api_key: apiKey,
        gateway_url: gatewayUrl
      }).then(function (data) {
        if (data.success) {
          setStatus(status, 'success', 'OK: ' + data.data);
        } else {
          setStatus(status, 'error', data.data || text('unknownError', 'Unknown error'));
        }
      }).catch(function (error) {
        setStatus(status, 'error', text('networkError', 'Network error: ') + error.message);
      }).finally(function () {
        restoreButton(button, text('healthDefault', 'Run Health Check'));
      });
    });
  }

  function bindUpdateCheck() {
    var button = document.getElementById('buykorigw-update-btn');
    if (!button) {
      return;
    }

    button.addEventListener('click', function () {
      var status = document.getElementById('buykorigw-update-status');
      button.disabled = true;
      button.textContent = text('updateChecking', 'Checking...');
      resetStatus(status);

      postAdminAjax('buykorigw_check_update_now')
        .then(function (data) {
          if (data.success) {
            setStatus(status, 'success', 'OK: ' + data.data);
          } else {
            setStatus(status, 'error', data.data || text('unknownError', 'Unknown error'));
          }
        })
        .catch(function (error) {
          setStatus(status, 'error', text('networkError', 'Network error: ') + error.message);
        })
        .finally(function () {
          restoreButton(button, text('updateDefault', 'Refresh Update Status'));
        });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindTabs();
    bindDisconnectConfirm();
    bindHealthCheck();
    bindUpdateCheck();
  });
})();
