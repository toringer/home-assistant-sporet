/* device-sensors-badges-card.js
 * - Inline SVGs (bundled in this file)
 * - device_id -> sensors via entity_registry/list
 * - reads 2 sensor values + boolean attributes from one sensor
 * - colors an icon based on primary sensor numeric ranges
 */

const CARD_TAG = "sporet.no-card";


// Discrete status value → color mapping
const STATUS_COLORS = {
  20: "#00F700", // LightGreen
  21: "#00F700",

  30: "#008026", // DarkGreen
  31: "#008026",

  40: "#FB9F06", // Orange
  41: "#FB9F06",

  50: "#BB63C5", // Purple
  51: "#BB63C5",

  60: "#FF5767", // LightRed
  61: "#FF5767",

  70: "#A0A0A0", // DarkGrey
  71: "#A0A0A0",
};

const DEFAULT_STATUS_COLOR = "#AAAAAA"; // Grey

const STATUS_LABELS = {
  20: "0-6 t",
  21: "0-6 t",

  30: "6-18 t",
  31: "6-18 t",

  40: "18-48 t",
  41: "18-48 t",

  50: "2-14 d",
  51: "2-14 d",

  60: "14+ dager",
  61: "14+ dager",

  70: "Ingen",
  71: "Ingen",
};

const DEFAULT_STATUS_LABEL = "Ukjent";


// 1) PASTE YOUR SVGs HERE (keep them as full <svg ...>...</svg> elements).
// Tip: remove width/height from the SVG if you want CSS to control it.
const INLINE_SVGS = {
  has_skating: `
    <!-- PASTE has_skating.svg CONTENT HERE -->
    <svg xmlns='http://www.w3.org/2000/svg' width='25' height='25' viewBox='0 0 25 25' fill='none'><g clip-path='url(%23clip0_4430_12870)'><path d='M19.3812 5.83423C18.238 5.83423 17.3078 6.76436 17.3078 7.90764C17.3078 9.05092 18.238 9.98105 19.3812 9.98105C20.5245 9.98105 21.4546 9.05092 21.4546 7.90764C21.4546 6.76436 20.5245 5.83423 19.3812 5.83423ZM10.6729 7.90764C10.1342 7.90764 9.8281 8.21106 9.57141 8.46568L7.77661 10.3795L3.74237 9.1695C3.70281 9.15694 3.66158 9.15039 3.62007 9.15007C3.52008 9.14988 3.42339 9.18583 3.34781 9.25129C3.27222 9.31675 3.22283 9.40732 3.20873 9.50631C3.19464 9.6053 3.21678 9.70605 3.27108 9.79001C3.32538 9.87397 3.40819 9.93549 3.50425 9.96323L7.35464 11.1182C7.34039 11.196 7.33288 11.2756 7.33358 11.3563C7.33649 11.688 7.46937 11.9996 7.70615 12.2318C7.94086 12.462 8.24881 12.5882 8.57682 12.5882C8.58055 12.5882 8.58482 12.5878 8.58897 12.5874C8.92154 12.5845 9.23252 12.4522 9.47179 12.2083L11.1718 10.3957H12.3268C11.7143 11.0775 11.1915 11.6842 10.766 12.2067C10.5666 12.4522 9.26904 14.6896 8.83114 15.4472C8.63458 15.6384 7.97589 16.296 5.58981 18.7015C5.10961 19.1913 5.1175 19.9813 5.60682 20.4607C5.63749 20.4908 5.67256 20.5136 5.70563 20.5401L3.74237 19.9512C3.70281 19.9387 3.66158 19.9321 3.62007 19.9318C3.52008 19.9316 3.42339 19.9676 3.34781 20.033C3.27222 20.0985 3.22283 20.1891 3.20873 20.288C3.19464 20.387 3.21678 20.4878 3.27108 20.5717C3.32538 20.6557 3.40819 20.7172 3.50425 20.745L15.9447 24.4771C15.9976 24.4955 16.0536 24.503 16.1095 24.4991C16.1653 24.4953 16.2198 24.4802 16.2696 24.4547C16.3194 24.4292 16.3636 24.3939 16.3995 24.3509C16.4353 24.308 16.4621 24.2582 16.4781 24.2045C16.4942 24.1509 16.4993 24.0946 16.493 24.039C16.4868 23.9834 16.4693 23.9296 16.4417 23.8809C16.4141 23.8322 16.377 23.7896 16.3325 23.7557C16.288 23.7217 16.2371 23.6971 16.1828 23.6834L6.59007 20.8057C6.88369 20.7795 7.15709 20.6563 7.36436 20.4453C10.0689 17.7246 10.6783 17.0921 10.83 16.9229H10.8308C12.1798 15.5624 15.7932 11.9457 16.3124 11.5564C17.1463 10.9314 17.4759 10.1276 17.2171 9.35174C16.9293 8.48795 15.9663 7.90764 14.8197 7.90764H10.6729ZM15.0781 13.8711L13.3076 15.6198L14.405 16.7164V19.5187C14.405 19.6649 14.4347 19.803 14.4812 19.9334H10.2582C10.2033 19.9326 10.1487 19.9428 10.0977 19.9633C10.0467 19.9838 10.0003 20.0142 9.96119 20.0528C9.92205 20.0914 9.89098 20.1373 9.86977 20.188C9.84856 20.2387 9.83764 20.2931 9.83764 20.3481C9.83764 20.4031 9.84856 20.4575 9.86977 20.5082C9.89098 20.5589 9.92205 20.6048 9.96119 20.6434C10.0003 20.682 10.0467 20.7124 10.0977 20.7329C10.1487 20.7534 10.2033 20.7636 10.2582 20.7628H15.6491H22.284C22.339 20.7636 22.3935 20.7534 22.4445 20.7329C22.4955 20.7124 22.5419 20.682 22.581 20.6434C22.6202 20.6048 22.6513 20.5589 22.6725 20.5082C22.6937 20.4575 22.7046 20.4031 22.7046 20.3481C22.7046 20.2931 22.6937 20.2387 22.6725 20.188C22.6513 20.1373 22.6202 20.0914 22.581 20.0528C22.5419 20.0142 22.4955 19.9838 22.4445 19.9633C22.3935 19.9428 22.339 19.9326 22.284 19.9334H16.817C16.8635 19.803 16.8931 19.6649 16.8931 19.5187V16.2013C16.8931 15.8235 16.719 15.4657 16.4242 15.2302C16.3977 15.1958 16.3687 15.1617 16.3359 15.1289L15.0781 13.8711Z' fill='%23425E87'/></g><defs><clipPath id='clip0_4430_12870'><rect width='24' height='24' fill='white' transform='translate(0.95459 0.5)'/></clipPath></defs></svg>
  `,
  has_classic: `
    <!-- PASTE has_classic.svg CONTENT HERE -->
    <svg xmlns='http://www.w3.org/2000/svg' width='25' height='25' viewBox='0 0 25 25' fill='none'><path fill-rule='evenodd' clip-rule='evenodd' d='M13.3833 1.82818C13.7307 1.4808 14.2019 1.28564 14.6931 1.28564C15.1844 1.28564 15.6555 1.4808 16.0029 1.82818C16.3503 2.17556 16.5455 2.64671 16.5455 3.13797C16.5455 3.62924 16.3503 4.10039 16.0029 4.44777C15.6555 4.79515 15.1844 4.9903 14.6931 4.9903C14.2019 4.9903 13.7307 4.79515 13.3833 4.44777C13.0359 4.10039 12.8408 3.62924 12.8408 3.13797C12.8408 2.64671 13.0359 2.17556 13.3833 1.82818ZM11.9259 6.15283C12.2132 5.93303 12.5658 5.81356 12.9276 5.81356H13.8594H13.861H13.8699C14.252 5.81356 14.6184 5.96535 14.8886 6.23553C15.1588 6.50572 15.3106 6.87217 15.3106 7.25426C15.3104 7.3934 15.2901 7.53178 15.2503 7.66509L15.2511 7.6675L14.0757 12.402L15.6104 15.0141L16.4329 18.7236C16.5069 18.8685 16.5454 19.0288 16.5455 19.1915C16.5455 19.3266 16.5188 19.4605 16.4671 19.5853C16.4154 19.7102 16.3396 19.8236 16.244 19.9192C16.2362 19.927 16.2282 19.9348 16.2201 19.9423H18.6238C18.6098 19.8994 18.603 19.8543 18.6036 19.8089V11.0747L16.3839 10.4396L15.6153 9.58656L16.1081 7.57826C16.1146 7.53363 16.1173 7.48813 16.12 7.44256C16.1211 7.42508 16.1221 7.40759 16.1234 7.39013L17.232 8.96108L19.2854 9.56405L19.2846 9.56646C19.606 9.67842 19.8385 9.98172 19.8385 10.3415C19.8385 10.6457 19.672 10.908 19.4269 11.0506V19.8089C19.4275 19.8543 19.4206 19.8994 19.4066 19.9423H21.3352C21.4157 19.9423 21.4957 19.9315 21.5733 19.91L22.2335 19.7275C22.4704 19.662 22.7046 19.8402 22.7046 20.086C22.7046 20.2532 22.593 20.3999 22.4318 20.4445L21.6453 20.6619C21.52 20.6966 21.3905 20.7142 21.2605 20.7142H3.59049C3.37736 20.7142 3.20459 20.5414 3.20459 20.3283C3.20459 20.1151 3.37736 19.9423 3.59049 19.9423H4.21857C4.20168 19.893 4.19432 19.8409 4.19689 19.7887C4.19956 19.7347 4.21284 19.6818 4.23598 19.6329L7.76296 12.1874C7.67715 12.1104 7.60848 12.0162 7.56139 11.9109C7.5143 11.8057 7.48985 11.6917 7.48962 11.5764C7.48986 11.4203 7.53447 11.2675 7.61825 11.1358L8.77998 8.39428L8.784 8.38866C8.84174 8.24523 8.9387 8.12097 9.06377 8.03009L9.06458 8.02928L9.0686 8.02687C9.0876 8.01318 9.10718 8.0003 9.12729 7.98828L11.9259 6.15283ZM5.00066 19.9423H8.63813C8.43793 19.7546 8.31287 19.4877 8.31287 19.1915C8.31287 18.9054 8.42946 18.6472 8.61758 18.4607L10.5792 15.9314L10.9651 13.9955L12.643 15.6685L12.2748 17.0481L10.2287 19.7141L10.2255 19.7117C10.1752 19.7971 10.1131 19.8748 10.0414 19.9423H14.8139C14.7188 19.8532 14.6411 19.7464 14.5854 19.6273L14.5814 19.6289L14.5765 19.6088C14.5206 19.4828 14.4905 19.347 14.4881 19.2092L13.7115 15.724L11.8173 13.6803C11.6808 13.571 11.5596 13.4445 11.4636 13.2977L11.4596 13.2936L11.4588 13.2896C11.293 13.0327 11.1943 12.7281 11.1943 12.3996C11.1943 12.2489 11.2215 12.1058 11.2594 11.9671L11.2578 11.9591C11.2578 11.9591 11.7644 9.61563 12.0352 8.35811L10.1564 9.433L9.1088 11.7814C9.07574 11.91 9.01204 12.0288 8.92315 12.1275C8.83425 12.2262 8.72279 12.3019 8.59828 12.3482L5.00066 19.9423Z' fill='%23425E87'/></svg>
  `,
  is_scooter_trail: `
    <!-- PASTE is_scooter_trail.svg CONTENT HERE -->
    <svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32' fill='none'><path fill-rule='evenodd' clip-rule='evenodd' d='M1.31805 12.2711C1.48087 11.5482 2.54415 10.7199 4.17288 11.7512L8.25666 13.1425H12.7906C12.7906 13.1425 13.557 12.2711 14.6807 11.7512H17.8763L14.0719 8.88596C13.844 8.08599 14.6807 7.94464 14.6807 7.94464L19.286 11.2818L18.5494 8.88596C18.5494 8.88596 18.2777 8.13425 19.0891 7.74068C19.9005 7.34712 20.6096 7.94464 20.6096 7.94464C20.6096 7.94464 21.4345 9.24245 23.4383 12.2711C29.2902 15.1043 29.1107 16.6858 29.1107 16.6858C29.1107 16.6858 29.1107 19.3474 24.0949 20.4828L25.4023 22.4527L30.2059 19.5443C30.2059 19.5443 31.1492 19.5443 30.9796 20.4828L26.0386 23.8821H17.1439C16.4145 23.1084 17.1439 22.4527 17.1439 22.4527H22.705L21.255 20.4828L14.8752 20.0115C14.8752 20.0115 15.0363 22.941 12.4839 23.8821C9.68064 24.9158 3.95812 24.0627 3.95812 24.0627C2.16735 23.8821 -0.996019 20.1701 2.75099 17.1605C0.505171 15.5574 1.15523 12.994 1.31805 12.2711ZM3.76242 19.1604C4.97542 19.1604 8.44652 19.1604 8.44652 19.1604C8.44652 19.1604 10.9174 19.6065 12.9402 20.4038C13.0373 22.0873 12.3141 22.535 12.3141 22.535C12.3141 22.535 4.43798 22.5894 3.76242 22.345C2.95219 22.345 2.27318 19.6845 3.76242 19.1604Z' fill='%23425E87'/></svg>
  `,
};

// Minimal “Lit” access pattern compatible with HA frontend builds
const getHaLit = () => {
  const p = customElements.get("ha-panel-lovelace");
  const base = p ? Object.getPrototypeOf(p) : HTMLElement;
  const LitElement = base?.prototype?.constructor ?? HTMLElement;
  const html =
    LitElement.prototype?.html ??
    ((strings, ...vals) => strings.reduce((acc, s, i) => acc + s + (vals[i] ?? ""), ""));
  const css = LitElement.prototype?.css ?? ((s) => s);
  return { LitElement, html, css };
};

const { LitElement, html, css } = getHaLit();

class DeviceSensorsBadgesCard extends LitElement {
  static get properties() {
    return {
      hass: {},
      _config: {},
      _deviceName: { state: true },
      _entityIds: { state: true },
      _error: { state: true },
    };
  }

  static get styles() {
    return css`
      .card {
        padding: 16px;
      }
      .row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .left {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 0;
      }
      .title {
        font-size: 14px;
        font-weight: 600;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .sub {
        font-size: 12px;
        opacity: 0.8;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .value {
        font-size: 20px;
        font-weight: 700;
        line-height: 1;
        text-align: right;
        white-space: nowrap;
      }
      .badges {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 10px;
        flex-wrap: wrap;
      }
      .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(0, 0, 0, 0.06);
      }
      .badge span {
        font-size: 12px;
        font-weight: 600;
      }

      /* Inline SVG wrapper */
      .svg-wrap {
        width: 18px;
        height: 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }
      .svg-wrap svg {
        width: 18px;
        height: 18px;
        display: block;
        /* If your SVG uses currentColor, it will inherit from here */
        fill: currentColor;
      }

      .clickable {
        cursor: pointer;
      }

      ha-icon {
        --mdc-icon-size: 22px;
      }
      .muted {
        opacity: 0.75;
      }
      .error {
        color: var(--error-color);
        padding: 12px 16px;
      }
    `;
  }

  setConfig(config) {
    if (!config || !config.device_id) throw new Error("device_id is required");

    this._deviceName = null;
    this._config = {
      title: config.title ?? "Device",
      device_id: config.device_id,

      // Optional regex to select the two sensors on the device
      primary_match: config.primary_match ?? null,
      secondary_match: config.secondary_match ?? null,

      // Which sensor’s attributes contain has_skating/has_classic/...:
      attributes_from: config.attributes_from ?? "numericValue", // "primary" | "secondary"

      // Color ranges based on PRIMARY sensor numeric value:
      // [{ min: 0, max: 10, color: "#00ff00" }, ...]
      color_ranges: Array.isArray(config.color_ranges) ? config.color_ranges : [],

      // Floodlight has no SVG; use an MDI icon
      floodlight_icon: config.floodlight_icon ?? "mdi:light-flood-down",

      // Optional: control whether SVG badges are tinted using the primary color
      tint_badges_with_primary_color: config.tint_badges_with_primary_color ?? false,
    };

    this._entityIds = null;
    this._error = null;
  }

  getCardSize() {
    return 2;
  }

  updated(changedProps) {
    if ((changedProps.has("hass") || changedProps.has("_config")) && this.hass && this._config?.device_id) {
      if (!this._entityIds) this._resolveEntitiesForDevice();
      if (!this._deviceName) this._resolveDeviceName();
    }
  }

  async _resolveDeviceName() {
    try {
      const devices = await this.hass.callWS({ type: "config/device_registry/list" });
      const dev = devices.find((d) => d.id === this._config.device_id);
  
      // Prefer a human-friendly field if present; otherwise fall back safely
      this._deviceName =
        dev?.name_by_user ||
        dev?.name ||
        dev?.model ||
        "Unknown device";
    } catch (err) {
      this._deviceName = "Unknown device";
    }
  }

  async _resolveEntitiesForDevice() {
    try {
      const entities = await this.hass.callWS({ type: "config/entity_registry/list" });
      const deviceEntities = entities
        .filter((e) => e.device_id === this._config.device_id)
        .map((e) => e.entity_id)
        .filter((eid) => typeof eid === "string" && eid.startsWith("sensor."))
        .sort();

      if (!deviceEntities.length) {
        this._error = `No sensor entities found for device_id=${this._config.device_id}`;
        this._entityIds = [];
        return;
      }

      const pickByRegex = (regexString) => {
        if (!regexString) return null;
        let re;
        try {
          re = new RegExp(regexString, "i");
        } catch {
          return null;
        }
        return deviceEntities.find((eid) => re.test(eid)) ?? null;
      };

      const primary = pickByRegex(this._config.primary_match) ?? deviceEntities[0] ?? null;
      const secondary =
        pickByRegex(this._config.secondary_match) ??
        deviceEntities.find((eid) => eid !== primary) ??
        null;

      this._entityIds = [primary, secondary].filter(Boolean);
      this._error = null;
    } catch (err) {
      this._error = `Failed to resolve entities via WebSocket: ${err?.message ?? err}`;
      this._entityIds = [];
    }
  }

  _numericState(entityId) {
    const st = this.hass?.states?.[entityId]?.state;
    if (st == null) return null;
    const n = Number(st);
    return Number.isFinite(n) ? n : null;
  }

  _formatState(entityId) {
    const s = this.hass?.states?.[entityId];
    if (!s) return "—";
    const unit = s.attributes?.unit_of_measurement ? ` ${s.attributes.unit_of_measurement}` : "";
    return `${s.state}${unit}`;
  }

  _colorForStatusValue(value) {
    if (value == null) return DEFAULT_STATUS_COLOR;
  
    const intVal = Number(value);
    if (!Number.isInteger(intVal)) return DEFAULT_STATUS_COLOR;
  
    return STATUS_COLORS[intVal] ?? DEFAULT_STATUS_COLOR;
  }


  _labelForStatusValue(value) {
    if (value == null) return DEFAULT_STATUS_LABEL;
  
    const intVal = Number(value);
    if (!Number.isInteger(intVal)) return DEFAULT_STATUS_LABEL;
  
    return STATUS_LABELS[intVal] ?? DEFAULT_STATUS_LABEL;
  }

  _colorForValue(value) {
    if (value == null) return "var(--secondary-text-color)";
    for (const r of this._config.color_ranges) {
      const min = r?.min ?? -Infinity;
      const max = r?.max ?? Infinity;
      if (value >= min && value <= max && r?.color) return r.color;
    }
    return "var(--secondary-text-color)";
  }

  _formatTimestamp(entityId) {
    const s = this.hass?.states?.[entityId]?.state;
    if (!s || s === "unknown" || s === "unavailable") return "—";
  
    const dt = new Date(s);
    if (Number.isNaN(dt.getTime())) {
      // If the sensor is already a friendly string, fall back to raw
      return s;
    }
  
    const locale =
      this.hass?.locale?.language
        ? `${this.hass.locale.language}${this.hass.locale.country ? "-" + this.hass.locale.country : ""}`
        : undefined;
  
    // Example output: "19. des. 2025, 13:45"
    return new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }).format(dt);
  }


  _attrBool(entityId, attr) {
    return this.hass?.states?.[entityId]?.attributes?.[attr] === true;
  }

  _renderInlineSvgBadge(label, svgKey, tintColor) {
    const svg = INLINE_SVGS[svgKey];
    if (!svg) return html``;

    // Note: this is “controlled” innerHTML from your own local file (no remote fetch),
    // which is acceptable for a bundled card. Keep SVGs trusted.
    return html`
      <span class="badge" title=${label} style=${tintColor ? `color:${tintColor}` : ""}>
        <span class="svg-wrap" .innerHTML=${svg}></span>
        <span>${label}</span>
      </span>
    `;
  }

  _formatRouteLength(entityId) {
    const meters = this.hass?.states?.[entityId]?.attributes?.route_length;
  
    if (meters == null) return null; // not present
    const m = Number(meters);
    if (!Number.isFinite(m) || m <= 0) return null;
  
    // If >= 1000 m, show km rounded sensibly; otherwise show meters.
    if (m >= 1000) {
      const km = m / 1000;
  
      // Rounding policy:
      // - < 10 km: 1 decimal (e.g., 3.4 km)
      // - >= 10 km: nearest whole km (e.g., 12 km)
      const rounded =
        km < 10 ? Math.round(km * 10) / 10 : Math.round(km);
  
      // Use Norwegian decimal comma if HA locale is nb-NO/nn-NO etc.
      const locale =
        this.hass?.locale?.language
          ? `${this.hass.locale.language}${this.hass.locale.country ? "-" + this.hass.locale.country : ""}`
          : undefined;
  
      const formatted = new Intl.NumberFormat(locale, {
        maximumFractionDigits: km < 10 ? 1 : 0,
        minimumFractionDigits: km < 10 && rounded % 1 !== 0 ? 1 : 0,
      }).format(rounded);
  
      return `${formatted} km`;
    }
  
    // < 1000 m: show meters rounded to nearest 10 m
    const roundedM = Math.round(m / 10) * 10;
    return `${roundedM} m`;
  }

  _entityIcon(entityId) {
    const s = this.hass?.states?.[entityId];
    // If the user set a custom icon, it will typically be in state attributes as "icon"
    return s?.attributes?.icon || "mdi:help-circle-outline";
  }

  _openMoreInfo(entityId) {
    if (!entityId) return;
    this.dispatchEvent(
      new CustomEvent("hass-more-info", {
        detail: { entityId },
        bubbles: true,
        composed: true,
      })
    );
  }

  render() {
    if (!this.hass || !this._config) return html``;
  
    if (this._error) {
      return html`<ha-card><div class="error">${this._error}</div></ha-card>`;
    }
  
    const entities = this._entityIds ?? [];
    if (!entities.length) {
      return html`<ha-card><div class="card muted">Resolving device sensors…</div></ha-card>`;
    }
  
    // Identify numeric vs datetime sensor by state parsability
    let numericEntity = null;
    let datetimeEntity = null;
  
    for (const eid of entities) {
      const state = this.hass?.states?.[eid]?.state;
      if (state == null) continue;
  
      const n = Number(state);
      if (Number.isFinite(n) && numericEntity === null) {
        numericEntity = eid;
      } else if (!Number.isFinite(n) && datetimeEntity === null) {
        datetimeEntity = eid;
      }
    }
  
    // Fallbacks if detection fails
    numericEntity ??= entities[0] ?? null;
    datetimeEntity ??= entities.find((e) => e !== numericEntity) ?? null;
  
    if (!numericEntity) {
      return html`<ha-card><div class="card muted">Resolving device sensors…</div></ha-card>`;
    }
  
    const numericValue = this._numericState(numericEntity);
    const primaryColor = this._colorForStatusValue(numericValue);
  
    // Attributes: from numeric sensor (recommended) unless configured to use datetime sensor
    const attrEntity =
      (this._config.attributes_from === "secondary" && datetimeEntity)
        ? datetimeEntity
        : numericEntity;
  
    const has_skating = this._attrBool(attrEntity, "has_skating");
    const has_classic = this._attrBool(attrEntity, "has_classic");
    const has_floodlight = this._attrBool(attrEntity, "has_floodlight");
    const is_scooter_trail = this._attrBool(attrEntity, "is_scooter_trail");
  
    const anyBadges = has_skating || has_classic || has_floodlight || is_scooter_trail;
    const tint = this._config.tint_badges_with_primary_color ? primaryColor : null;
  
    const icon = this._entityIcon(numericEntity);
  
    const timestampText = datetimeEntity ? this._formatTimestamp(datetimeEntity) : "—";
    const routeLenText = this._formatRouteLength(numericEntity) ?? "-";
  
    return html`
      <ha-card>
        <div class="card">
          <div class="row">
            <div class="left">
              <ha-icon
                icon=${icon}
                style="color:${primaryColor}"
                class="clickable"
                @click=${() => this._openMoreInfo(numericEntity)}
                title="More info"
              ></ha-icon>
  
              <div style="min-width:0">
                <div
                  class="title clickable"
                  role="button"
                  tabindex="0"
                  @click=${() => this._openMoreInfo(numericEntity)}
                  @keydown=${(e) => {
                    if (e.key === "Enter" || e.key === " ") this._openMoreInfo(numericEntity);
                  }}
                  title="More info"
                >
                  ${this._deviceName ?? "…"}
                </div>
  
                <div class="sub">
                  ${timestampText}
                </div>
              </div>
            </div>
  
            <div style="text-align:right">
              <div class="value">
                <span
                  class="clickable"
                  role="button"
                  tabindex="0"
                  style="color:${primaryColor}"
                  @click=${() => this._openMoreInfo(datetimeEntity || numericEntity)}
                  @keydown=${(e) => {
                    if (e.key === "Enter" || e.key === " ")
                      this._openMoreInfo(datetimeEntity || numericEntity);
                  }}
                  title="More info"
                >
                  ${this._labelForStatusValue(numericValue)}
                </span>
              </div>
  
              <div class="sub muted">${routeLenText}</div>
            </div>
          </div>
  
          ${anyBadges
            ? html`
                <div class="badges">
                  ${has_skating ? this._renderInlineSvgBadge("Skating", "has_skating", tint) : html``}
                  ${has_classic ? this._renderInlineSvgBadge("Classic", "has_classic", tint) : html``}
                  ${is_scooter_trail ? this._renderInlineSvgBadge("Scooter", "is_scooter_trail", tint) : html``}
  
                  ${has_floodlight
                    ? html`
                        <span class="badge" title="Floodlight">
                          <ha-icon icon=${this._config.floodlight_icon}></ha-icon>
                          <span>Floodlight</span>
                        </span>
                      `
                    : html``}
                </div>
              `
            : html``}
        </div>
      </ha-card>
    `;
  }
}

customElements.define(CARD_TAG, DeviceSensorsBadgesCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: CARD_TAG,
  name: "Sporet.no Card",
  description: "Shows colored status for Slopes from Sporet.no",
});

