(function () {
  'use strict';

  function postManualConfirm(button) {
    var orderId = button.getAttribute('data-buykorigw-order-id');
    var nonce = button.getAttribute('data-buykorigw-nonce');

    if (!orderId || !nonce) {
      return;
    }

    if (!window.confirm('Send Purchase event again for order #' + orderId + '?')) {
      return;
    }

    var body = new URLSearchParams();
    body.append('action', 'buykorigw_manual_confirm');
    body.append('order_id', orderId);
    body.append('nonce', nonce);

    button.disabled = true;
    button.textContent = 'Sending...';

    fetch(window.ajaxurl || '/wp-admin/admin-ajax.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString()
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('HTTP ' + response.status);
        }
        return response.json();
      })
      .then(function (data) {
        if (data.success) {
          button.textContent = 'Sent';
          button.classList.add('buykorigw-manual-confirm-sent');
        } else {
          button.textContent = 'Failed';
          button.disabled = false;
        }
      })
      .catch(function () {
        button.textContent = 'Error';
        button.disabled = false;
      });
  }

  document.addEventListener('click', function (event) {
    var button = event.target.closest('.buykorigw-manual-confirm');
    if (!button) {
      return;
    }

    postManualConfirm(button);
  });
})();
