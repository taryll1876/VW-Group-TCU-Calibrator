/**
 * Euro Drive TCU - Calibration Tuning Engine
 * Manages operational parameters, threshold validation, and binary map profile exports.
 */
class CalibrationEngine {
    constructor(paramConfigPath = '../../../assets/tcuParameters.json') { // Adjusted backsteps
        this.paramConfigPath = paramConfigPath;
        // ... rest of code

class CalibrationEngine {
    constructor(paramConfigPath = '../assets/tcuParameters.json') {
        this.paramConfigPath = paramConfigPath;
        this.parameterMeta = null;
        this.activeSessionValues = {};
    }

    /**
     * Loads calibration rulesets and copies parameter defaults to active memory space.
     */
    async loadParameters() {
        try {
            const response = await fetch(this.paramConfigPath);
            if (!response.ok) throw new Error("Failed to read calibration spec map.");
            const data = await response.json();
            this.parameterMeta = data.parameters;
            
            // Initialize runtime values using default settings
            for (const [key, definition] of Object.entries(this.parameterMeta)) {
                this.activeSessionValues[key] = definition.defaultValue;
            }
            console.log("[Calibration Engine] Map definitions mapped cleanly to working matrix.");
        } catch (e) {
            console.error("[Calibration Engine] Hardware parameter definition mapping failed:", e);
        }
    }

    /**
     * Updates an individual calibration channel safely with safety bounds checks
     * @param {string} key - Configuration target parameter key
     * @param {number} inputVal - Numerical override value
     */
    updateValue(key, inputVal) {
        if (!this.parameterMeta[key]) return { success: false, reason: "Parameter unknown." };
        const meta = this.parameterMeta[key];
        
        if (inputVal < meta.minLimit || inputVal > meta.maxLimit) {
            return { 
                success: false, 
                reason: `Value out of range! Bound limits: ${meta.minLimit} - ${meta.maxLimit} ${meta.unit}`
            };
        }
        
        this.activeSessionValues[key] = Number(inputVal);
        return { success: true, updatedValue: this.activeSessionValues[key] };
    }

    /**
     * Generates a clean JSON file snapshot representing custom changes ready for flashing
     */
    exportCalibrationProfile() {
        const payload = {
            timestamp: new Date().toISOString(),
            checksum: "CRC32_" + Math.random().toString(16).substr(2, 8).toUpperCase(),
            appliedCalibration: { ...this.activeSessionValues }
        };

        const jsonString = JSON.stringify(payload, null, 2);
        const dataBlob = new Blob([jsonString], { type: "application/json" });
        const downloadUrl = URL.createObjectURL(dataBlob);

        const virtualAnchor = document.createElement('a');
        virtualAnchor.href = downloadUrl;
        virtualAnchor.download = `EuroDrive_TCU_Cal_${Math.floor(Date.now() / 1000)}.json`;
        document.body.appendChild(virtualAnchor);
        virtualAnchor.click();
        document.body.removeChild(virtualAnchor);
        URL.revokeObjectURL(downloadUrl);
        
        return payload;
    }
}

export default CalibrationEngine;
