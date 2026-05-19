/**
 * Euro Drive TCU - Dashboard UI & Theme Manager
 * Handles real-time SVG widget injection, alert colorization, and brand switching.
 */
class DashboardManager {
    constructor(configPath = '../assets/themeConfig.json') {
        this.configPath = configPath;
        this.themeData = null;
        this.activeTheme = null;
        this.registeredIcons = new Map();
    }

    /**
     * Initializes the theme engine, fetches configurations, and registers dashboard icons.
     */
    async initialize() {
        try {
            const response = await fetch(this.configPath);
            if (!response.ok) throw new Error(`Failed to fetch config at ${this.configPath}`);
            
            this.themeData = await response.json();
            this.setTheme(this.themeData.activeTheme);
            this.injectKeyframeAnimations();
            
            console.log(`[TCU Dashboard Engine] Initialized brand profiles successfully.`);
        } catch (error) {
            console.error(`[TCU Dashboard Engine] Initialization crash:`, error);
        }
    }

    /**
     * Sets the global brand UI theme layout (audi_sport_virtual, vw_r_performance, porsche_motorsport)
     * @param {string} themeKey 
     */
    setTheme(themeKey) {
        if (!this.themeData.themes[themeKey]) {
            console.warn(`Theme '${themeKey}' not found in configuration profile. Falling back.`);
            return;
        }
        this.activeTheme = this.themeData.themes[themeKey];
        document.body.style.backgroundColor = this.activeTheme.globalBackground;
        document.body.style.fontFamily = this.activeTheme.fontFamily;
        
        // Refresh all active visual markers to apply new style sheets instantly
        this.refreshAllActiveIndicators();
    }

    /**
     * Generates and appends CSS animation keyframes to document head dynamically
     */
    injectKeyframeAnimations() {
        let styleSheet = document.getElementById('tcu-dynamic-animations');
        if (!styleSheet) {
            styleSheet = document.createElement("style");
            styleSheet.id = "tcu-dynamic-animations";
            document.head.appendChild(styleSheet);
        }

        let cssRules = "";
        for (const [name, profile] of Object.entries(this.themeData.animations)) {
            cssRules += `
                @keyframes ${name} { ${profile.keyframes} }
                .${name}-active {
                    animation-name: ${name};
                    animation-duration: ${profile.duration};
                    animation-iteration-count: ${profile.iteration};
                }
            `;
        }
        styleSheet.textContent = cssRules;
    }

    /**
     * Registers an SVG target indicator element inside the virtual memory pool
     * @param {string} elementId - DOM selector ID
     * @param {string} telemetryChannel - Key inside real-time metrics feed mapping to this light
     */
    registerIndicator(elementId, telemetryChannel) {
        const domElement = document.getElementById(elementId);
        if (domElement) {
            this.registeredIcons.set(telemetryChannel, domElement);
            this.applyStateStyle(domElement, 'dimmed'); // Initialize visually off/dark
        }
    }

    /**
     * Takes incoming real-time telemetry frame and applies updates safely across registered widgets
     * @param {Object} telemetryFrame 
     */
    parseTelemetry(telemetryFrame) {
        for (const [channel, value] of Object.entries(telemetryFrame)) {
            if (this.registeredIcons.has(channel)) {
                const targetSvg = this.registeredIcons.get(channel);
                let targetedState = 'dimmed';

                // Core logic mapping rules matching standard car telemetry
                if (typeof value === 'boolean') {
                    targetedState = value ? 'ok' : 'dimmed';
                } else if (typeof value === 'string') {
                    // Accepts direct telemetry status states ('ok', 'warning', 'critical', 'info')
                    targetedState = ['ok', 'warning', 'critical', 'info', 'dimmed'].includes(value) ? value : 'dimmed';
                }
                
                this.applyStateStyle(targetSvg, targetedState);
            }
        }
    }

    /**
     * Helper to manipulate specific vector graphic node colors and effects
     */
    applyStateStyle(element, stateKey) {
        if (!this.activeTheme) return;
        const stateConfig = this.activeTheme.states[stateKey];

        // Apply raw color properties to path fill & outer glows
        element.style.color = stateConfig.hex;
        element.style.filter = stateConfig.glow;
        element.style.transition = "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)";

        // Wipe out past telemetry animation classes cleanly
        element.className.baseVal = ""; 
        
        if (stateConfig.animation !== "none") {
            element.classList.add(`${stateConfig.animation}-active`);
        }
    }

    /**
     * Iterates through memory map elements updating styles globally when brand profiles swap live
     */
    refreshAllActiveIndicators() {
        this.registeredIcons.forEach((element) => {
            // Evaluates current active style profile to re-render appropriate color depths
            if (element.classList.contains('pulse_fast-active')) this.applyStateStyle(element, 'critical');
            else if (element.classList.contains('strobe-active')) this.applyStateStyle(element, 'critical');
            else if (element.classList.contains('solid_flash-active')) this.applyStateStyle(element, 'critical');
            else if (element.style.filter !== "none" && element.style.filter !== "") {
                // Approximate mapping rules for static indicator translations
                if (element.style.color === "#ffd60a" || element.style.color === "#ffaa00" || element.style.color === "#ff6600") this.applyStateStyle(element, 'warning');
                else if (element.style.color === "#30d158" || element.style.color === "#00f0ff" || element.style.color === "#ffffff") this.applyStateStyle(element, 'ok');
                else if (element.style.color === "#0a84ff" || element.style.color === "#0055ff" || element.style.color === "#00ffaa") this.applyStateStyle(element, 'info');
            } else {
                this.applyStateStyle(element, 'dimmed');
            }
        });
    }
}

// Export for module architectures or keep context-global
export default DashboardManager;
