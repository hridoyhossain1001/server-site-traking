(function () {
  'use strict';

  var root = document.querySelector('.ceb-wrap');
  if (!root) {
    return;
  }

  var list = document.getElementById('ceb-events-list');
  var status = document.getElementById('ceb-status');
  var events = parseEvents(root.getAttribute('data-ceb-events'));
  var nonce = root.getAttribute('data-ceb-nonce') || '';

  function parseEvents(raw) {
    try {
      var parsed = JSON.parse(raw || '[]');
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      return [];
    }
  }

  function eventDefaults() {
    return {
      name: '',
      trigger: 'click',
      selector: '',
      url_pattern: '',
      value: 0,
      currency: 'BDT',
      custom_param: '',
      enabled: true
    };
  }

  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (key) {
      if (key === 'class') {
        node.className = attrs[key];
      } else if (key === 'dataset') {
        Object.keys(attrs[key]).forEach(function (dataKey) {
          node.dataset[dataKey] = attrs[key][dataKey];
        });
      } else if (key === 'checked') {
        node.checked = Boolean(attrs[key]);
      } else {
        node.setAttribute(key, attrs[key]);
      }
    });
    if (text !== undefined) {
      node.textContent = text;
    }
    return node;
  }

  function field(labelText, input) {
    var wrap = el('div', { class: 'ceb-field' });
    wrap.appendChild(el('label', {}, labelText));
    wrap.appendChild(input);
    return wrap;
  }

  function hint(text) {
    return el('div', { class: 'ceb-hint' }, text);
  }

  function bindValue(input, index, key, transform, rerender) {
    input.addEventListener('change', function () {
      events[index][key] = transform ? transform(input.value) : input.value;
      if (rerender) {
        render();
      }
    });
  }

  function textInput(index, key, placeholder, type, transform) {
    var input = el('input', {
      type: type || 'text',
      value: events[index][key] || '',
      placeholder: placeholder || ''
    });
    bindValue(input, index, key, transform);
    return input;
  }

  function triggerSelect(index) {
    var select = el('select');
    [
      ['click', 'CSS Selector Click'],
      ['url', 'URL Pattern Match'],
      ['form', 'Form Submit'],
      ['timer', 'Time on Page (Timer)']
    ].forEach(function (option) {
      var opt = el('option', { value: option[0] }, option[1]);
      if (events[index].trigger === option[0]) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });
    bindValue(select, index, 'trigger', null, true);
    return select;
  }

  function render() {
    list.innerHTML = '';

    if (events.length === 0) {
      list.appendChild(el('div', { class: 'ceb-empty' }, 'No custom events yet. Click Add New Event.'));
      return;
    }

    events.forEach(function (eventConfig, index) {
      var card = el('div', { class: 'ceb-card' + (eventConfig.enabled ? '' : ' disabled') });
      var remove = el('button', { class: 'ceb-remove', type: 'button' }, 'Remove');
      remove.addEventListener('click', function () {
        if (!window.confirm('Remove this event?')) {
          return;
        }
        events.splice(index, 1);
        render();
      });
      card.appendChild(remove);

      var toggle = el('div', { class: 'ceb-toggle' });
      var toggleLabel = el('label');
      var checkbox = el('input', { type: 'checkbox', checked: eventConfig.enabled });
      checkbox.addEventListener('change', function () {
        events[index].enabled = checkbox.checked;
        render();
      });
      toggleLabel.appendChild(checkbox);
      toggleLabel.appendChild(document.createTextNode(' Active'));
      toggle.appendChild(toggleLabel);
      card.appendChild(toggle);

      var firstRow = el('div', { class: 'ceb-row' });
      var nameField = field('Event Name', textInput(index, 'name', 'e.g. WishlistAdd, CouponUsed'));
      nameField.appendChild(hint('Event name sent to the ad platform.'));
      firstRow.appendChild(nameField);
      firstRow.appendChild(field('Trigger Type', triggerSelect(index)));
      card.appendChild(firstRow);

      var secondRow = el('div', { class: 'ceb-row' });
      if (eventConfig.trigger === 'url') {
        var urlField = field('URL Pattern', textInput(index, 'url_pattern', '/thank-you/ or /success/'));
        urlField.appendChild(hint('Fire when the current URL contains this pattern.'));
        secondRow.appendChild(urlField);
      } else if (eventConfig.trigger === 'timer') {
        var timerField = field('Time (Seconds)', textInput(index, 'selector', '30', 'number'));
        timerField.appendChild(hint('Fire after the visitor stays this many seconds.'));
        secondRow.appendChild(timerField);
      } else {
        var selectorField = field('CSS Selector', textInput(index, 'selector', '.wishlist-btn, #apply-coupon'));
        selectorField.appendChild(hint('Fire when this element is clicked or submitted.'));
        secondRow.appendChild(selectorField);
      }
      var paramField = field('Custom Parameter', textInput(index, 'custom_param', 'e.g. coupon_code, video_name'));
      paramField.appendChild(hint('Optional custom_data parameter.'));
      secondRow.appendChild(paramField);
      card.appendChild(secondRow);

      var thirdRow = el('div', { class: 'ceb-row' });
      thirdRow.appendChild(field('Value (Amount)', textInput(index, 'value', '0.00', 'number', function (value) {
        return parseFloat(value) || 0;
      })));
      thirdRow.appendChild(field('Currency', textInput(index, 'currency', 'BDT')));
      card.appendChild(thirdRow);

      list.appendChild(card);
    });
  }

  function setStatus(type, message) {
    status.className = 'ceb-status is-visible ' + type;
    status.textContent = message;
  }

  function saveAll() {
    setStatus('is-saving', 'Saving...');

    var formData = new FormData();
    formData.append('action', 'buykorigw_save_custom_events');
    formData.append('nonce', nonce);
    formData.append('events', JSON.stringify(events));

    fetch(window.ajaxurl || '/wp-admin/admin-ajax.php', {
      method: 'POST',
      body: formData
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('HTTP ' + response.status);
        }
        return response.json();
      })
      .then(function (data) {
        if (data.success) {
          setStatus('is-success', 'All events saved.');
        } else {
          setStatus('is-error', 'Error: ' + (data.data || 'Save failed'));
        }
        setTimeout(function () {
          status.className = 'ceb-status';
          status.textContent = '';
        }, 3000);
      })
      .catch(function (error) {
        setStatus('is-error', 'Error: ' + error.message);
      });
  }

  root.addEventListener('click', function (event) {
    var action = event.target.getAttribute('data-ceb-action');
    if (action === 'add') {
      events.push(eventDefaults());
      render();
    } else if (action === 'save') {
      saveAll();
    }
  });

  render();
})();
