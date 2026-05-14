    const ranges = [...document.querySelectorAll('input[type="range"]')];
    const numbers = [...document.querySelectorAll('.number[data-for]')];
    const abuseValueEl = document.querySelector('#abuse-value');
    const tempValueEl = document.querySelector('#temp-value');
    const connectionStatusEl = document.querySelector('#connection-status');
    const connectorMenuEl = document.querySelector('#connector-menu');
    const unitMenuEl = document.querySelector('#unit-menu');
    const heatmap = document.querySelector('#heatmap');
    const events = document.querySelector('#events');
    const profileStatus = document.querySelector('#profile-status');
    const calibrationDetail = document.querySelector('#calibration-detail');

    const profileValues = {
      street: { takeoff: 72, handover: 64, torque: 58, pressure: 42, downshift: 62, kisspoint: 56, thermal: 66, ramp: 48, label: 'Street Smooth' },
      sport: { takeoff: 55, handover: 58, torque: 66, pressure: 62, downshift: 46, kisspoint: 52, thermal: 60, ramp: 58, label: 'Sport Balanced' },
      track: { takeoff: 35, handover: 50, torque: 78, pressure: 78, downshift: 34, kisspoint: 46, thermal: 74, ramp: 70, label: 'Track Firm' }
    };

    const calibrationGroups = {
      clutch: [
        ['K1/K2 balance', 'Odd/even clutch load split and handover symmetry'],
        ['Creep bite ramp', 'Low-speed bite-in shape for parking and traffic'],
        ['Kiss-point learn', 'Adaptation health and post-service relearn tracking']
      ],
      torque: [
        ['CAN torque honesty', 'Keeps gearbox model aligned with engine torque reporting'],
        ['Shift torque cut', 'Timing window for synchronization without harshness'],
        ['Limiter strategy', 'Soft ceiling model for tuned engine output']
      ],
      shift: [
        ['D-mode schedule', 'Earlier smooth shifts without lugging the gearbox'],
        ['S-mode schedule', 'Higher RPM targets with controlled pressure ramps'],
        ['Paddle response', 'Fast request handling with low-load damping']
      ],
      thermal: [
        ['Oil temp envelope', 'Heat rise prediction under repeated pulls'],
        ['Cool-down logic', 'Recovery gates before aggressive shift requests'],
        ['Abuse counter', 'Flags repeated slip, shock, and high-temp events']
      ]
    };

    function clamp(value) {
      return Math.max(0, Math.min(100, Number(value) || 0));
    }

    function values() {
      return Object.fromEntries(ranges.map((range) => [range.id, Number(range.value)]));
    }

    function setValue(id, value) {
      const safe = clamp(value);
      document.querySelector(`#${id}`).value = safe;
      document.querySelector(`[data-for="${id}"]`).value = safe;
    }

    function computeScore() {
      const v = values();
      const smooth = (v.takeoff * 0.19) + (v.handover * 0.18) + (v.torque * 0.13) + (v.downshift * 0.15) + (v.kisspoint * 0.12) + (v.thermal * 0.09) + ((100 - Math.abs(v.pressure - 55)) * 0.08) + ((100 - Math.abs(v.ramp - 55)) * 0.06);
      const abuse = clamp(100 - smooth + Math.max(0, v.pressure - 70) * 0.55 + Math.max(0, v.ramp - 72) * 0.28 + Math.max(0, 42 - v.takeoff) * 0.35 - v.thermal * 0.08);
      const slip = Math.max(2.1, 12 - (v.pressure * 0.08) - (v.handover * 0.035) - (v.kisspoint * 0.025) + (100 - v.torque) * 0.018);
      const temp = Math.round(4 + abuse * 0.22 + Math.max(0, v.pressure - 65) * 0.18 + Math.max(0, 48 - v.thermal) * 0.1);
      const comfort = clamp(Math.round(smooth - Math.max(0, v.pressure - 68) * 0.32 - Math.max(0, v.ramp - 76) * 0.25));
      const protection = clamp(Math.round(50 + v.pressure * 0.22 + v.torque * 0.13 + v.handover * 0.08 + v.thermal * 0.22 - abuse * 0.1));
      const health = clamp(Math.round(104 - abuse * 0.55 - slip * 0.9 - temp * 0.18));
      return { abuse: Math.round(abuse), slip, temp, comfort, protection, health };
    }

    function renderCalibrationGroup(group = 'clutch') {
      calibrationDetail.innerHTML = calibrationGroups[group].map(([title, body]) => `
        <div class="deep-card">
          <strong>${title}</strong>
          <span>${body}</span>
        </div>
      `).join('');
    }

    function renderHeatmap() {
      const v = values();
      const rows = ['Low', 'Mid', 'High'];
      const cells = ['Load', '1', '2', '3', '4', '5', '6', '7'].map((item) => `<div class="cell head">${item}</div>`);

      rows.forEach((row, rowIndex) => {
        cells.push(`<div class="cell head">${row}</div>`);
        for (let gear = 1; gear <= 7; gear += 1) {
          const base = 36 + rowIndex * 18 + gear * 2.8;
          const pressure = Math.round(base + v.pressure * 0.2 + v.ramp * 0.06 - v.takeoff * (rowIndex === 0 ? 0.12 : 0.03) + v.torque * 0.06 - v.thermal * 0.025);
          const tone = pressure > 72 ? 'map-high' : pressure > 56 ? 'map-mid' : 'map-low';
          cells.push(`<div class="cell ${tone}">${pressure}</div>`);
        }
      });

      heatmap.innerHTML = cells.join('');
    }

    function renderEvents(score) {
      const items = [
        ['Idle creep', score.comfort > 74 ? 'Low vibration predicted' : 'Review clutch bite ramp', score.comfort > 74 ? 'green' : 'amber'],
        ['2-3 upshift', score.abuse < 40 ? 'Clean torque handover' : 'Firm shift shock risk', score.abuse < 40 ? 'green' : 'red'],
        ['Kickdown', values().downshift > 48 ? 'Damped paddle response' : 'Aggressive request profile', values().downshift > 48 ? 'blue' : 'amber'],
        ['Thermal', score.temp < 16 ? 'Within modeled envelope' : 'Heat rise needs review', score.temp < 16 ? 'green' : 'red'],
        ['Adaptation', values().kisspoint > 48 ? 'Kiss-point model stable' : 'Learning pass recommended', values().kisspoint > 48 ? 'green' : 'amber']
      ];

      events.innerHTML = items.map(([time, text, tone]) => `
        <div class="event">
          <time>${time}</time>
          <span>${text}</span>
          <span class="pill ${tone}">${tone === 'green' ? 'OK' : tone === 'red' ? 'Risk' : 'Watch'}</span>
        </div>
      `).join('');
    }

    function update() {
      numbers.forEach((input) => {
        input.value = document.querySelector(`#${input.dataset.for}`).value;
      });
      const score = computeScore();
      document.querySelector('#abuse-value').innerHTML = `${score.abuse}<small>/100</small>`;
      document.querySelector('#slip-value').innerHTML = `${score.slip.toFixed(1)}<small>%</small>`;
      document.querySelector('#temp-value').innerHTML = `${score.temp}<small>C</small>`;
      document.querySelector('#comfort-value').innerHTML = `${score.comfort}<small>%</small>`;
      document.querySelector('#comfort-bar').style.width = `${score.comfort}%`;
      document.querySelector('#protect-bar').style.width = `${score.protection}%`;
      document.querySelector('#health-value').textContent = score.health;
      document.querySelector('#needle').style.transform = `rotate(${(score.health / 100) * 170 - 85}deg)`;
      renderHeatmap();
      renderEvents(score);
    }

    ranges.forEach((range) => {
      range.addEventListener('input', update);
    });

    numbers.forEach((input) => {
      input.addEventListener('input', () => {
        setValue(input.dataset.for, input.value);
        update();
      });
    });

    document.querySelectorAll('[data-profile]').forEach((button) => {
      button.addEventListener('click', () => {
        document.querySelectorAll('[data-profile]').forEach((item) => item.classList.remove('active'));
        button.classList.add('active');
        const profile = profileValues[button.dataset.profile];
        Object.entries(profile).forEach(([key, value]) => {
          if (key !== 'label') setValue(key, value);
        });
        profileStatus.textContent = profile.label;
        update();
      });
    });

    document.querySelectorAll('[data-cal]').forEach((button) => {
      button.addEventListener('click', () => {
        document.querySelectorAll('[data-cal]').forEach((item) => item.classList.remove('active'));
        button.classList.add('active');
        renderCalibrationGroup(button.dataset.cal);
      });
    });

    let toolkitConn = {
      active: false,
      abort: null,
    };

    async function connectToolkitStream({
      url,
      onSnapshot,
      onError,
    }) {
      toolkitConn.abort?.abort?.();
      const controller = new AbortController();
      toolkitConn.abort = controller;

      const resp = await fetch(url, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        signal: controller.signal,
      });

      if (!resp.ok || !resp.body) {
        throw new Error(`Toolkit stream HTTP ${resp.status}`);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';

      while (!controller.signal.aborted) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });

        // newline-delimited JSON
        let idx;
        while ((idx = buf.indexOf('\n')) >= 0) {
          const line = buf.slice(0, idx).trim();
          buf = buf.slice(idx + 1);
          if (!line) continue;

          try {
            const msg = JSON.parse(line);
            if (msg.type === 'snapshot') {
              onSnapshot(msg);
            }
          } catch (e) {
            // ignore partial/non-JSON
          }
        }
      }
    }

    function applyToolkitSnapshot(msg) {
      const oilTemp = msg.oil_temp_c;
      const k1 = msg.k1_clutch_pressure_candidate_bar;
      const k2 = msg.k2_clutch_pressure_candidate_bar;
      const rpm = msg.rpm;

      // Abuse index now primarily reacts to oil temp >= 130C
      // We keep existing slider-based score, but override the displayed values when stream exists.
      if (oilTemp !== null && oilTemp !== undefined && !Number.isNaN(oilTemp)) {
        const metricUnits = unitMenuEl.value === 'metric';
        const displayTemp = metricUnits ? oilTemp : (oilTemp * 9 / 5) + 32;
        const tempUnit = metricUnits ? 'C' : 'F';
        tempValueEl.innerHTML = `${Math.round(displayTemp)}<small>${tempUnit}</small>`;

        const abuseEl = abuseValueEl;
        const shouldGlow = oilTemp >= 130;

        // map oil temp to abuse index (0..100), tuned for UI prototyping
        const abuse = clamp(Math.round((oilTemp - 70) * 1.2));
        abuseEl.innerHTML = `${abuse}<small>/100</small>`;

        // glow red behavior: when >=130C turn abuse index card to red
        const card = abuseEl.closest('.card');
        const gauge = document.querySelector('.gauge');
        if (card) {
          card.classList.toggle('hot-abuse', shouldGlow);
        }
        if (gauge) {
          gauge.classList.toggle('hot-health', shouldGlow);
        }
        if (msg.abuse_index !== null && msg.abuse_index !== undefined && !Number.isNaN(msg.abuse_index)) {
          document.querySelector('#health-value').textContent = Math.max(0, Math.min(100, Math.round(100 - msg.abuse_index * 0.42)));
        }

        // also feed "thermal" slider as a visual proxy without changing calibration values
        // (keeps UI consistent while not claiming the slider is a real parameter write)
        if (shouldGlow) {
          // no-op for now
        }
      }

      if (k1 !== null && k1 !== undefined && !Number.isNaN(k1)) {
        // show clutch slip proxy as existing UI field
        // (proto only; not raw ECU units)
      }
      if (k2 !== null && k2 !== undefined && !Number.isNaN(k2)) {
        // no-op
      }

      renderEvents(computeScore());
    }

        document.querySelector('#simulate').addEventListener('click', async () => {
      if (toolkitConn.active) return;
      toolkitConn.active = true;
      try {
        const url = 'http://127.0.0.1:8765/stream';
        connectionStatusEl.textContent = `Connecting via ${connectorMenuEl.value}`;
        connectionStatusEl.className = 'pill blue';
        document.querySelector('#simulate').classList.add('locked');
        await connectToolkitStream({
          url,
          onSnapshot: (msg) => {
            connectionStatusEl.textContent = `Live ${connectorMenuEl.value}`;
            connectionStatusEl.className = 'pill green';
            applyToolkitSnapshot(msg);
          },
          onError: (e) => console.error(e),
        });
      } catch (e) {
        console.error(e);
        connectionStatusEl.textContent = 'Toolkit offline';
        connectionStatusEl.className = 'pill red';
      } finally {
        toolkitConn.active = false;
        document.querySelector('#simulate').classList.remove('locked');
      }
    });

    function showPage(page) {
      document.querySelectorAll('[data-page-panel]').forEach((panel) => {
        panel.classList.toggle('active', panel.dataset.pagePanel === page);
      });
      document.querySelectorAll('[data-page]').forEach((button) => {
        button.classList.toggle('active', button.dataset.page === page);
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    document.querySelectorAll('[data-page]').forEach((button) => {
      button.addEventListener('click', () => showPage(button.dataset.page));
    });

    document.querySelectorAll('[data-page-jump]').forEach((button) => {
      button.addEventListener('click', () => showPage(button.dataset.pageJump));
    });

    document.querySelector('#torque-simulate').addEventListener('click', () => {
      setValue('torque', clamp(Number(document.querySelector('#torque').value) + 6));
      setValue('pressure', clamp(Number(document.querySelector('#pressure').value) + 5));
      setValue('ramp', clamp(Number(document.querySelector('#ramp').value) + 4));
      update();
      showPage('dashboard');
    });

    function exportReviewPack() {
      const score = computeScore();
      const payload = {
        vehicle: document.querySelector('#vehicle-menu').value,
        features: {
          fit_statement: 'Supported vehicle fit statement',
          feature_list: [
            'Optimized part throttle drive and sport maps',
            'Optimized wide open throttle drive and sport maps',
            'Increased clutch pressure',
            'Increased clutch torque limits',
            'Manual downshift lockout limit increased',
            'Improved paddle response',
            'Improved shift times and advanced AMAX mode',
            'Increased maximum RPM',
            'Reduced pull-away delay',
            'Customizable auto up-shift behavior',
            'Customizable launch control',
            'Improved launch control response',
            'Launch control enabled with stability control',
            'Launch counter',
            'Gear display active in drive and sport',
            'Direct Port Programming â€“ easy install through the OBD II port without removing the ECU',
            'Free updates included for the supported lifecycle',
            '30-day satisfaction guarantee'
          ]
        },
        gearbox: 'VW Group DSG/S tronic family',
        mechatronic: '0BH 927 711 X',
        clutch_architecture: {
          K1: ['1st gear', '3rd gear', '5th gear', '7th gear'],
          K2: ['2nd gear', '4th gear', '6th gear', 'Reverse']
        },
        uds_profile: {
          config: 'configs/dq500_readonly.yaml',
          tx_id: '0x7E1',
          rx_id: '0x7E9',
          bitrate: 500000,
          session_request: '02 10 03 00 00 00 00 00',
          success_response: '02 50 03',
          dids: [
            { did: '0x1901', signal: 'k1_clutch_pressure_candidate', request: '03 22 19 01 00 00 00 00' },
            { did: '0x1902', signal: 'k2_clutch_pressure_candidate', request: '03 22 19 02 00 00 00 00' },
            { did: '0x1905', signal: 'gearbox_oil_pressure_or_temp_candidate', request: '03 22 19 05 00 00 00 00' }
          ]
        },
        mode: 'offline-review-only',
        safety_boundary: 'read-only diagnostics; SecurityAccess and write/flash services blocked',
        controls: values(),
        score
      };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'vw-tcu-review-pack.json';
      link.click();
      URL.revokeObjectURL(url);
    }

    document.querySelector('#export').addEventListener('click', exportReviewPack);
    document.querySelector('#export-page-button').addEventListener('click', exportReviewPack);

    renderCalibrationGroup();
    update();

